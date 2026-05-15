#!/usr/bin/env python
import sys
import os

# Asegurarse de que la carpeta `src` esté en el path para imports tipo "controllers..." o "ai..."
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

# Cargar .env (si existe)
from dotenv import load_dotenv
load_dotenv()

# Inicializar BD (si existe el módulo)
try:
    from src.db.orm import init_db
except Exception:
    # Soporte alternativo: si el paquete es importable como 'db.orm' al tener 'src' en sys.path
    try:
        from db.orm import init_db
    except Exception:
        init_db = None

from PyQt6.QtWidgets import QApplication
# Importar el controlador de login (debe existir en src/controllers/login_controller.py)
try:
    from controllers.login_controller import ControladorLogin
except Exception:
    # Intento alternativo por si el paquete está estructurado distinto
    try:
        from src.controllers.login_controller import ControladorLogin
    except Exception:
        ControladorLogin = None

# Importar el simulador AI (implementado en src/ai/simulator.py)
try:
    from ai.simulator import get_ai_response
except Exception:
    # No crítico: la UI puede importar esta función más adelante si hace falta
    def get_ai_response(prompt, history=None):
        return "[Simulador no disponible]"


def iniciar_app():
    # Inicializar DB si la función está disponible
    if init_db:
        try:
            init_db()
        except Exception as e:
            print("Advertencia: init_db falló:", e)

    app = QApplication(sys.argv)

    if ControladorLogin is None:
        print("Error: no se encontró ControladorLogin. Verifica 'src/controllers/login_controller.py'")
        return

    controlador = ControladorLogin()
    controlador.mostrar()

    sys.exit(app.exec())


if __name__ == "__main__":
    iniciar_app()
