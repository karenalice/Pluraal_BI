import re
from Backend.database.connection import get_db_cursor
from Backend.services.security_service import (
    hash_password,
    verify_password,
    create_access_token
)
from Backend.services.user_service import get_user_by_email, get_user_by_id

def authenticate_user(email: str, plain_senha: str):
    user = get_user_by_email(email)
    if not user:
        raise ValueError("Credenciais inválidas. Verifique seu e-mail e senha.")

    if not user.get("ativo"):
        raise PermissionError("Usuário inativo. Entre em contato com o administrador.")

    if user.get("login_expirado"):
        raise PermissionError("O prazo de acesso deste usuário terminou. Entre em contato com a administração.")

    if not verify_password(plain_senha, user["senha"]):
        raise ValueError("Credenciais inválidas. Verifique seu e-mail e senha.")

    token_payload = {
        "id_usuario": user["id_usuario"],
        "email": user["email"],
        "nome_completo_usuario": user["nome_completo_usuario"],
        "hierarquia": user["hierarquia"],
        "trocar_senha_no_primeiro_acesso": user["trocar_senha_no_primeiro_acesso"],
        "pode_criar_usuario": user.get("pode_criar_usuario", False),
        "pode_criar_link": user.get("pode_criar_link", False),
        "token_versao": user.get("token_versao", 1)
    }
    token = create_access_token(token_payload)
    full_user = get_user_by_id(user["id_usuario"])

    return {
        "token": token,
        "usuario": full_user
    }

def validate_password_strength(password: str):
    if len(password) < 8:
        return False, "A nova senha deve ter no mínimo 8 caracteres."
    if not re.search(r"[A-Za-z]", password):
        return False, "A nova senha deve conter pelo menos uma letra."
    if not re.search(r"[0-9]", password):
        return False, "A nova senha deve conter pelo menos um número."
    return True, ""

def change_user_password(user_id: int, senha_atual: str, nova_senha: str, confirmacao_senha: str):
    if not nova_senha or not confirmacao_senha:
        raise ValueError("Nova senha e confirmação de senha são obrigatórias.")

    if nova_senha != confirmacao_senha:
        raise ValueError("A nova senha e a confirmação não coincidem.")

    if senha_atual == nova_senha:
        raise ValueError("A nova senha deve ser diferente da senha temporária atual.")

    is_strong, err_msg = validate_password_strength(nova_senha)
    if not is_strong:
        raise ValueError(err_msg)

    with get_db_cursor(commit=True) as cur:
        cur.execute("""
            SELECT id_usuario, email, nome_completo_usuario, hierarquia, senha,
                   trocar_senha_no_primeiro_acesso, pode_criar_usuario, pode_criar_link, token_versao
            FROM usuario
            WHERE id_usuario = %s
        """, (user_id,))
        user = cur.fetchone()
        if not user:
            raise ValueError("Usuário não encontrado.")

        if not verify_password(senha_atual, user["senha"]):
            raise ValueError("A senha atual informada está incorreta.")

        new_hash = hash_password(nova_senha)
        new_token_versao = user["token_versao"] + 1

        cur.execute("""
            UPDATE usuario
            SET senha = %s,
                trocar_senha_no_primeiro_acesso = false,
                token_versao = %s
            WHERE id_usuario = %s
        """, (new_hash, new_token_versao, user_id))

        new_token_payload = {
            "id_usuario": user["id_usuario"],
            "email": user["email"],
            "nome_completo_usuario": user["nome_completo_usuario"],
            "hierarquia": user["hierarquia"],
            "trocar_senha_no_primeiro_acesso": False,
            "pode_criar_usuario": user["pode_criar_usuario"],
            "pode_criar_link": user["pode_criar_link"],
            "token_versao": new_token_versao
        }
        refreshed_token = create_access_token(new_token_payload)
        refreshed_user = get_user_by_id(user_id)

        return {
            "token": refreshed_token,
            "usuario": refreshed_user
        }
