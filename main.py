#!/usr/bin/env python
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

# Cargar .env
from dotenv import load_dotenv
load_dotenv()

from PyQt6.QtWidgets import QApplication
from db.orm import init_db
from controllers.login_controller import ControladorLogin


def iniciar_app():
    # Inicializar base de datos
    try:
        init_db()
        print("✓ Base de datos inicializada")
    except Exception as e:
        print(f"Advertencia: init_db falló: {e}")

    app = QApplication(sys.argv)
    
    controlador = ControladorLogin()
    controlador.mostrar()

    sys.exit(app.exec())


if __name__ == "__main__":
    iniciar_app()
