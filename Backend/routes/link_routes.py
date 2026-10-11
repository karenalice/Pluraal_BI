from flask import Blueprint, request, jsonify, g
from Backend.services.link_service import (
    list_all_links,
    get_user_links,
    create_link,
    update_link,
    delete_link
)
from Backend.middleware.auth_middleware import login_required

link_bp = Blueprint("links", __name__, url_prefix="/api/links")

@link_bp.route("", methods=["GET"])
@login_required()
def get_links():
    try:
        user = g.current_user
        # If user has permissions to assign or create links, return all available links
        if user["hierarquia"] == "Master" or user.get("pode_criar_usuario") or user.get("pode_criar_link"):
            links = list_all_links()
        else:
            links = get_user_links(user["id_usuario"])
        return jsonify(links), 200
    except Exception as e:
        return jsonify({"error": "SERVER_ERROR", "message": str(e)}), 500

@link_bp.route("/my-links", methods=["GET"])
@login_required()
def get_my_links():
    try:
        links = get_user_links(g.current_user["id_usuario"])
        return jsonify(links), 200
    except Exception as e:
        return jsonify({"error": "SERVER_ERROR", "message": str(e)}), 500

@link_bp.route("", methods=["POST"])
@login_required()
def handle_create_link():
    data = request.get_json(silent=True) or {}
    try:
        creator_id = g.current_user["id_usuario"]
        new_link = create_link(creator_id, data)
        return jsonify({
            "message": "Link cadastrado com sucesso!",
            "link": new_link
        }), 201
    except PermissionError as e:
        return jsonify({"error": "PERMISSION_DENIED", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": "VALIDATION_ERROR", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "SERVER_ERROR", "message": f"Erro ao criar link: {str(e)}"}), 500

@link_bp.route("/<int:link_id>", methods=["PUT"])
@login_required()
def handle_update_link(link_id):
    data = request.get_json(silent=True) or {}
    try:
        updater_id = g.current_user["id_usuario"]
        updated = update_link(updater_id, link_id, data)
        return jsonify({
            "message": "Link atualizado com sucesso!",
            "link": updated
        }), 200
    except PermissionError as e:
        return jsonify({"error": "PERMISSION_DENIED", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": "VALIDATION_ERROR", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "SERVER_ERROR", "message": f"Erro ao atualizar link: {str(e)}"}), 500

@link_bp.route("/<int:link_id>", methods=["DELETE"])
@login_required()
def handle_delete_link(link_id):
    try:
        requester_id = g.current_user["id_usuario"]
        res = delete_link(requester_id, link_id)
        return jsonify(res), 200
    except PermissionError as e:
        return jsonify({"error": "PERMISSION_DENIED", "message": str(e)}), 403
    except Exception as e:
        return jsonify({"error": "SERVER_ERROR", "message": f"Erro ao excluir link: {str(e)}"}), 500
