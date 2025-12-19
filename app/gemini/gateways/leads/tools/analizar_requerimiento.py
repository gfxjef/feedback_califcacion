"""
Tool: analizar_requerimiento

Analiza el texto del requerimiento usando Gemini IA
- compra_producto: El cliente quiere comprar productos/equipos
- servicio_tecnico: El cliente necesita calibracion, mantenimiento, reparacion

Usa Gemini para analisis contextual inteligente (no keywords)

Basado en el codigo original TypeScript
"""

import os
import json
import requests
from typing import Optional

try:
    from app.gemini.core.types import AnalizarRequerimientoResult
    from app.gemini.config import GEMINI_CONFIG, GEMINI_CONFIG_CLASIFICACION
except ImportError:
    from gemini.core.types import AnalizarRequerimientoResult
    from gemini.config import GEMINI_CONFIG, GEMINI_CONFIG_CLASIFICACION


def analizar_requerimiento(
    texto_requerimiento: str,
    empresa_nombre: Optional[str] = None,
    origen: Optional[str] = None
) -> AnalizarRequerimientoResult:
    """
    Analiza el requerimiento usando Gemini

    Args:
        texto_requerimiento: Texto del requerimiento a analizar
        empresa_nombre: Nombre de la empresa (opcional)
        origen: Origen del lead (opcional)

    Returns:
        AnalizarRequerimientoResult con la clasificacion
    """
    print(f"[analizar_requerimiento] Analizando con Gemini: {texto_requerimiento[:100]}...")

    try:
        # Validar que hay texto
        if not texto_requerimiento or texto_requerimiento.strip() == "":
            return {
                "success": False,
                "tipo_requerimiento": "compra_producto",
                "confianza": "baja",
                "keywords": [],
                "razonamiento": "No se proporciono texto de requerimiento",
                "error": "Texto de requerimiento vacio"
            }

        # Construir prompt para Gemini
        prompt = f"""Analiza el siguiente requerimiento de un cliente y clasifícalo como:
- "compra_producto": si el cliente quiere COMPRAR, COTIZAR, o ADQUIRIR productos/equipos
- "servicio_tecnico": si el cliente necesita CALIBRACIÓN, MANTENIMIENTO, REPARACIÓN, INSTALACIÓN, o cualquier SERVICIO TÉCNICO

Requerimiento: "{texto_requerimiento}"
"""

        if empresa_nombre:
            prompt += f"\nEmpresa: {empresa_nombre}"

        if origen:
            prompt += f"\nOrigen: {origen}"

        prompt += """

Responde ÚNICAMENTE con un JSON (sin markdown, sin bloques de código):
{
  "tipo": "compra_producto" o "servicio_tecnico",
  "confianza": "alta", "media" o "baja",
  "razonamiento": "breve explicación de tu decisión"
}"""

        # Validar API Key
        api_key = GEMINI_CONFIG.get("api_key") or os.getenv("GOOGLE_API", "")

        if not api_key:
            print("[analizar_requerimiento] ERROR: API Key de Gemini no configurada")
            return {
                "success": False,
                "tipo_requerimiento": "compra_producto",
                "confianza": "baja",
                "keywords": [],
                "razonamiento": "Error de configuracion",
                "error": "API Key de Gemini no disponible"
            }

        # Llamar a Gemini API
        model = GEMINI_CONFIG.get("model", "gemini-2.0-flash-exp")
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        gemini_payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": GEMINI_CONFIG_CLASIFICACION.get("temperature", 0.3),
                "maxOutputTokens": GEMINI_CONFIG_CLASIFICACION.get("max_output_tokens", 300),
                "topP": GEMINI_CONFIG_CLASIFICACION.get("top_p", 0.95),
                "topK": GEMINI_CONFIG_CLASIFICACION.get("top_k", 40)
            }
        }

        response = requests.post(
            gemini_url,
            json=gemini_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if not response.ok:
            error_text = response.text
            print(f"[analizar_requerimiento] Error de Gemini API: {error_text}")

            return {
                "success": False,
                "tipo_requerimiento": "compra_producto",
                "confianza": "baja",
                "keywords": [],
                "razonamiento": "Error al analizar con IA",
                "error": f"Error de Gemini API: {response.status_code}"
            }

        gemini_data = response.json()

        # Extraer texto de la respuesta
        candidate = gemini_data.get("candidates", [{}])[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        text_part = next((p for p in parts if "text" in p), None)

        if not text_part or not text_part.get("text"):
            print("[analizar_requerimiento] No se encontro texto en la respuesta")

            return {
                "success": False,
                "tipo_requerimiento": "compra_producto",
                "confianza": "baja",
                "keywords": [],
                "razonamiento": "No se pudo obtener respuesta de IA",
                "error": "Respuesta vacia de Gemini"
            }

        response_text = text_part["text"].strip()
        print(f"[analizar_requerimiento] Respuesta de Gemini: {response_text}")

        # Parsear JSON de la respuesta
        try:
            # Limpiar markdown si existe
            cleaned_text = response_text

            if "```json" in cleaned_text:
                cleaned_text = cleaned_text.replace("```json", "").replace("```", "").strip()
            elif "```" in cleaned_text:
                cleaned_text = cleaned_text.replace("```", "").strip()

            parsed_data = json.loads(cleaned_text)

        except json.JSONDecodeError as parse_error:
            print(f"[analizar_requerimiento] Error al parsear JSON: {parse_error}")

            return {
                "success": False,
                "tipo_requerimiento": "compra_producto",
                "confianza": "baja",
                "keywords": [],
                "razonamiento": "Error al interpretar respuesta de IA",
                "error": "No se pudo parsear respuesta JSON"
            }

        # Validar tipo
        tipo_requerimiento = "servicio_tecnico" if parsed_data.get("tipo") == "servicio_tecnico" else "compra_producto"

        confianza_raw = parsed_data.get("confianza", "media")
        confianza = confianza_raw if confianza_raw in ["alta", "media", "baja"] else "media"

        print(f"[analizar_requerimiento] Clasificado como: {tipo_requerimiento} ({confianza})")

        return {
            "success": True,
            "tipo_requerimiento": tipo_requerimiento,
            "confianza": confianza,
            "keywords": [],  # Ya no usamos keywords
            "razonamiento": parsed_data.get("razonamiento", "Analisis completado con IA")
        }

    except requests.exceptions.Timeout:
        print("[analizar_requerimiento] Timeout al conectar con Gemini API")
        return {
            "success": False,
            "tipo_requerimiento": "compra_producto",
            "confianza": "baja",
            "keywords": [],
            "razonamiento": "Timeout al analizar",
            "error": "Timeout al conectar con Gemini"
        }

    except Exception as e:
        print(f"[analizar_requerimiento] Error inesperado: {e}")

        return {
            "success": False,
            "tipo_requerimiento": "compra_producto",
            "confianza": "baja",
            "keywords": [],
            "razonamiento": "Error inesperado al analizar",
            "error": str(e)
        }
