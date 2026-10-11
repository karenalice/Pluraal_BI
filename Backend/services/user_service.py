from datetime import date
from Backend.config.settings import settings
from Backend.database.connection import get_db_cursor
from Backend.services.security_service import (
    hash_password,
    generate_temporary_password
)

def get_user_by_email(email: str):
    with get_db_cursor(commit=False) as cur:
        cur.execute("""
            SELECT id_usuario, nome_completo_usuario, email, senha, hierarquia,
                   ativo, trocar_senha_no_primeiro_acesso, pode_criar_usuario, pode_criar_link,
                   pode_simular_visao, limite_criacao_usuarios,
                   criado_por_usuario_id, criado_em, token_versao, foto_perfil,
                   data_expiracao_login,
                   (data_expiracao_login IS NOT NULL AND data_expiracao_login < CURRENT_DATE) AS login_expirado
            FROM usuario
            WHERE LOWER(email) = LOWER(%s)
        """, (email.strip(),))
        return cur.fetchone()

def get_user_by_id(user_id: int):
    with get_db_cursor(commit=False) as cur:
        cur.execute("""
            SELECT id_usuario, nome_completo_usuario, email, hierarquia,
                   ativo, trocar_senha_no_primeiro_acesso, pode_criar_usuario, pode_criar_link,
                   pode_simular_visao, limite_criacao_usuarios,
                   criado_por_usuario_id, criado_em, token_versao, foto_perfil,
                   data_expiracao_login
            FROM usuario
            WHERE id_usuario = %s
        """, (user_id,))
        user = cur.fetchone()
        if not user:
            return None
        if user.get("data_expiracao_login"):
            user["data_expiracao_login"] = user["data_expiracao_login"].isoformat()

        # Load user assigned Power BI links
        cur.execute("""
            SELECT l.id_link, l.nome, l.link, l.descricao, l.ativo
            FROM usuario_powerbi up
            JOIN powerbi_link l ON up.id_link = l.id_link
            WHERE up.id_usuario = %s AND l.ativo = true
            ORDER BY l.nome ASC
        """, (user_id,))
        user["links_bi"] = cur.fetchall()

        # Load organizational accesses if any
        col_escola = "ep.ESCOLA" if settings.DB_ENGINE == "mysql" else 'ep."ESCOLA"'
        col_uniao = "ep.UNIAO" if settings.DB_ENGINE == "mysql" else 'ep."UNIAO"'
        col_assoc = "ep.ASSOCIACAO" if settings.DB_ENGINE == "mysql" else 'ep."ASSOCIACAO"'

        cur.execute(f"""
            SELECT ua.id_acesso, ua.tipo, ua.sigla_uniao, ua.sigla_associacao, ua.id_escolas,
                   {col_escola} as nome_escola, {col_uniao} as nome_uniao, {col_assoc} as nome_associacao
            FROM usuario_acesso ua
            LEFT JOIN escolas_pluraal ep ON ua.id_escolas = ep.id_escolas
            WHERE ua.id_usuario = %s
            ORDER BY ua.tipo, ua.sigla_uniao, ua.sigla_associacao
        """, (user_id,))
        user["acessos"] = cur.fetchall()

        return user

