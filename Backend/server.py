import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from Backend.config.settings import settings
from Backend.routes import auth_bp, user_bp, link_bp, hierarchy_bp

FRONTEND_DIR = ROOT_DIR / "Frontend"

def create_app():
    app = Flask(__name__, static_folder=None)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(link_bp)
    app.register_blueprint(hierarchy_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "Pluraal BI API",
            "engine": settings.DB_ENGINE,
            "version": "1.0.0"
        }), 200

    # Serve static frontend files
    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        return send_from_directory(FRONTEND_DIR / "assets", filename)

    @app.route("/css/<path:filename>")
    def serve_css(filename):
        return send_from_directory(FRONTEND_DIR / "css", filename)

    @app.route("/js/<path:filename>")
    def serve_js(filename):
        return send_from_directory(FRONTEND_DIR / "js", filename)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api/"):
            return jsonify({"error": "NOT_FOUND", "message": "Endpoint não encontrado."}), 404
        
        target = FRONTEND_DIR / path
        if path and target.exists() and target.is_file():
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"Iniciando Pluraal BI na porta {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
