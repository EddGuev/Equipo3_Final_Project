"""
Servicio de IA usando la SDK oficial de Google GenAI (Gemini).
Lee la clave desde la variable de entorno GEMINI_API_KEY o GOOGLE_API_KEY y llama al modelo configurado.
"""
import os
import logging
from typing import Optional

from google import genai

LOG = logging.getLogger(__name__)

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
MAX_CONTEXT_CHARS = int(os.getenv("GEMINI_MAX_CONTEXT_CHARS", "20000"))

if not API_KEY:
    LOG.warning("No se encontró GEMINI_API_KEY/GOOGLE_API_KEY en el entorno.")


def _make_client():
    if not API_KEY:
        raise RuntimeError("Gemini API key no configurada. Set GEMINI_API_KEY or GOOGLE_API_KEY.")
    return genai.Client(api_key=API_KEY)


def get_response(prompt: str, contexto: Optional[str] = None) -> str:
    prompt = (prompt or "").strip()
    contexto = (contexto or "").strip()

    if not contexto or len(contexto) < 5:
        return "No hay contenido suficiente en el archivo para analizar. Por favor, asegúrate de que el archivo tenga texto."

    if len(contexto) > MAX_CONTEXT_CHARS:
        contexto = contexto[:MAX_CONTEXT_CHARS] + "\n\n...[context truncated]..."

    full_input = (
        "Contexto del documento:\n"
        f"{contexto}\n\n"
        "Pregunta del usuario:\n"
        f"{prompt}\n\n"
        "Responde de forma clara, concisa y referenciando el contexto cuando sea necesario."
    )

    try:
        client = _make_client()
        resp = client.models.generate_content(model=MODEL, contents=full_input)
        text = getattr(resp, "text", None)
        if not text:
            try:
                text = resp.get("text", "")
            except Exception:
                text = str(resp)
        return text
    except Exception as e:
        LOG.exception("Error al llamar a Gemini:")
        return f"Error al obtener la respuesta de la IA: {e}"