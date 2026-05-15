# src/ai/simulator.py
"""
Simulador avanzado para respuestas tipo IA.
Este módulo intenta comportarse como proveedor de fallback cuando no hay API keys.
Exporta `get_ai_response(prompt, history=None)`.
"""
from dotenv import load_dotenv
load_dotenv()

import os
import random
import re
import textwrap
from typing import List, Optional

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
USE_SIMULATOR = not (bool(GEMINI_API_KEY) or bool(GOOGLE_API_KEY))

_STOPWORDS = {
    "de","la","que","el","en","y","a","los","del","se","las","por","un","para",
    "con","no","una","su","al","lo","como","más","o","pero","sus","le","ya",
    "fue","este","ha","sí","son","entre"
}


def _tokenize(text: str) -> List[str]:
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return [t for t in text.split() if t and t not in _STOPWORDS]


def _top_keywords(text: str, n: int = 5) -> List[str]:
    toks = _tokenize(text)
    freq = {}
    for t in toks:
        freq[t] = freq.get(t, 0) + 1
    items = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    return [k for k, _ in items[:n]]


def _first_sentences(text: str, max_sent: int = 2) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sentences[:max_sent]).strip()


def simulate_ai_response(prompt: str, history: Optional[List[str]] = None) -> str:
    history = history or []
    p = prompt.strip()
    lower = p.lower()

    # Detectores simples
    wants_summary = any(k in lower for k in ("resum", "sintetiz", "summary", "resume"))
    wants_list = any(k in lower for k in ("lista", "puntos", "enumerar", "bullet", "bullets"))
    wants_explain = any(k in lower for k in ("explica", "explicar", "describe", "describir", "eli5"))

    keywords = _top_keywords(p, n=4)

    intros = [
        "Según lo que pides, aquí va una respuesta útil:",
        "Buena pregunta — esto es lo que propongo:",
        "Basado en la información disponible, respuesta:",
        "Aquí tienes una respuesta orientativa:"
    ]
    intro = random.choice(intros)

    ctx = ""
    if history:
        last = history[-1]
        ctx_k = _top_keywords(last, n=3)
        if ctx_k:
            ctx = f"(Contexto: {', '.join(ctx_k)}) "

    # Generadores de respuesta por tipo
    if wants_summary:
        if ":" in p and len(p.split(":", 1)[1].strip()) > 40:
            candidate = p.split(":", 1)[1].strip()
            summary = _first_sentences(candidate, max_sent=3)
            return f"{intro} {ctx}Resumen generado:\n\n{summary}"
        if keywords:
            return f"{intro} {ctx}Resumen breve: se centra en {', '.join(keywords)}. " \
                   "Si quieres un resumen más largo, pega el texto o pide 'resumen detallado'."

    if wants_list:
        parts = re.split(r'\band\b|,|;|\n', p)
        bullets = []
        for part in parts:
            txt = part.strip()
            if len(txt) > 8 and len(bullets) < 8:
                bullets.append(f"- {textwrap.shorten(txt, width=80)}")
        if bullets:
            return f"{intro} {ctx}Aquí tienes una lista basada en tu petición:\n" + "\n".join(bullets)
        if keywords:
            return f"{intro} {ctx}Puntos clave:\n" + "\n".join(f"- {k}" for k in keywords)

    if wants_explain:
        if "eli5" in lower or "como si tuviera 5" in lower or "como si fuera un niño" in lower:
            return f"{intro} {ctx}Explicación sencilla: Imagina que ... (resumen simple). Si quieres detalles técnicos, pide 'nivel técnico'."
        if keywords:
            return f"{intro} {ctx}Explicación sobre {', '.join(keywords)}:\n" + \
                   "En términos sencillos, esto significa que ... (detalle general)."

    base_answer_templates = [
        "He leído tu petición. Mi sugerencia principal es enfocarse en: {k}. ¿Quieres que desarrolle un plan?",
        "Respuesta orientativa: considera revisar {k} y validar con datos reales. Puedo preparar un checklist.",
        "Posible enfoque: 1) identificar {k}; 2) priorizar; 3) prototipar y testear. ¿Deseas ejemplos?"
    ]
    template = random.choice(base_answer_templates)
    ktext = ", ".join(keywords) if keywords else "los puntos clave mencionados"
    reply = template.format(k=ktext)

    if history:
        reply += f"\n\nNota: según el último mensaje ({textwrap.shorten(history[-1], 80)}), esto conecta con {ktext}."

    return f"{intro} {ctx}{reply}"


def get_ai_response(prompt: str, history: Optional[List[str]] = None) -> str:
    """
    Punto único de llamada para obtener respuesta AI.
    Si hay API keys, aquí deberías integrar las llamadas reales.
    """
    if USE_SIMULATOR:
        return simulate_ai_response(prompt, history)

    # Placeholder para integración real
    if GEMINI_API_KEY:
        return "[Implementar llamada a Gemini]"
    if GOOGLE_API_KEY:
        return "[Implementar llamada a Google]"

    return "[Error] No hay proveedor AI configurado."
