"""
Tool: buscar_en_siek

Busca informacion de un cliente en la base de datos SIEK por RUC/DNI
Hace una llamada HTTP directa a la API externa de SIEK

Basado en el codigo original TypeScript
"""

import os
import re
import requests
from typing import Dict

try:
    from app.gemini.core.types import BuscarEnSIEKResult
    from app.gemini.config import SIEK_CONFIG
except ImportError:
    from gemini.core.types import BuscarEnSIEKResult
    from gemini.config import SIEK_CONFIG


def buscar_en_siek(ruc: str) -> BuscarEnSIEKResult:
    """
    Busca un cliente en la API SIEK

    Args:
        ruc: Numero de RUC (11 digitos) o DNI (8 digitos)

    Returns:
        BuscarEnSIEKResult con los datos del cliente
    """
    print(f"[buscar_en_siek] Buscando cliente con RUC: {ruc}")

    try:
        # Validar RUC
        if not ruc or ruc.strip() == "":
            return {
                "success": False,
                "encontrado": False,
                "mensaje": "RUC/DNI no proporcionado"
            }

        # Limpiar RUC (solo numeros)
        ruc_limpio = re.sub(r'\D', '', ruc)

        if len(ruc_limpio) != 11 and len(ruc_limpio) != 8:
            return {
                "success": False,
                "encontrado": False,
                "mensaje": "RUC/DNI invalido. RUC debe tener 11 digitos, DNI debe tener 8 digitos"
            }

        # Obtener API Key
        api_key = SIEK_CONFIG.get("api_key") or os.getenv("API_KEY_KSSD", "")

        if not api_key:
            print("[buscar_en_siek] ERROR: API_KEY_KSSD no configurada")
            return {
                "success": False,
                "encontrado": False,
                "mensaje": "Error de configuracion: API Key SIEK no disponible"
            }

        # Llamar a API SIEK externa
        base_url = SIEK_CONFIG.get("base_url", "https://apisiek.grupokossodo.com/mkt")
        url = f"{base_url}/obtener-cliente/{ruc_limpio}"

        response = requests.get(
            url,
            headers={
                "Accept": "application/json",
                "API-Key": api_key
            },
            timeout=15
        )

        # Manejar 404 (no encontrado)
        if response.status_code == 404:
            print("[buscar_en_siek] Cliente no encontrado en SIEK")
            return {
                "success": True,
                "encontrado": False,
                "mensaje": f"Cliente con RUC/DNI {ruc_limpio} no encontrado en base SIEK"
            }

        # Manejar otros errores
        if not response.ok:
            try:
                error_data = response.json()
            except:
                error_data = {}

            print(f"[buscar_en_siek] Error en API SIEK: {error_data}")

            return {
                "success": False,
                "encontrado": False,
                "mensaje": error_data.get("error", f"Error al consultar SIEK: HTTP {response.status_code}")
            }

        # Procesar respuesta
        data = response.json()

        # La API SIEK retorna un array, tomamos el primer elemento
        cliente_data = data[0] if isinstance(data, list) and len(data) > 0 else data

        # Verificar si hay datos (array vacio = cliente no encontrado)
        if not cliente_data:
            print("[buscar_en_siek] Cliente no encontrado (array vacio)")
            return {
                "success": True,
                "encontrado": False,
                "mensaje": f"Cliente con RUC/DNI {ruc_limpio} no encontrado en base SIEK"
            }

        print(f"[buscar_en_siek] Cliente encontrado: {cliente_data.get('RazonSocial', '')}")

        return {
            "success": True,
            "encontrado": True,
            "data": cliente_data,
            "mensaje": f"Cliente encontrado: {cliente_data.get('RazonSocial', '')}"
        }

    except requests.exceptions.Timeout:
        print("[buscar_en_siek] Timeout al conectar con API SIEK")
        return {
            "success": False,
            "encontrado": False,
            "mensaje": "Timeout al conectar con API SIEK"
        }

    except Exception as e:
        print(f"[buscar_en_siek] Error inesperado: {e}")

        return {
            "success": False,
            "encontrado": False,
            "mensaje": str(e)
        }
