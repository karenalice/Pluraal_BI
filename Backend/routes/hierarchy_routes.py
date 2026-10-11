from flask import Blueprint, jsonify, g
from Backend.middleware.auth_middleware import login_required

hierarchy_bp = Blueprint("hierarchy", __name__, url_prefix="/api/hierarchy")

@hierarchy_bp.route("/capabilities", methods=["GET"])
@login_required()
def get_capabilities():
    user = g.current_user
    h = user["hierarquia"]
    is_master = (h == "Master")
    can_create_user = is_master or bool(user.get("pode_criar_usuario"))
    can_create_link = h in ("Master", "Administrador")

    if is_master:
        allowed_roles = ["Master", "Administrador", "uniao", "associacao", "escola"]
    elif can_create_user:
        allowed_roles = ["Administrador", "uniao", "associacao", "escola"]
    else:
        allowed_roles = []

    return jsonify({
        "usuario_hierarquia": h,
        "is_master": is_master,
        "pode_criar_usuario": can_create_user,
        "pode_criar_link": can_create_link,
        "can_grant_pode_criar_usuario": is_master,
        "can_grant_pode_criar_link": False, # Automaticamente disponivel para Master e Administrador
        "allowed_target_hierarchies": allowed_roles
    }), 200
