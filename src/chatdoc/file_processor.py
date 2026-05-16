"""
File Processor - Lector universal de archivos
Lee cualquier formato, procesa solo TXT/PDF
"""
import os
from pathlib import Path
import pdfplumber
from config import Config

class FileProcessor:
    def __init__(self):
        self.supported_formats = Config.SUPPORTED_FORMATS
        self.processable_formats = Config.PROCESSABLE_FORMATS
    
    def can_read(self, file_path):
        \"\"\"Verifica si el archivo puede ser leído\"\"\"
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_formats
    
    def can_process(self, file_path):
        \"\"\"Verifica si el archivo puede ser procesado por IA\"\"\"
        ext = Path(file_path).suffix.lower()
        return ext in self.processable_formats
    
    def read_file(self, file_path):
        \"\"\"
        Lee el contenido del archivo
        Returns:
            tuple: (success, content_or_error, can_process)
        \"\"\"
        if not os.path.exists(file_path):
            return False, 'Archivo no encontrado', False
        
        ext = Path(file_path).suffix.lower()
        
        if not self.can_read(file_path):
            return False, f'Formato {ext} no soportado', False
        
        can_process = self.can_process(file_path)
        
        try:
            if ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return True, content, can_process
            
            elif ext == '.pdf':
                content = self._read_pdf(file_path)
                return True, content, can_process
            
            else:
                # Otros formatos: se leen pero no se procesan
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return True, content, can_process
        
        except Exception as e:
            return False, f'Error al leer archivo: {str(e)}', False
    
    def _read_pdf(self, file_path):
        \"\"\"Extrae texto de PDF usando pdfplumber\"\"\"
        text_content = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(f'--- Página {page_num} ---\n{text}')
        
        return '\n\n'.join(text_content)
    
    def get_file_info(self, file_path):
        \"\"\"Retorna información del archivo\"\"\"
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        ext = Path(file_path).suffix.lower()
        
        return {
            'name': Path(file_path).name,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / 1024 / 1024, 2),
            'extension': ext,
            'can_read': self.can_read(file_path),
            'can_process': self.can_process(file_path),
            'status': self._get_status_message(ext)
        }
    
    def _get_status_message(self, ext):
        \"\"\"Mensaje de estado según extensión\"\"\"
        if ext in self.processable_formats:
            return '✅ Listo para procesar'
        elif ext in self.supported_formats:
            return '⚠️ Solo lectura (no procesable por IA)'
        else:
            return '❌ Formato no soportado'
