# src/views/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFileDialog, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

class VentanaPrincipal(QMainWindow):
    enviar_pregunta = pyqtSignal(str)
    solicitar_archivo = pyqtSignal()

    # nuevas señales para exportación
    export_json_requested = pyqtSignal()
    export_xml_requested = pyqtSignal()

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self._configurar_ui()

    def _configurar_ui(self):
        self.setWindowTitle(f"ChatDoc - Sesión de {self.usuario}")
        self.resize(900, 700)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4; font-family: 'Segoe UI';")

        central = QWidget()
        self.setCentralWidget(central)

        # Layout principal horizontal: panel lateral (izq) + contenido (der)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)

        # --- Contenido principal (chat) como widget separado para facilitar inserción ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)

        # Encabezado
        header = QFrame()
        header.setStyleSheet("background-color: #24273a; border-bottom: 1px solid #313244;")
        layout_h = QHBoxLayout(header)
        layout_h.setContentsMargins(10, 8, 10, 8)

        lbl_titulo = QLabel(f"📄 Analizando como: {self.usuario}")
        lbl_titulo.setStyleSheet("font-weight: bold; font-size: 14px; color: #89b4fa;")
        layout_h.addWidget(lbl_titulo)

        layout_h.addStretch()

        self.btn_archivo = QPushButton("📂 Cargar Archivo")
        self.btn_archivo.setStyleSheet("""
            QPushButton { background-color: #313244; padding: 8px 15px; border-radius: 5px; font-weight: bold; color: #cdd6f4; }
            QPushButton:hover { background-color: #45475a; }
        """)
        self.btn_archivo.clicked.connect(lambda: self.solicitar_archivo.emit())
        layout_h.addWidget(self.btn_archivo)

        content_layout.addWidget(header)

        # Área de Chat
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            background-color: #181825;
            border: none;
            padding: 20px;
            font-size: 14px;
            line-height: 1.5;
        """)
        content_layout.addWidget(self.chat_area)

        # Barra de entrada
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.entrada_pregunta = QLineEdit()
        self.entrada_pregunta.setPlaceholderText("Escribe tu pregunta sobre el documento...")
        self.entrada_pregunta.setStyleSheet("""
            background-color: #313244; border: 1px solid #45475a;
            border-radius: 10px; padding: 12px; color: #cdd6f4;
        """)
        self.entrada_pregunta.returnPressed.connect(self._manejar_envio)
        input_layout.addWidget(self.entrada_pregunta)

        self.btn_enviar = QPushButton("✈️")
        self.btn_enviar.setFixedSize(50, 42)
        self.btn_enviar.setStyleSheet("background-color: #89b4fa; border-radius: 10px; font-size: 18px;")
        self.btn_enviar.clicked.connect(self._manejar_envio)
        input_layout.addWidget(self.btn_enviar)

        content_layout.addWidget(input_frame)

        # Guardamos el widget de contenido para el panel lateral (en caso necesario)
        self.chat_widget = content_widget

        # --- Panel lateral (se añadirá a la izquierda) ---
        self.setup_side_panel()

        # Insertar widgets en el layout principal: primero panel lateral, luego contenido
        main_layout.addWidget(self.side_panel, 0)     # tamaño fijo relativo
        main_layout.addWidget(self.chat_widget, 1)    # ocupa el resto

    def setup_side_panel(self):
        """Crear y configurar el panel lateral con botones para exportar y etiqueta de archivo."""
        self.side_panel = QWidget()
        self.side_panel.setFixedWidth(220)
        self.side_panel.setStyleSheet("background-color: #191a21; border: 1px solid #2a2b33; padding: 10px;")
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_layout.setContentsMargins(8, 8, 8, 8)
        self.side_layout.setSpacing(10)

        # Etiqueta para el archivo cargado
        self.lbl_archivo = QLabel("Archivo: Ninguno")
        self.lbl_archivo.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        self.side_layout.addWidget(self.lbl_archivo)

        # Separador visual
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #313244;")
        self.side_layout.addWidget(sep)

        # Botón Exportar JSON
        self.btn_export_json = QPushButton("Exportar JSON")
        self.btn_export_json.setStyleSheet("""
            QPushButton { background-color: #313244; padding: 8px; border-radius: 6px; color: #cdd6f4; }
            QPushButton:hover { background-color: #45475a; }
        """)
        self.btn_export_json.clicked.connect(lambda: self.export_json_requested.emit())
        self.side_layout.addWidget(self.btn_export_json)

        # Botón Exportar XML
        self.btn_export_xml = QPushButton("Exportar XML")
        self.btn_export_xml.setStyleSheet("""
            QPushButton { background-color: #313244; padding: 8px; border-radius: 6px; color: #cdd6f4; }
            QPushButton:hover { background-color: #45475a; }
        """)
        self.btn_export_xml.clicked.connect(lambda: self.export_xml_requested.emit())
        self.side_layout.addWidget(self.btn_export_xml)

        self.side_layout.addStretch()

    def _manejar_envio(self):
        texto = self.entrada_pregunta.text().strip()
        if texto:
            self.agregar_mensaje("Tú", texto, "#b4befe")
            self.entrada_pregunta.clear()
            self.enviar_pregunta.emit(texto)

    def agregar_mensaje(self, autor, mensaje, color):
        # Añade salto de línea extra para separar burbujas de mensajes
        self.chat_area.append(f"<b style='color: {color}'>{autor}:</b> {mensaje}<br>")

    def seleccionar_archivo(self):
        file_filter = "Documentos (*.txt *.pdf *.json *.xml)"
        fname, _ = QFileDialog.getOpenFileName(self, 'Seleccionar archivo', '', file_filter)
        return fname

    # Métodos utilitarios usados por el controlador:

    def set_loaded_file(self, filename: str):
        """Actualiza la etiqueta del archivo cargado en el panel lateral."""
        if hasattr(self, "lbl_archivo"):
            display = filename if filename else "Ninguno"
            # mostrar solo el nombre del archivo (no la ruta completa)
            try:
                short = filename.split("\\")[-1]
            except Exception:
                short = filename
            self.lbl_archivo.setText(f"Archivo: {short}")

    def get_save_path(self, typ: str) -> str:
        """Abre diálogo para escoger ruta de guardado y devuelve la ruta (o '' si canceló)."""
        if typ.lower() == "json":
            path, _ = QFileDialog.getSaveFileName(self, "Guardar JSON", "", "JSON Files (*.json)")
        else:
            path, _ = QFileDialog.getSaveFileName(self, "Guardar XML", "", "XML Files (*.xml)")
        return path or ""

    def mostrar_error(self, mensaje: str):
        QMessageBox.critical(self, "Error", mensaje)

    def mostrar_info(self, mensaje: str):
        QMessageBox.information(self, "Información", mensaje)