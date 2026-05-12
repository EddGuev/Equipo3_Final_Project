import sys
import os

# Añade la carpeta "src" al path para que imports como "from controllers... " funcionen
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
)

from PyQt6.QtWidgets import QApplication
from controllers.login_controller import ControladorLogin

def iniciar_app():
    app = QApplication(sys.argv)

    controlador = ControladorLogin()
    controlador.mostrar()

    sys.exit(app.exec())

if __name__ == "__main__":
    iniciar_app()