def list_users(requester_id: int):
    with get_db_cursor(commit=False) as cur:
        cur.execute("""
            SELECT id_usuario, hierarquia, pode_criar_usuario, pode_criar_link
            FROM usuario
            WHERE id_usuario = %s
        """, (requester_id,))
        requester = cur.fetchone()
        if not requester:
            raise ValueError("Usuário solicitante não encontrado.")

        is_master = requester["hierarquia"] == "Master"
        can_create = requester["pode_criar_usuario"]

        if not is_master and not can_create:
            raise PermissionError("Você não tem permissão para gerenciar usuários.")

        if is_master:
            cur.execute("""
                SELECT u.id_usuario, u.nome_completo_usuario, u.email, u.hierarquia,
                       u.ativo, u.trocar_senha_no_primeiro_acesso, u.pode_criar_usuario, u.pode_criar_link,
                       u.criado_por_usuario_id, u.criado_em, u.data_expiracao_login,
                       creator.nome_completo_usuario as criado_por_nome
                FROM usuario u
                LEFT JOIN usuario creator ON u.criado_por_usuario_id = creator.id_usuario
                ORDER BY u.id_usuario ASC
            """)
        else:
            cur.execute("""
                SELECT u.id_usuario, u.nome_completo_usuario, u.email, u.hierarquia,
                       u.ativo, u.trocar_senha_no_primeiro_acesso, u.pode_criar_usuario, u.pode_criar_link,
                       u.criado_por_usuario_id, u.criado_em, u.data_expiracao_login,
                       creator.nome_completo_usuario as criado_por_nome
                FROM usuario u
                LEFT JOIN usuario creator ON u.criado_por_usuario_id = creator.id_usuario
                WHERE u.criado_por_usuario_id = %s OR u.id_usuario = %s
                ORDER BY u.id_usuario ASC
            """, (requester_id, requester_id))

        users = cur.fetchall()

        # Fetch assigned links for each user
        for u in users:
            if u.get("data_expiracao_login"):
                u["data_expiracao_login"] = u["data_expiracao_login"].isoformat()
            if u.get("criado_em"):
                u["criado_em"] = u["criado_em"].isoformat()

            cur.execute("""
                SELECT l.id_link, l.nome
                FROM usuario_powerbi up
                JOIN powerbi_link l ON up.id_link = l.id_link
                WHERE up.id_usuario = %s
                ORDER BY l.nome ASC
            """, (u["id_usuario"],))
            u["links_bi"] = cur.fetchall()

        return users

