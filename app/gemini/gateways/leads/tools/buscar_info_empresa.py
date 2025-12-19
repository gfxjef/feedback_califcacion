"""
Tool: buscar_info_empresa

Busca informacion de una empresa usando IA (Gemini)
- RUC (numero de identificacion tributaria)
- Sector/Rubro al que pertenece

Usa Google Gemini con google_search para busqueda web e inferencia

Basado en el codigo original TypeScript
"""

import os
import json
import requests
from typing import Optional

try:
    from app.gemini.core.types import BuscarInfoEmpresaResult
    from app.gemini.config import GEMINI_CONFIG
except ImportError:
    from gemini.core.types import BuscarInfoEmpresaResult
    from gemini.config import GEMINI_CONFIG


def buscar_info_empresa(
    nombre_empresa: str,
    departamento: Optional[str] = None,
    contexto: Optional[str] = None
) -> BuscarInfoEmpresaResult:
    """
    Busca RUC y sector de una empresa usando Gemini con Google Search

    Args:
        nombre_empresa: Nombre de la empresa a buscar
        departamento: Departamento de Peru (opcional)
        contexto: Contexto adicional (opcional)

    Returns:
        BuscarInfoEmpresaResult con la informacion encontrada
    """
    print(f"[buscar_info_empresa] Buscando: {nombre_empresa}")

    try:
        # Validar nombre de empresa
        if not nombre_empresa or nombre_empresa.strip() == "":
            return {
                "success": False,
                "ruc": None,
                "sector_rubro": None,
                "razon_social_completa": None,
                "confianza": "baja",
                "fuente": "no_encontrado",
                "error": "Nombre de empresa no proporcionado"
            }

        # Construir prompt para Gemini
        prompt = f'Encuentra el numero de RUC de la empresa "{nombre_empresa}"'

        if departamento:
            prompt += f" ubicada en {departamento}, Perú"
        else:
            prompt += " en Perú"

        if contexto:
            prompt += f". Contexto adicional: {contexto}"

        prompt += ". También identifica su sector o rubro principal (ej: Minería, Alimentos, Salud, Pesquera, Servicios, etc.)."
        prompt += " Si no encuentras información exacta, responde con ruc null y sector_rubro null."
        prompt += ' Responde ÚNICAMENTE con formato JSON puro sin markdown, sin bloques de código, sin explicaciones adicionales.'
        prompt += ' Formato exacto: {"ruc": "numero_ruc_o_null", "sector_rubro": "sector_o_null", "razon_social": "razon_social_completa_o_null"}'

        # Validar API Key
        api_key = GEMINI_CONFIG.get("api_key") or os.getenv("GOOGLE_API", "")

        if not api_key:
            print("[buscar_info_empresa] ERROR: API Key de Gemini no configurada")
            return {
                "success": False,
                "ruc": None,
                "sector_rubro": None,
                "razon_social_completa": None,
                "confianza": "baja",
                "fuente": "no_encontrado",
                "error": "API Key de Gemini no configurada"
            }

        # Llamar a Gemini API con google_search
        model = GEMINI_CONFIG.get("model", "gemini-2.0-flash-exp")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,  # Baja para precision
                "maxOutputTokens": 500
            },
            "tools": [
                {"google_search": {}}  # Sintaxis para Gemini 2.0+
            ]
        }

        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if not response.ok:
            error_text = response.text
            print(f"[buscar_info_empresa] Error de Gemini API: {error_text}")

            return {
                "success": False,
                "ruc": None,
                "sector_rubro": None,
                "razon_social_completa": None,
                "confianza": "baja",
                "fuente": "no_encontrado",
                "error": f"Error de Gemini API: {response.status_code}"
            }

        data = response.json()

        # Extraer texto de la respuesta
        candidate = data.get("candidates", [{}])[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        text_part = next((p for p in parts if "text" in p), None)

        if not text_part or not text_part.get("text"):
            print("[buscar_info_empresa] No se encontro texto en la respuesta")

            return {
                "success": False,
                "ruc": None,
                "sector_rubro": None,
                "razon_social_completa": None,
                "confianza": "baja",
                "fuente": "no_encontrado",
                "error": "Respuesta vacia de Gemini"
            }

        text = text_part["text"].strip()
        print(f"[buscar_info_empresa] Respuesta de Gemini: {text}")

        # Limpiar markdown si existe
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "").strip()
        elif "```" in text:
            text = text.replace("```", "").strip()

        # Parsear JSON
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"[buscar_info_empresa] Error al parsear JSON: {e}")

            return {
                "success": False,
                "ruc": None,
                "sector_rubro": None,
                "razon_social_completa": None,
                "confianza": "baja",
                "fuente": "no_encontrado",
                "error": "No se pudo parsear respuesta JSON"
            }

        ruc = parsed.get("ruc")
        sector_rubro = parsed.get("sector_rubro")
        razon_social = parsed.get("razon_social")

        # Convertir "null" string a None
        if ruc == "null" or ruc == "":
            ruc = None
        if sector_rubro == "null" or sector_rubro == "":
            sector_rubro = None
        if razon_social == "null" or razon_social == "":
            razon_social = None

        # Determinar confianza basada en que datos encontramos
        if ruc and sector_rubro and razon_social:
            confianza = "alta"
        elif ruc and sector_rubro:
            confianza = "media"
        elif ruc or sector_rubro:
            confianza = "baja"
        else:
            return {
                "success": False,
                "ruc": None,
                "sector_rubro": None,
                "razon_social_completa": None,
                "confianza": "baja",
                "fuente": "no_encontrado"
            }

        print(f"[buscar_info_empresa] Encontrado - RUC: {ruc}, Sector: {sector_rubro}")

        return {
            "success": True,
            "ruc": ruc,
            "sector_rubro": sector_rubro,
            "razon_social_completa": razon_social,
            "confianza": confianza,
            "fuente": "web"
        }

    except requests.exceptions.Timeout:
        print("[buscar_info_empresa] Timeout al conectar con Gemini API")
        return {
            "success": False,
            "ruc": None,
            "sector_rubro": None,
            "razon_social_completa": None,
            "confianza": "baja",
            "fuente": "no_encontrado",
            "error": "Timeout al conectar con Gemini"
        }

    except Exception as e:
        print(f"[buscar_info_empresa] Error inesperado: {e}")

        return {
            "success": False,
            "ruc": None,
            "sector_rubro": None,
            "razon_social_completa": None,
            "confianza": "baja",
            "fuente": "no_encontrado",
            "error": str(e)
        }
