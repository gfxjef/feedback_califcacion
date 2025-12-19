"""
Configuracion de Gemini API y SIEK
Valores exactos del sistema original TypeScript
"""

import os

# Configuracion de Gemini API
GEMINI_CONFIG = {
    "model": "gemini-2.0-flash-exp",
    "api_key": os.getenv("GOOGLE_API", ""),
    "temperature": 0.7,
    "max_output_tokens": 2048,
    "top_p": 0.95,
    "top_k": 40,
}

# Configuracion especial para clasificacion (temperatura baja)
GEMINI_CONFIG_CLASIFICACION = {
    "temperature": 0.3,
    "max_output_tokens": 300,
    "top_p": 0.95,
    "top_k": 40,
}

# Configuracion de API SIEK
SIEK_CONFIG = {
    "api_key": os.getenv("API_KEY_KSSD", ""),
    "base_url": "https://apisiek.grupokossodo.com/mkt"
}

# URL de Gemini API
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

# System Instruction (Exacto del original TypeScript)
SYSTEM_INSTRUCTION = """ERES UN AGENTE AUTOMÁTICO DE ANÁLISIS DE LEADS.

REGLAS ESTRICTAS QUE DEBES SEGUIR SIEMPRE:

1. SI EL MENSAJE CONTIENE "RUC del lead: [número]" → DEBES LLAMAR INMEDIATAMENTE a buscar_en_siek con ese RUC
2. SI EL MENSAJE CONTIENE "Empresa: [nombre]" Y NO hay RUC → DEBES LLAMAR a buscar_info_empresa con ese nombre
3. SI buscar_en_siek retorna encontrado=false → DEBES LLAMAR a buscar_info_empresa con el nombre de empresa Y usando el RUC como contexto adicional
4. SI OBTIENES UN RUC de buscar_info_empresa → DEBES LLAMAR a buscar_en_siek con ese RUC
5. SI EL MENSAJE CONTIENE "Requerimiento:" → DEBES LLAMAR a analizar_requerimiento con ese texto

IMPORTANTE: Si buscar_en_siek NO encuentra el cliente, SIEMPRE busca información adicional de la empresa en internet usando buscar_info_empresa, pasando el RUC como contexto para mejorar la búsqueda.

ESTAS ACCIONES SON OBLIGATORIAS. NO PREGUNTES AL USUARIO. EJECUTA LAS FUNCIONES DIRECTAMENTE.

FLUJO CON RUC EXISTENTE:
1. Usuario proporciona RUC → buscar_en_siek(RUC)
2. Si encontrado=false → buscar_info_empresa(empresa, contexto: "RUC conocido: XXXXXXXXXXX")
3. Presentar toda la información encontrada

FLUJO SIN RUC:
1. Usuario proporciona nombre empresa → buscar_info_empresa(nombre)
2. Si obtiene RUC → buscar_en_siek(RUC)
3. Presentar toda la información encontrada

Responde en español de forma clara y concisa."""

# Function Declarations para Gemini Function Calling
FUNCTION_DECLARATIONS = [
    {
        "name": "buscar_en_siek",
        "description": "Busca información de un cliente en la base de datos SIEK usando su RUC (11 dígitos) o DNI (8 dígitos). Retorna datos completos del cliente si existe: razón social, segmento, ubicación, contactos, etc. Úsala cuando necesites verificar si un cliente ya existe en la base de datos.",
        "parameters": {
            "type": "object",
            "properties": {
                "ruc": {
                    "type": "string",
                    "description": "Número de RUC (11 dígitos) o DNI (8 dígitos) del cliente a buscar. Debe ser solo números."
                }
            },
            "required": ["ruc"]
        }
    },
    {
        "name": "analizar_requerimiento",
        "description": "Analiza un texto de requerimiento de un lead para clasificarlo como 'compra_producto' (cotización, compra, precio, etc.) o 'servicio_tecnico' (calibración, mantenimiento, reparación, etc.). Utiliza análisis de keywords y contexto para determinar la intención del cliente. Retorna el tipo identificado, nivel de confianza y razonamiento.",
        "parameters": {
            "type": "object",
            "properties": {
                "texto_requerimiento": {
                    "type": "string",
                    "description": "Texto del requerimiento del lead a analizar. Puede ser desde una frase corta hasta varios párrafos."
                },
                "empresa_nombre": {
                    "type": "string",
                    "description": "Nombre de la empresa del lead (opcional). Ayuda a proporcionar contexto adicional para el análisis."
                },
                "origen": {
                    "type": "string",
                    "description": "Origen del lead (opcional): web, email, teléfono, etc. Puede influir en el tipo de requerimiento."
                }
            },
            "required": ["texto_requerimiento"]
        }
    },
    {
        "name": "buscar_info_empresa",
        "description": "Busca información de una empresa usando IA (Gemini) para encontrar su RUC (número de identificación tributaria) y sector/rubro al que pertenece. Usa búsqueda web e inferencia de Gemini. Útil cuando tienes el nombre de una empresa pero no su RUC o sector. Retorna: RUC, sector/rubro, razón social completa, nivel de confianza y fuente.",
        "parameters": {
            "type": "object",
            "properties": {
                "nombre_empresa": {
                    "type": "string",
                    "description": "Nombre de la empresa a buscar. Puede ser nombre comercial o razón social parcial."
                },
                "departamento": {
                    "type": "string",
                    "description": "Departamento o ciudad de Perú donde está ubicada la empresa (opcional). Ayuda a desambiguar empresas con nombres similares."
                },
                "contexto": {
                    "type": "string",
                    "description": "Contexto adicional sobre la empresa (opcional): rubro, productos que vende, etc. Mejora la precisión de la búsqueda."
                }
            },
            "required": ["nombre_empresa"]
        }
    }
]