def create_user(creator_id: int, user_data: dict):
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            SELECT id_usuario, hierarquia, pode_criar_usuario, pode_criar_link
            FROM usuario WHERE id_usuario = %s
        """, (creator_id,))
        creator = cur.fetchone()
        if not creator:
            raise ValueError("Criador não encontrado.")

        is_master = (creator["hierarquia"] == "Master")
        if not is_master and not creator["pode_criar_usuario"]:
            raise PermissionError("Você não tem autorização para criar usuários.")

        nome = user_data.get("nome_completo_usuario", "").strip()
        email = user_data.get("email", "").strip()
        hierarquia = user_data.get("hierarquia", "escola").strip()
        ativo = bool(user_data.get("ativo", True))
        data_expiracao = user_data.get("data_expiracao_login") or None

        if not nome or not email:
            raise ValueError("Nome completo e e-mail são obrigatórios.")

        cur.execute("SELECT id_usuario FROM usuario WHERE LOWER(email) = LOWER(%s)", (email,))
        if cur.fetchone():
            raise ValueError(f"O e-mail '{email}' já está cadastrado no sistema.")

        # Permissions: only Master can authorize pode_criar_usuario and pode_criar_link
        # and only Administrador can receive pode_criar_link
        pode_criar_usuario = False
        pode_criar_link = False

        if is_master:
            pode_criar_usuario = bool(user_data.get("pode_criar_usuario", False))
            # "o unico que pode receber autorização para criar link é o administrador"
            if hierarquia in ("Master", "Administrador"):
                pode_criar_link = bool(user_data.get("pode_criar_link", False))
        else:
            # Non-masters cannot grant creation rights
            pode_criar_usuario = False
            pode_criar_link = False

        temp_password = generate_temporary_password(10)
        pass_hash = hash_password(temp_password)

        cur.execute("""
            INSERT INTO usuario (
                nome_completo_usuario, email, senha, hierarquia, ativo,
                trocar_senha_no_primeiro_acesso, pode_criar_usuario, pode_criar_link,
                criado_por_usuario_id, data_expiracao_login
            ) VALUES (%s, %s, %s, %s, %s, true, %s, %s, %s, %s)
        """, (
            nome, email, pass_hash, hierarquia, ativo,
            pode_criar_usuario, pode_criar_link, creator_id, data_expiracao
        ))

        # Get generated user id (works across Postgres and MySQL)
        cur.execute("SELECT id_usuario FROM usuario WHERE LOWER(email) = LOWER(%s)", (email,))
        new_user_id = cur.fetchone()["id_usuario"]

        # Assign Power BI links
        links_ids = user_data.get("links_ids", [])
        for lid in links_ids:
            cur.execute("""
                INSERT INTO usuario_powerbi (id_usuario, id_link, atribuido_por_usuario_id)
                VALUES (%s, %s, %s)
            """, (new_user_id, lid, creator_id))

        return {
            "id_usuario": new_user_id,
            "nome_completo_usuario": nome,
            "email": email,
            "hierarquia": hierarquia,
            "senha_temporaria": temp_password,
            "pode_criar_usuario": pode_criar_usuario,
            "pode_criar_link": pode_criar_link
        }

def update_user(updater_id: int, user_id: int, user_data: dict):
    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            SELECT id_usuario, hierarquia, pode_criar_usuario FROM usuario WHERE id_usuario = %s
        """, (updater_id,))
        updater = cur.fetchone()
        if not updater:
            raise ValueError("Usuário solicitante não encontrado.")

        cur.execute("SELECT * FROM usuario WHERE id_usuario = %s", (user_id,))
        target = cur.fetchone()
        if not target:
            raise ValueError("Usuário a ser editado não encontrado.")

        is_master = (updater["hierarquia"] == "Master")
        if not is_master and target["criado_por_usuario_id"] != updater_id:
            raise PermissionError("Você só pode atualizar usuários criados por você.")

        nome = user_data.get("nome_completo_usuario", target["nome_completo_usuario"]).strip()
        email = user_data.get("email", target["email"]).strip()
        hierarquia = user_data.get("hierarquia", target["hierarquia"]).strip()
        ativo = bool(user_data.get("ativo", target["ativo"]))
        data_expiracao = user_data.get("data_expiracao_login") or None

        # Check email uniqueness
        cur.execute("SELECT id_usuario FROM usuario WHERE LOWER(email) = LOWER(%s) AND id_usuario != %s", (email, user_id))
        if cur.fetchone():
            raise ValueError(f"O e-mail '{email}' já está em uso por outro usuário.")

        pode_criar_usuario = target["pode_criar_usuario"]
        pode_criar_link = target["pode_criar_link"]

        if is_master:
            pode_criar_usuario = bool(user_data.get("pode_criar_usuario", pode_criar_usuario))
            if hierarquia in ("Master", "Administrador"):
                pode_criar_link = bool(user_data.get("pode_criar_link", pode_criar_link))
            else:
                pode_criar_link = False

        cur.execute("""
            UPDATE usuario
            SET nome_completo_usuario = %s,
                email = %s,
                hierarquia = %s,
                ativo = %s,
                pode_criar_usuario = %s,
                pode_criar_link = %s,
                data_expiracao_login = %s
            WHERE id_usuario = %s
        """, (nome, email, hierarquia, ativo, pode_criar_usuario, pode_criar_link, data_expiracao, user_id))

        # Update assigned links if provided
        if "links_ids" in user_data:
            cur.execute("DELETE FROM usuario_powerbi WHERE id_usuario = %s", (user_id,))
            for lid in user_data["links_ids"]:
                cur.execute("""
                    INSERT INTO usuario_powerbi (id_usuario, id_link, atribuido_por_usuario_id)
                    VALUES (%s, %s, %s)
                """, (user_id, lid, updater_id))

        return get_user_by_id(user_id)

def reset_user_password(requester_id: int, user_id: int):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id_usuario, hierarquia, pode_criar_usuario FROM usuario WHERE id_usuario = %s", (requester_id,))
        requester = cur.fetchone()
        if not requester:
            raise ValueError("Usuário solicitante não encontrado.")

        cur.execute("SELECT id_usuario, criado_por_usuario_id, token_versao FROM usuario WHERE id_usuario = %s", (user_id,))
        target = cur.fetchone()
        if not target:
            raise ValueError("Usuário não encontrado.")

        is_master = (requester["hierarquia"] == "Master")
        if not is_master and target["criado_por_usuario_id"] != requester_id:
            raise PermissionError("Você só pode redefinir senhas de usuários criados por você.")

        temp_pwd = generate_temporary_password(10)
        h = hash_password(temp_pwd)
        new_token_versao = target["token_versao"] + 1

        cur.execute("""
            UPDATE usuario
            SET senha = %s,
                trocar_senha_no_primeiro_acesso = true,
                token_versao = %s
            WHERE id_usuario = %s
        """, (h, new_token_versao, user_id))

        return {"senha_temporaria": temp_pwd}
