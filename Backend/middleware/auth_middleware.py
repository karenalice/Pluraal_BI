from functools import wraps
from flask import request, jsonify, g
from Backend.services.security_service import decode_access_token
from Backend.database.connection import get_db_cursor

def get_current_token_payload():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "Cabeçalho de autorização ausente ou em formato inválido."
    token = auth_header.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token)
        return payload, None
    except ValueError as e:
        return None, str(e)

def login_required(allow_pending_password_change=False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            payload, err = get_current_token_payload()
            if err:
                return jsonify({"error": "UNAUTHORIZED", "message": err}), 401

            user_id = payload.get("id_usuario")
            token_versao = payload.get("token_versao", 1)

            with get_db_cursor(commit=False) as cur:
                cur.execute("""
                    SELECT id_usuario, nome_completo_usuario, email, hierarquia,
                           ativo, trocar_senha_no_primeiro_acesso, pode_criar_usuario, pode_criar_link,
                           criado_por_usuario_id, token_versao, data_expiracao_login,
                           (data_expiracao_login IS NOT NULL AND data_expiracao_login < CURRENT_DATE) AS login_expirado
                    FROM usuario
                    WHERE id_usuario = %s
                """, (user_id,))
                user = cur.fetchone()

            if not user:
                return jsonify({"error": "USER_NOT_FOUND", "message": "Usuário não encontrado."}), 401

            if not user["ativo"]:
                return jsonify({"error": "USER_INACTIVE", "message": "Usuário desativado. Entre em contato com a administração."}), 403

            if user.get("login_expirado"):
                return jsonify({"error": "LOGIN_EXPIRED", "message": "O prazo de acesso deste usuário terminou."}), 401

            if user["token_versao"] != token_versao:
                return jsonify({
                    "error": "SESSION_REVOKED",
                    "message": "Sessão invalidada por redefinição de senha. Realize login novamente."
                }), 401

            if user["trocar_senha_no_primeiro_acesso"] and not allow_pending_password_change:
                return jsonify({
                    "error": "FORCE_PASSWORD_CHANGE",
                    "message": "Definição de nova senha obrigatória antes de continuar."
                }), 403

            g.current_user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator
