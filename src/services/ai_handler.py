"""
Servicio de IA (Simulado).
Procesa el prompt del usuario basándose en el contexto del archivo extraído.
"""
from typing import Optional

def get_response(prompt: str, contexto: Optional[str] = None) -> str:
    prompt = (prompt or "").lower()
    
    if not contexto or len(contexto.strip()) < 5:
        return "No hay contenido suficiente en el archivo para analizar. Por favor, asegúrate de que el archivo tenga texto."

    # Lógica de respuesta simulada basada en palabras clave
    if "hola" in prompt or "qué tal" in prompt:
        return "¡Hola! He analizado el documento. ¿En qué puedo ayudarte hoy?"
    
    if "resumen" in prompt or "resumir" in prompt:
        # En una fase real, aquí enviaríamos el contexto a GPT/Llama
        resumen = contexto[:300] + "..." if len(contexto) > 300 else contexto
        return f"Aquí tienes un resumen del inicio del documento: \n\n{resumen}"

    if "datos" in prompt or "números" in prompt:
        return "He detectado datos numéricos en el archivo, pero necesito un modelo avanzado para tabularlos. ¿Buscas algo específico?"

    # Fallback genérico
    return "Entiendo tu pregunta. Basado en el documento cargado, parece que trata sobre temas técnicos. ¿Podrías ser más específico con tu duda?"
