"""
ChatDoc Window - Ventana de consulta de documentos
Integrada con la estructura PyQt6 existente
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QComboBox, QPushButton, QTextEdit,
                              QLineEdit, QFileDialog, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from pathlib import Path
import sys
import os

# Importar módulos locales
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from config import Config
from src.chatdoc.ai_manager import AIManager
from src.chatdoc.file_processor import FileProcessor


class VentanaChatDoc(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('ChatDoc - Sistema de Consulta de Documentos')
        self.setGeometry(100, 100, 900, 700)
        
        # Managers
        self.ai_manager = AIManager()
        self.file_processor = FileProcessor()
        
        # Variables
        self.current_file = None
        self.file_content = None
        self.can_process = False
        
        self._init_ui()
        self._validate_initial_mode()
    
    def _init_ui(self):
        \"\"\"Construye la interfaz\"\"\"
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # === GRUPO: Configuración ===
        config_group = QGroupBox('⚙️ Configuración')
        config_layout = QHBoxLayout()
        
        config_layout.addWidget(QLabel('Modo de IA:'))
        
        self.ai_mode_combo = QComboBox()
        self.ai_mode_combo.addItems(['🤖 Gemini Real', '💭 Simulador'])
        self.ai_mode_combo.setCurrentIndex(1 if self.ai_manager.current_mode == 'mock' else 0)
        self.ai_mode_combo.currentIndexChanged.connect(self._on_mode_change)
        config_layout.addWidget(self.ai_mode_combo)
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet('color: green; font-weight: bold;')
        config_layout.addWidget(self.status_label)
        
        config_layout.addStretch()
        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)
        
        # === GRUPO: Archivo ===
        file_group = QGroupBox('📁 Archivo')
        file_layout = QHBoxLayout()
        
        self.load_btn = QPushButton('Cargar archivo')
        self.load_btn.clicked.connect(self._load_file)
        file_layout.addWidget(self.load_btn)
        
        self.file_label = QLabel('Ningún archivo cargado')
        self.file_label.setStyleSheet('color: gray;')
        file_layout.addWidget(self.file_label)
        
        self.file_status = QLabel()
        file_layout.addWidget(self.file_status)
        
        file_layout.addStretch()
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # === GRUPO: Conversación ===
        chat_group = QGroupBox('💬 Conversación')
        chat_layout = QVBoxLayout()
        
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet(\"\"\"
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }
        \"\"\")
        chat_layout.addWidget(self.chat_area)
        
        # Input de pregunta
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel('Tu pregunta:'))
        
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText('Escribe tu pregunta aquí...')
        self.question_input.returnPressed.connect(self._send_question)
        input_layout.addWidget(self.question_input)
        
        self.send_btn = QPushButton('Enviar')
        self.send_btn.clicked.connect(self._send_question)
        input_layout.addWidget(self.send_btn)
        
        chat_layout.addLayout(input_layout)
        chat_group.setLayout(chat_layout)
        main_layout.addWidget(chat_group)
        
        self._update_mode_display()
    
    def _validate_initial_mode(self):
        \"\"\"Valida el modo inicial\"\"\"
        success, message = self.ai_manager.validate_connection()
        if success:
            self._add_system_message(f'✅ {message}')
        else:
            self._add_system_message(f'⚠️ {message}')
            if self.ai_manager.current_mode == 'real':
                self.ai_manager.set_mode('mock')
                self.ai_mode_combo.setCurrentIndex(1)
                self._add_system_message('🔄 Cambiado a modo Simulador')
    
    def _on_mode_change(self):
        \"\"\"Maneja cambio de modo\"\"\"
        index = self.ai_mode_combo.currentIndex()
        new_mode = 'real' if index == 0 else 'mock'
        
        success, message = self.ai_manager.set_mode(new_mode)
        
        if success:
            self._add_system_message(f'✅ {message}')
            self._update_mode_display()
        else:
            QMessageBox.critical(self, 'Error', message)
            # Revertir
            self.ai_mode_combo.setCurrentIndex(1 if self.ai_manager.current_mode == 'mock' else 0)
    
    def _update_mode_display(self):
        \"\"\"Actualiza indicador de estado\"\"\"
        display = self.ai_manager.get_mode_display()
        self.status_label.setText(f'Estado: {display}')
    
    def _load_file(self):
        \"\"\"Carga archivo\"\"\"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Seleccionar archivo',
            '',
            'Archivos soportados (*.txt *.pdf *.json *.xml *.docx *.csv);;Todos los archivos (*.*)'
        )
        
        if not file_path:
            return
        
        success, content, can_process = self.file_processor.read_file(file_path)
        
        if not success:
            QMessageBox.critical(self, 'Error', content)
            return
        
        self.current_file = file_path
        self.file_content = content
        self.can_process = can_process
        
        file_info = self.file_processor.get_file_info(file_path)
        
        self.file_label.setText(f\"{file_info['name']} ({file_info['size_mb']} MB)\")
        self.file_label.setStyleSheet('color: black; font-weight: bold;')
        self.file_status.setText(file_info['status'])
        
        self._add_system_message(f\"📄 Archivo cargado: {file_info['name']}\")
        self._add_system_message(f\"   {file_info['status']}\")
        
        if not can_process:
            self._add_system_message('⚠️ Este archivo solo puede visualizarse, no se puede consultar con IA')
    
    def _send_question(self):
        \"\"\"Envía pregunta\"\"\"
        question = self.question_input.text().strip()
        
        if not question:
            return
        
        if not self.current_file:
            QMessageBox.warning(self, 'Advertencia', 'Primero carga un archivo')
            return
        
        if not self.can_process:
            QMessageBox.warning(
                self,
                'Advertencia',
                'Este archivo no puede ser procesado por IA.\\nSolo se aceptan archivos TXT y PDF.'
            )
            return
        
        self._add_user_message(question)
        self.question_input.clear()
        
        self.send_btn.setEnabled(False)
        
        try:
            answer = self.ai_manager.ask(question, self.file_content)
            self._add_ai_message(answer)
        except Exception as e:
            self._add_system_message(f'❌ Error: {str(e)}')
        finally:
            self.send_btn.setEnabled(True)
    
    def _add_user_message(self, message):
        \"\"\"Añade mensaje del usuario\"\"\"
        self.chat_area.append(f'<b style=\"color: blue;\">👤 Tú:</b> {message}<br>')
    
    def _add_ai_message(self, message):
        \"\"\"Añade respuesta de IA\"\"\"
        icon = '🤖' if self.ai_manager.current_mode == 'real' else '💭'
        self.chat_area.append(f'<b style=\"color: green;\">{icon} IA:</b> {message}<br>')
    
    def _add_system_message(self, message):
        \"\"\"Añade mensaje del sistema\"\"\"
        self.chat_area.append(f'<i style=\"color: gray;\">{message}</i><br>')
