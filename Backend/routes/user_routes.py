from flask import Blueprint, request, jsonify, g
from Backend.services.user_service import (
    list_users,
    get_user_by_id,
    create_user,
    update_user,
    reset_user_password
)
from Backend.middleware.auth_middleware import login_required

user_bp = Blueprint("users", __name__, url_prefix="/api/users")

@user_bp.route("", methods=["GET"])
@login_required()
def get_users():
    try:
        users = list_users(g.current_user["id_usuario"])
        return jsonify(users), 200
    except PermissionError as e:
        return jsonify({"error": "FORBIDDEN", "message": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "SERVER_ERROR", "message": str(e)}), 500

@user_bp.route("/<int:user_id>", methods=["GET"])
@login_required()
def get_single_user(user_id):
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "NOT_FOUND", "message": "Usuário não encontrado."}), 404
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": "SERVER_ERROR", "message": str(e)}), 500

@user_bp.route("", methods=["POST"])
@login_required()
def handle_create_user():
    data = request.get_json(silent=True) or {}
    try:
        creator_id = g.current_user["id_usuario"]
        new_user = create_user(creator_id, data)
        return jsonify({
            "message": "Usuário cadastrado com sucesso!",
            "user": new_user
        }), 201
    except PermissionError as e:
        return jsonify({"error": "PERMISSION_DENIED", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": "VALIDATION_ERROR", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "SERVER_ERROR", "message": f"Erro ao criar usuário: {str(e)}"}), 500

@user_bp.route("/<int:user_id>", methods=["PUT"])
@login_required()
def handle_update_user(user_id):
    data = request.get_json(silent=True) or {}
    try:
        updater_id = g.current_user["id_usuario"]
        updated_user = update_user(updater_id, user_id, data)
        return jsonify({
            "message": "Usuário atualizado com sucesso!",
            "user": updated_user
        }), 200
    except PermissionError as e:
        return jsonify({"error": "PERMISSION_DENIED", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": "VALIDATION_ERROR", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "SERVER_ERROR", "message": f"Erro ao atualizar usuário: {str(e)}"}), 500

@user_bp.route("/<int:user_id>/reset-password", methods=["POST"])
@login_required()
def handle_reset_password(user_id):
    try:
        requester_id = g.current_user["id_usuario"]
        res = reset_user_password(requester_id, user_id)
        return jsonify({
            "message": "Senha temporária gerada com sucesso!",
            "senha_temporaria": res["senha_temporaria"]
        }), 200
    except PermissionError as e:
        return jsonify({"error": "PERMISSION_DENIED", "message": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "SERVER_ERROR", "message": f"Erro ao redefinir senha: {str(e)}"}), 500
