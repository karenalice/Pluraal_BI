from Backend.database.connection import get_db_cursor

def list_all_links():
    with get_db_cursor(commit=False) as cur:
        cur.execute("""
            SELECT id_link, nome, link, descricao, ativo, criado_em
            FROM powerbi_link
            ORDER BY nome ASC
        """)
        links = cur.fetchall()
        for l in links:
            if l.get("criado_em"):
                l["criado_em"] = l["criado_em"].isoformat()
        return links

def get_user_links(user_id: int):
    with get_db_cursor(commit=False) as cur:
        # Check user
        cur.execute("SELECT id_usuario, hierarquia, pode_criar_usuario, pode_criar_link FROM usuario WHERE id_usuario = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            return []

        # If user is Master, they have access to all active links!
        if user["hierarquia"] == "Master":
            cur.execute("""
                SELECT id_link, nome, link, descricao, ativo
                FROM powerbi_link
                WHERE ativo = true
                ORDER BY nome ASC
            """)
            return cur.fetchall()

        # Regular user or Admin: get assigned links
        cur.execute("""
            SELECT l.id_link, l.nome, l.link, l.descricao, l.ativo
            FROM usuario_powerbi up
            JOIN powerbi_link l ON up.id_link = l.id_link
            WHERE up.id_usuario = %s AND l.ativo = true
            ORDER BY l.nome ASC
        """, (user_id,))
        return cur.fetchall()

def create_link(creator_id: int, data: dict):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id_usuario, hierarquia, pode_criar_link FROM usuario WHERE id_usuario = %s", (creator_id,))
        user = cur.fetchone()
        if not user:
            raise ValueError("Usuário não encontrado.")

        # Regra: Apenas Master e Administrador podem adicionar links do Power BI
        if user["hierarquia"] not in ("Master", "Administrador"):
            raise PermissionError("Apenas os perfis Master e Administrador têm permissão para adicionar links do Power BI.")

        nome = data.get("nome", "").strip()
        link = data.get("link", "").strip()
        descricao = data.get("descricao", "").strip() or None

        if not nome or not link:
            raise ValueError("Nome do dashboard e link do Power BI são obrigatórios.")

        cur.execute("""
            INSERT INTO powerbi_link (nome, link, descricao, ativo, criado_por_usuario_id)
            VALUES (%s, %s, %s, true, %s)
        """, (nome, link, descricao, creator_id))

        cur.execute("SELECT id_link, nome, link, descricao, ativo, criado_em FROM powerbi_link WHERE nome = %s ORDER BY id_link DESC LIMIT 1", (nome,))
        created = cur.fetchone()
        if created.get("criado_em"):
            created["criado_em"] = created["criado_em"].isoformat()
        return created

def update_link(updater_id: int, link_id: int, data: dict):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id_usuario, hierarquia, pode_criar_link FROM usuario WHERE id_usuario = %s", (updater_id,))
        user = cur.fetchone()
        if not user:
            raise ValueError("Usuário não encontrado.")

        if user["hierarquia"] not in ("Master", "Administrador"):
            raise PermissionError("Apenas os perfis Master e Administrador têm permissão para editar links do Power BI.")

        nome = data.get("nome", "").strip()
        link = data.get("link", "").strip()
        descricao = data.get("descricao", "").strip() or None
        ativo = bool(data.get("ativo", True))

        if not nome or not link:
            raise ValueError("Nome e link são obrigatórios.")

        cur.execute("""
            UPDATE powerbi_link
            SET nome = %s, link = %s, descricao = %s, ativo = %s
            WHERE id_link = %s
        """, (nome, link, descricao, ativo, link_id))

        cur.execute("SELECT id_link, nome, link, descricao, ativo, criado_em FROM powerbi_link WHERE id_link = %s", (link_id,))
        updated = cur.fetchone()
        if updated.get("criado_em"):
            updated["criado_em"] = updated["criado_em"].isoformat()
        return updated

def delete_link(requester_id: int, link_id: int):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id_usuario, hierarquia, pode_criar_link FROM usuario WHERE id_usuario = %s", (requester_id,))
        user = cur.fetchone()
        if not user:
            raise ValueError("Usuário não encontrado.")

        if user["hierarquia"] not in ("Master", "Administrador"):
            raise PermissionError("Apenas os perfis Master e Administrador têm permissão para excluir links do Power BI.")

        cur.execute("DELETE FROM usuario_powerbi WHERE id_link = %s", (link_id,))
        cur.execute("DELETE FROM powerbi_link WHERE id_link = %s", (link_id,))
        return {"message": "Link removido com sucesso."}
