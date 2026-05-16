"""
Configuración centralizada de la aplicación ChatDoc.
Lee variables de entorno desde .env
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Rutas
    BASE_DIR = Path(__file__).parent
    DB_PATH = os.getenv('DB_PATH', 'chatdoc.db')
    
    # IA
    AI_MODE = os.getenv('AI_MODE', 'mock')  # 'real' o 'mock'
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    # Formatos soportados (lee cualquiera, procesa solo TXT/PDF)
    SUPPORTED_FORMATS = ['.txt', '.pdf', '.json', '.xml', '.docx', '.csv']
    PROCESSABLE_FORMATS = ['.txt', '.pdf']  # Solo estos se procesan
    
    # MongoDB (preparado para futuro)
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    MONGO_DB = os.getenv('MONGO_DB', 'chatdoc')
    MONGO_ENABLED = os.getenv('MONGO_ENABLED', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls):
        \"\"\"Valida la configuración\"\"\"
        if cls.AI_MODE == 'real' and not cls.GEMINI_API_KEY:
            raise ValueError('GEMINI_API_KEY requerida cuando AI_MODE=real')
        
        if cls.AI_MODE not in ['real', 'mock']:
            raise ValueError('AI_MODE debe ser real o mock')
        
        return True
    
    @classmethod
    def get_ai_mode_display(cls):
        \"\"\"Retorna el modo de IA en formato legible\"\"\"
        return 'Gemini (Real)' if cls.AI_MODE == 'real' else 'Simulador (Mock)'
