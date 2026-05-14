import os
import sqlite3
from typing import List, Dict, Optional
from models.auth_model import obtener_conexion
from controllers.file_handler import FileHandler
from services.ai_handler import get_response

class ModeloChat:
    def __init__(self):
        self.archivo_actual: Optional[str] = None
        self.contenido_archivo: str = ""
        self._crear_tabla_mensajes()

    def _crear_tabla_mensajes(self):
        """Crea la tabla de historial si no existe."""
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            autor TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fuente_archivo TEXT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        conn.close()

    def cargar_archivo(self, ruta: str) -> str:
        """Extrae texto real del archivo seleccionado."""
        if not os.path.exists(ruta):
            return "Error: El archivo no existe en la ruta especificada."
            
        texto = FileHandler.extract_text(ruta)
        self.archivo_actual = os.path.basename(ruta)
        
        if isinstance(texto, str) and texto.startswith("Error"):
            return texto
            
        self.contenido_archivo = texto
        self.guardar_mensaje("Sistema", f"Archivo '{self.archivo_actual}' cargado correctamente.", fuente=self.archivo_actual)
        return f"Archivo '{self.archivo_actual}' cargado con éxito. Ahora puedes hacer preguntas."

    def guardar_mensaje(self, autor: str, mensaje: str, fuente: Optional[str] = None):
        """Persiste el mensaje en la base de datos SQLite."""
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO mensajes (autor, mensaje, fuente_archivo) VALUES (?, ?, ?)",
            (autor, mensaje, fuente)
        )
        conn.commit()
        conn.close()

    def obtener_historial(self, limite: int = 50) -> List[Dict]:
        """Recupera los últimos mensajes de la base de datos."""
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT autor, mensaje, fuente_archivo FROM mensajes ORDER BY id ASC LIMIT ?", (limite,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def obtener_respuesta_ia(self, pregunta: str) -> str:
        """Procesa la pregunta, guarda la interacción y devuelve la respuesta de la IA."""
        # 1. Guardar pregunta del usuario
        self.guardar_mensaje("Usuario", pregunta, fuente=self.archivo_actual)
        
        # 2. Obtener respuesta del servicio
        respuesta = get_response(pregunta, contexto=self.contenido_archivo)
        
        # 3. Guardar respuesta de la IA
        self.guardar_mensaje("Assistant", respuesta, fuente=self.archivo_actual)
        return respuesta
