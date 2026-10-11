import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from Backend.server import create_app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5050))
    print(f"==================================================")
    print(f"  Pluraal BI Iniciado em http://localhost:{port}")
    print(f"==================================================")
    app.run(host="0.0.0.0", port=port, debug=True)
