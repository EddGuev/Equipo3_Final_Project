"""
AI Manager - Gestor centralizado de modelos de IA
Soporta Gemini (real) y Simulador (mock) con switch dinámico
"""
import google.generativeai as genai
from config import Config
import time
import random

class AIManager:
    def __init__(self):
        self.current_mode = Config.AI_MODE
        self.gemini_model = None
        self._initialize()
    
    def _initialize(self):
        \"\"\"Inicializa el modelo según configuración\"\"\"
        if self.current_mode == 'real':
            if not Config.GEMINI_API_KEY:
                raise ValueError('API Key de Gemini no configurada')
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(Config.GEMINI_MODEL)
    
    def set_mode(self, mode):
        \"\"\"
        Cambia el modo de IA en runtime
        Args:
            mode (str): 'real' o 'mock'
        Returns:
            tuple: (success, message)
        \"\"\"
        if mode not in ['real', 'mock']:
            return False, 'Modo inválido. Use real o mock'
        
        if mode == 'real' and not Config.GEMINI_API_KEY:
            return False, 'API Key de Gemini no configurada en .env'
        
        self.current_mode = mode
        if mode == 'real' and not self.gemini_model:
            self._initialize()
        
        return True, f'Modo cambiado a: {self.get_mode_display()}'
    
    def get_mode_display(self):
        \"\"\"Retorna el modo actual en formato legible\"\"\"
        return '🤖 Gemini Real' if self.current_mode == 'real' else '💭 Simulador'
    
    def ask(self, question, context):
        \"\"\"
        Envía pregunta al modelo activo
        Args:
            question (str): Pregunta del usuario
            context (str): Contenido del documento
        Returns:
            str: Respuesta generada
        \"\"\"
        if self.current_mode == 'real':
            return self._ask_gemini(question, context)
        else:
            return self._ask_mock(question, context)
    
    def _ask_gemini(self, question, context):
        \"\"\"Consulta a Gemini real\"\"\"
        try:
            prompt = f\"\"\"Eres un asistente que responde preguntas sobre documentos.

CONTEXTO DEL DOCUMENTO:
{context[:4000]}  # Limitar contexto para no exceder tokens

PREGUNTA DEL USUARIO:
{question}

INSTRUCCIONES:
- Responde SOLO basándote en el contexto proporcionado
- Si la respuesta no está en el contexto, di: \"No encuentro esa información en el documento\"
- Sé conciso y preciso
- Cita fragmentos relevantes si es necesario
\"\"\"
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            return f'❌ Error al consultar Gemini: {str(e)}'
    
    def _ask_mock(self, question, context):
        \"\"\"Simulador de respuestas (para pruebas sin API)\"\"\"
        time.sleep(0.5)  # Simular latencia de red
        
        # Respuestas inteligentes basadas en palabras clave
        q_lower = question.lower()
        
        if any(word in q_lower for word in ['resumen', 'trata', 'sobre', 'tema']):
            return f'📄 Este documento trata sobre: {context[:200]}...'
        
        elif any(word in q_lower for word in ['cuánto', 'cuándo', 'fecha', 'número']):
            return '🔢 Según el documento, la información numérica relevante es: [simulación de datos]'
        
        elif any(word in q_lower for word in ['cómo', 'proceso', 'pasos']):
            return '📋 El proceso descrito en el documento incluye los siguientes pasos: [simulación de pasos]'
        
        elif any(word in q_lower for word in ['quién', 'autor', 'responsable']):
            return '👤 El documento menciona a: [simulación de nombres]'
        
        else:
            responses = [
                f'💡 Basándome en el documento, puedo decir que: {context[:150]}...',
                f'📌 La respuesta a tu pregunta se encuentra en: {context[100:250]}...',
                f'✅ Según el contenido analizado: {context[50:200]}...'
            ]
            return random.choice(responses)
    
    def validate_connection(self):
        \"\"\"
        Valida la conexión con el servicio activo
        Returns:
            tuple: (success, message)
        \"\"\"
        if self.current_mode == 'mock':
            return True, 'Simulador listo'
        
        try:
            # Test simple con Gemini
            test_response = self.gemini_model.generate_content('Hola')
            return True, 'Gemini conectado correctamente'
        except Exception as e:
            return False, f'Error de conexión: {str(e)}'
