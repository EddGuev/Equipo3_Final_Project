"""
Launcher independiente para ChatDoc
Úsalo si quieres probar ChatDoc sin el sistema de login
"""
import sys
from PyQt6.QtWidgets import QApplication
from src.chatdoc.chatdoc_window import VentanaChatDoc

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaChatDoc()
    ventana.show()
    sys.exit(app.exec())
