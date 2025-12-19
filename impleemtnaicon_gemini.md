# Documentacion: Sistema de Orquestacion Gemini para Analisis de Leads

## Resumen Ejecutivo

Sistema de orquestacion que utiliza **Google Gemini Function Calling** para analizar leads automaticamente. Permite buscar informacion de empresas, verificar clientes en base SIEK, y clasificar requerimientos.

**Tecnologia actual:** Next.js 15 + TypeScript
**Objetivo:** Adaptar a Python/Flask para el proyecto `feedback-califcacion.onrender.com`

---

## Arquitectura General

```
+-------------------------------------------------------------------------+
|                           FRONTEND (Next.js)                            |
+-------------------------------------------------------------------------+
|                                                                         |
|  +------------------------------------------------------------------+  |
|  |                     API Routes (Next.js)                          |  |
|  |  /api/gemini/orchestrator  ->  Endpoint principal                 |  |
|  |  /api/gemini/buscar-ruc    ->  Busqueda web con Gemini            |  |
|  +-------------------------------+----------------------------------+   |
|                                  |                                      |
|  +-------------------------------v----------------------------------+   |
|  |                    GatewayOrchestrator                            |  |
|  |  - Coordina multiples gateways                                    |  |
|  |  - Maneja loop de Function Calling                                |  |
|  |  - Comunica con Gemini API                                        |  |
|  +-------------------------------+----------------------------------+   |
|                                  |                                      |
|  +-------------------------------v----------------------------------+   |
|  |                      GatewayLeads                                 |  |
|  |  +-- buscar_en_siek()        ->  API SIEK externa                 |  |
|  |  +-- analizar_requerimiento() ->  Gemini directo                  |  |
|  |  +-- buscar_info_empresa()    ->  Gemini + Google Search          |  |
|  +------------------------------------------------------------------+   |
|                                                                         |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                        APIS EXTERNAS                                    |
+-------------------------------------------------------------------------+
|  - Google Gemini API (gemini-2.0-flash-exp)                            |
|  - API SIEK (apisiek.grupokossodo.com)                                 |
+-------------------------------------------------------------------------+
```

---

## Estructura de Archivos

### Archivos Core (Nucleo del Sistema)

| Archivo | Descripcion |
|---------|-------------|
| `frontend/lib/gemini/core/types.ts` | Interfaces y tipos TypeScript |
| `frontend/lib/gemini/core/base-gateway.ts` | Clase base abstracta para gateways |
| `frontend/lib/gemini/core/orchestrator.ts` | Orquestador principal (loop de function calling) |

### Archivos de Configuracion

| Archivo | Descripcion |
|---------|-------------|
| `frontend/lib/gemini/config/gemini-config.ts` | Configuracion de Gemini API (modelo, API key, temperatura) |
| `frontend/lib/gemini/config/gateway-registry.ts` | Registro de gateways disponibles |

### Gateway de Leads

| Archivo | Descripcion |
|---------|-------------|
| `frontend/lib/gemini/gateways/leads/gateway.ts` | Gateway principal de leads |
| `frontend/lib/gemini/gateways/leads/index.ts` | Exports del gateway |
| `frontend/lib/gemini/gateways/leads/tools/buscar-en-siek.ts` | Tool: Buscar cliente en SIEK |
| `frontend/lib/gemini/gateways/leads/tools/analizar-requerimiento.ts` | Tool: Clasificar requerimiento |
| `frontend/lib/gemini/gateways/leads/tools/buscar-info-empresa.ts` | Tool: Buscar RUC/sector en web |

### API Routes (Endpoints HTTP)

| Archivo | Endpoint | Descripcion |
|---------|----------|-------------|
| `frontend/app/api/gemini/orchestrator/route.ts` | POST /api/gemini/orchestrator | Endpoint principal del orchestrator |
| `frontend/app/api/gemini/buscar-ruc/route.ts` | POST /api/gemini/buscar-ruc | Busqueda web con Gemini (google_search) |

---

## Tipos e Interfaces Principales

### Configuracion de Gemini

```typescript
interface GeminiConfig {
  model: string;           // "gemini-2.0-flash-exp"
  apiKey: string;          // process.env.GOOGLE_API
  temperature?: number;    // 0.7 (default)
  maxOutputTokens?: number; // 2048 (default)
  topP?: number;           // 0.95 (default)
  topK?: number;           // 40 (default)
}
```

### Declaracion de Funcion (para Function Calling)

```typescript
interface FunctionDeclaration {
  name: string;
  description: string;
  parameters: {
    type: "object";
    properties: Record<string, PropertyDefinition>;
    required?: string[];
  };
}

interface PropertyDefinition {
  type: "string" | "number" | "boolean" | "object" | "array";
  description: string;
  enum?: string[];
}
```

### Respuesta del Orchestrator

```typescript
interface OrchestratorResponse {
  success: boolean;
  response: string;                    // Respuesta final de Gemini
  gatewaysCalled?: string[];           // ["gateway_leads"]
  functionsCalled?: FunctionCall[];    // Funciones ejecutadas con resultados
  conversationHistory: Content[];      // Historial para continuar conversacion
  metadata?: {
    totalTokens?: number;
    executionTime?: number;
    iterations?: number;
  };
  error?: string;
}
```

### Resultados de Tools

```typescript
// Resultado de buscar_en_siek
interface BuscarEnSIEKResult {
  success: boolean;
  encontrado: boolean;
  data?: ClienteSIEK;
  mensaje?: string;
}

interface ClienteSIEK {
  TipoDocumento: string;
  NumeroDocumento: string;
  RazonSocial: string;
  Segmento: string;
  AsesorAsignado: string;
  Departamento: string;
  Provincia: string;
  Distrito: string;
}

// Resultado de analizar_requerimiento
interface AnalizarRequerimientoResult {
  success: boolean;
  tipo_requerimiento: "compra_producto" | "servicio_tecnico";
  confianza: "alta" | "media" | "baja";
  keywords: string[];
  razonamiento: string;
}

// Resultado de buscar_info_empresa
interface BuscarInfoEmpresaResult {
  success: boolean;
  ruc: string | null;
  sector_rubro: string | null;
  razon_social_completa: string | null;
  confianza: "alta" | "media" | "baja";
  fuente: "web" | "inferencia" | "no_encontrado";
}
```

---

## Flujo de Function Calling

```
1. Usuario envia mensaje
   |
   v
2. Orchestrator construye request para Gemini API
   - Incluye: mensaje, historial, declaraciones de funciones
   |
   v
3. Gemini responde con:
   - Texto directo, O
   - Llamadas a funciones (functionCall)
   |
   v
4. Si hay functionCall:
   a. Orchestrator busca gateway que tiene esa funcion
   b. Ejecuta la funcion con los parametros
   c. Agrega resultado (functionResponse) al historial
   d. Vuelve a llamar a Gemini con el resultado
   |
   v
5. Loop continua hasta que Gemini responde solo con texto
   |
   v
6. Retorna respuesta final + funciones ejecutadas + historial
```

---

## Funciones Disponibles (Tools)

### 1. buscar_en_siek

**Proposito:** Buscar un cliente en la base de datos SIEK por RUC/DNI.

**Parametros:**
```json
{
  "ruc": "20123456789"
}
```
- ruc: 11 digitos (RUC) o 8 digitos (DNI)

**Respuesta:**
```json
{
  "success": true,
  "encontrado": true,
  "data": {
    "TipoDocumento": "RUC",
    "NumeroDocumento": "20123456789",
    "RazonSocial": "EMPRESA ABC S.A.C.",
    "Segmento": "CORPORATIVO",
    "AsesorAsignado": "ROJAS CAMPUSANO, XIMENA",
    "Departamento": "LIMA",
    "Provincia": "LIMA",
    "Distrito": "MIRAFLORES"
  },
  "mensaje": "Cliente encontrado: EMPRESA ABC S.A.C."
}
```

**Implementacion:**
- Llama a API externa: `https://apisiek.grupokossodo.com/mkt/obtener-cliente/{ruc}`
- Header: `API-Key: {API_KEY_KSSD}`

---

### 2. analizar_requerimiento

**Proposito:** Clasificar un texto de requerimiento como compra de producto o servicio tecnico.

**Parametros:**
```json
{
  "texto_requerimiento": "Necesito cotizacion de balanzas analiticas",
  "empresa_nombre": "Laboratorio XYZ",
  "origen": "web"
}
```
- texto_requerimiento: REQUERIDO
- empresa_nombre: opcional
- origen: opcional

**Respuesta:**
```json
{
  "success": true,
  "tipo_requerimiento": "compra_producto",
  "confianza": "alta",
  "keywords": [],
  "razonamiento": "El cliente solicita cotizacion de productos (balanzas)"
}
```

**Implementacion:**
- Llama directamente a Gemini API
- Usa prompt estructurado para clasificacion
- Retorna JSON parseado

---

### 3. buscar_info_empresa

**Proposito:** Buscar RUC y sector de una empresa usando busqueda web con Gemini.

**Parametros:**
```json
{
  "nombre_empresa": "Minera Los Andes",
  "departamento": "Arequipa",
  "contexto": "mineria de cobre"
}
```
- nombre_empresa: REQUERIDO
- departamento: opcional
- contexto: opcional

**Respuesta:**
```json
{
  "success": true,
  "ruc": "20456789012",
  "sector_rubro": "Mineria",
  "razon_social_completa": "MINERA LOS ANDES S.A.C.",
  "confianza": "alta",
  "fuente": "web"
}
```

**Implementacion:**
- Llama a `/api/gemini/buscar-ruc`
- Usa Gemini con `google_search` tool (grounding)
- Sintaxis para Gemini 2.0+: `tools: [{ google_search: {} }]`

---

## Configuracion de Gemini API

### Variables de Entorno

```bash
GOOGLE_API=tu_api_key_de_gemini
API_KEY_KSSD=tu_api_key_de_siek
NEXT_PUBLIC_APP_URL=https://tu-dominio.com
```

### Modelo Recomendado

```
gemini-2.0-flash-exp
```

### Payload para Gemini API

```json
{
  "contents": [
    { "role": "user", "parts": [{ "text": "mensaje" }] },
    { "role": "model", "parts": [{ "functionCall": {...} }] },
    { "role": "function", "parts": [{ "functionResponse": {...} }] }
  ],
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": "buscar_en_siek",
          "description": "Busca informacion de un cliente...",
          "parameters": {
            "type": "object",
            "properties": {
              "ruc": { "type": "string", "description": "..." }
            },
            "required": ["ruc"]
          }
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 0.7,
    "topP": 0.95,
    "topK": 40,
    "maxOutputTokens": 2048
  },
  "systemInstruction": {
    "parts": [{ "text": "Instrucciones del sistema..." }]
  }
}
```

### URL de Gemini API

```
https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={API_KEY}
```

---

## System Instruction (Prompt del Sistema)

```
ERES UN AGENTE AUTOMATICO DE ANALISIS DE LEADS.

REGLAS ESTRICTAS QUE DEBES SEGUIR SIEMPRE:

1. SI EL MENSAJE CONTIENE "RUC del lead: [numero]" -> DEBES LLAMAR INMEDIATAMENTE a buscar_en_siek con ese RUC
2. SI EL MENSAJE CONTIENE "Empresa: [nombre]" Y NO hay RUC -> DEBES LLAMAR a buscar_info_empresa con ese nombre
3. SI buscar_en_siek retorna encontrado=false -> DEBES LLAMAR a buscar_info_empresa con el nombre de empresa
4. SI OBTIENES UN RUC de buscar_info_empresa -> DEBES LLAMAR a buscar_en_siek con ese RUC
5. SI EL MENSAJE CONTIENE "Requerimiento:" -> DEBES LLAMAR a analizar_requerimiento con ese texto

FLUJO CON RUC EXISTENTE:
1. Usuario proporciona RUC -> buscar_en_siek(RUC)
2. Si encontrado=false -> buscar_info_empresa(empresa, contexto: "RUC conocido: XXXXXXXXXXX")
3. Presentar toda la informacion encontrada

FLUJO SIN RUC:
1. Usuario proporciona nombre empresa -> buscar_info_empresa(nombre)
2. Si obtiene RUC -> buscar_en_siek(RUC)
3. Presentar toda la informacion encontrada

Responde en espanol de forma clara y concisa.
```

---

## Adaptacion a Python/Flask

### Estructura de Archivos Sugerida

```
backend/
+-- gemini/
|   +-- __init__.py
|   +-- config.py                  # Configuracion de Gemini
|   +-- core/
|   |   +-- __init__.py
|   |   +-- types.py               # Clases/TypedDict para tipos
|   |   +-- base_gateway.py        # Clase base para gateways
|   |   +-- orchestrator.py        # Orquestador principal
|   +-- gateways/
|       +-- leads/
|           +-- __init__.py
|           +-- gateway.py         # GatewayLeads
|           +-- tools/
|               +-- __init__.py
|               +-- buscar_en_siek.py
|               +-- analizar_requerimiento.py
|               +-- buscar_info_empresa.py
+-- routes/
    +-- gemini_routes.py           # Endpoints Flask
```

### Ejemplo de Implementacion en Python

```python
# gemini/config.py
import os

GEMINI_CONFIG = {
    "model": "gemini-2.0-flash-exp",
    "api_key": os.getenv("GOOGLE_API", ""),
    "temperature": 0.7,
    "max_output_tokens": 2048,
    "top_p": 0.95,
    "top_k": 40,
}
```

```python
# gemini/core/orchestrator.py
import requests
from typing import List, Dict, Any

class GatewayOrchestrator:
    def __init__(self, gateways: List, config: Dict):
        self.gateways = {g.get_gateway_name(): g for g in gateways}
        self.config = config

    def chat(self, message: str, system_instruction: str = None) -> Dict[str, Any]:
        contents = [{"role": "user", "parts": [{"text": message}]}]
        functions_called = []

        for iteration in range(10):  # max iterations
            response = self._call_gemini_api(contents, system_instruction)

            # Extraer function calls
            function_calls = self._extract_function_calls(response)

            if not function_calls:
                # No mas function calls, retornar respuesta final
                return {
                    "success": True,
                    "response": self._extract_text(response),
                    "functions_called": functions_called,
                }

            # Ejecutar funciones
            function_responses = []
            for fc in function_calls:
                gateway = self._find_gateway_for_function(fc["name"])
                result = gateway.execute(fc["name"], fc["args"])
                functions_called.append({**fc, "result": result})
                function_responses.append({
                    "name": fc["name"],
                    "response": result,
                })

            # Agregar respuestas al historial
            contents.append({
                "role": "function",
                "parts": [{"functionResponse": fr} for fr in function_responses]
            })

        return {"success": False, "error": "Max iterations exceeded"}

    def _call_gemini_api(self, contents, system_instruction):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config['model']}:generateContent?key={self.config['api_key']}"

        payload = {
            "contents": contents,
            "tools": [{"functionDeclarations": self._get_all_function_declarations()}],
            "generationConfig": {
                "temperature": self.config["temperature"],
                "topP": self.config["top_p"],
                "topK": self.config["top_k"],
                "maxOutputTokens": self.config["max_output_tokens"],
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        response = requests.post(url, json=payload)
        return response.json()

    def _extract_function_calls(self, response):
        """Extrae function calls de la respuesta de Gemini"""
        try:
            parts = response["candidates"][0]["content"]["parts"]
            return [p["functionCall"] for p in parts if "functionCall" in p]
        except:
            return []

    def _extract_text(self, response):
        """Extrae texto de la respuesta de Gemini"""
        try:
            parts = response["candidates"][0]["content"]["parts"]
            texts = [p["text"] for p in parts if "text" in p]
            return "\n".join(texts)
        except:
            return ""

    def _find_gateway_for_function(self, function_name):
        """Encuentra el gateway que tiene una funcion especifica"""
        for gateway in self.gateways.values():
            if gateway.has_action(function_name):
                return gateway
        return None

    def _get_all_function_declarations(self):
        """Obtiene todas las declaraciones de funciones de todos los gateways"""
        declarations = []
        for gateway in self.gateways.values():
            declarations.extend(gateway.get_function_declarations())
        return declarations
```

```python
# gemini/core/base_gateway.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseGateway(ABC):
    @abstractmethod
    def get_gateway_name(self) -> str:
        """Retorna el nombre unico del gateway"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Retorna la descripcion del gateway"""
        pass

    @abstractmethod
    def get_function_declarations(self) -> List[Dict]:
        """Retorna las declaraciones de funciones para Gemini"""
        pass

    @abstractmethod
    def execute_action(self, action: str, params: Dict) -> Any:
        """Ejecuta una accion especifica del gateway"""
        pass

    def has_action(self, action: str) -> bool:
        """Verifica si el gateway tiene una accion"""
        declarations = self.get_function_declarations()
        return any(d["name"] == action for d in declarations)

    def execute(self, action: str, params: Dict) -> Any:
        """Ejecuta una accion con validacion"""
        if not self.has_action(action):
            return {"success": False, "error": f"Accion no encontrada: {action}"}
        try:
            return self.execute_action(action, params)
        except Exception as e:
            return {"success": False, "error": str(e)}
```

```python
# gemini/gateways/leads/gateway.py
from ...core.base_gateway import BaseGateway
from .tools.buscar_en_siek import buscar_en_siek
from .tools.analizar_requerimiento import analizar_requerimiento
from .tools.buscar_info_empresa import buscar_info_empresa

class GatewayLeads(BaseGateway):
    def get_gateway_name(self) -> str:
        return "gateway_leads"

    def get_description(self) -> str:
        return "Gateway para gestion y analisis de leads de ventas"

    def get_function_declarations(self):
        return [
            {
                "name": "buscar_en_siek",
                "description": "Busca informacion de un cliente en la base de datos SIEK usando su RUC (11 digitos) o DNI (8 digitos).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ruc": {
                            "type": "string",
                            "description": "Numero de RUC (11 digitos) o DNI (8 digitos)"
                        }
                    },
                    "required": ["ruc"]
                }
            },
            {
                "name": "analizar_requerimiento",
                "description": "Analiza un texto de requerimiento para clasificarlo como compra_producto o servicio_tecnico",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "texto_requerimiento": {
                            "type": "string",
                            "description": "Texto del requerimiento a analizar"
                        },
                        "empresa_nombre": {
                            "type": "string",
                            "description": "Nombre de la empresa (opcional)"
                        },
                        "origen": {
                            "type": "string",
                            "description": "Origen del lead (opcional)"
                        }
                    },
                    "required": ["texto_requerimiento"]
                }
            },
            {
                "name": "buscar_info_empresa",
                "description": "Busca RUC y sector de una empresa usando busqueda web con Gemini",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombre_empresa": {
                            "type": "string",
                            "description": "Nombre de la empresa a buscar"
                        },
                        "departamento": {
                            "type": "string",
                            "description": "Departamento de Peru (opcional)"
                        },
                        "contexto": {
                            "type": "string",
                            "description": "Contexto adicional (opcional)"
                        }
                    },
                    "required": ["nombre_empresa"]
                }
            }
        ]

    def execute_action(self, action: str, params: dict):
        if action == "buscar_en_siek":
            return buscar_en_siek(params["ruc"])
        elif action == "analizar_requerimiento":
            return analizar_requerimiento(
                params["texto_requerimiento"],
                params.get("empresa_nombre"),
                params.get("origen")
            )
        elif action == "buscar_info_empresa":
            return buscar_info_empresa(
                params["nombre_empresa"],
                params.get("departamento"),
                params.get("contexto")
            )
        else:
            raise ValueError(f"Accion desconocida: {action}")
```

```python
# gemini/gateways/leads/tools/buscar_en_siek.py
import os
import requests
import re

def buscar_en_siek(ruc: str) -> dict:
    """Busca un cliente en la API SIEK"""

    # Limpiar RUC (solo numeros)
    ruc_limpio = re.sub(r'\D', '', ruc)

    # Validar longitud
    if len(ruc_limpio) != 11 and len(ruc_limpio) != 8:
        return {
            "success": False,
            "encontrado": False,
            "mensaje": "RUC/DNI invalido. RUC debe tener 11 digitos, DNI debe tener 8 digitos"
        }

    api_key = os.getenv("API_KEY_KSSD")
    if not api_key:
        return {
            "success": False,
            "encontrado": False,
            "mensaje": "API Key no configurada"
        }

    try:
        response = requests.get(
            f"https://apisiek.grupokossodo.com/mkt/obtener-cliente/{ruc_limpio}",
            headers={
                "Accept": "application/json",
                "API-Key": api_key
            }
        )

        if response.status_code == 404:
            return {
                "success": True,
                "encontrado": False,
                "mensaje": f"Cliente con RUC/DNI {ruc_limpio} no encontrado en base SIEK"
            }

        if not response.ok:
            return {
                "success": False,
                "encontrado": False,
                "mensaje": f"Error al consultar SIEK: HTTP {response.status_code}"
            }

        data = response.json()
        cliente_data = data[0] if isinstance(data, list) and len(data) > 0 else data

        if not cliente_data:
            return {
                "success": True,
                "encontrado": False,
                "mensaje": f"Cliente con RUC/DNI {ruc_limpio} no encontrado en base SIEK"
            }

        return {
            "success": True,
            "encontrado": True,
            "data": cliente_data,
            "mensaje": f"Cliente encontrado: {cliente_data.get('RazonSocial', '')}"
        }

    except Exception as e:
        return {
            "success": False,
            "encontrado": False,
            "mensaje": str(e)
        }
```

```python
# gemini/gateways/leads/tools/buscar_info_empresa.py
import os
import requests

def buscar_info_empresa(nombre_empresa: str, departamento: str = None, contexto: str = None) -> dict:
    """Busca RUC y sector de una empresa usando Gemini con Google Search"""

    api_key = os.getenv("GOOGLE_API")
    if not api_key:
        return {
            "success": False,
            "ruc": None,
            "sector_rubro": None,
            "razon_social_completa": None,
            "confianza": "baja",
            "fuente": "no_encontrado",
            "error": "API Key de Gemini no configurada"
        }

    # Construir prompt
    prompt = f'Encuentra el numero de RUC de la empresa "{nombre_empresa}"'
    if departamento:
        prompt += f" ubicada en {departamento}, Peru"
    else:
        prompt += " en Peru"

    if contexto:
        prompt += f". Contexto adicional: {contexto}"

    prompt += ". Tambien identifica su sector o rubro principal."
    prompt += ' Responde UNICAMENTE con formato JSON: {"ruc": "numero_o_null", "sector_rubro": "sector_o_null", "razon_social": "razon_social_o_null"}'

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 500
            },
            "tools": [{"google_search": {}}]  # Sintaxis para Gemini 2.0+
        }

        response = requests.post(url, json=payload)

        if not response.ok:
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
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        # Limpiar markdown si existe
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "").strip()
        elif "```" in text:
            text = text.replace("```", "").strip()

        import json
        parsed = json.loads(text)

        return {
            "success": True,
            "ruc": parsed.get("ruc"),
            "sector_rubro": parsed.get("sector_rubro"),
            "razon_social_completa": parsed.get("razon_social"),
            "confianza": "alta" if parsed.get("ruc") and parsed.get("sector_rubro") else "media",
            "fuente": "web"
        }

    except Exception as e:
        return {
            "success": False,
            "ruc": None,
            "sector_rubro": None,
            "razon_social_completa": None,
            "confianza": "baja",
            "fuente": "no_encontrado",
            "error": str(e)
        }
```

---

## Flujo para Procesamiento Automatico de Leads

Cuando un lead nuevo llega al sistema:

```
1. Lead insertado en tabla WIX
   |
   v
2. Llamar a endpoint de procesamiento:
   POST /api/gemini/orchestrator
   Body: {
     "message": "Analiza este lead:\n- Empresa: {empresa}\n- RUC del lead: {ruc_dni}\n- Requerimiento: {requerimiento}",
     "context": {
       "leadId": 123,
       "empresa": "Empresa ABC",
       "requerimiento": "Necesito cotizacion..."
     }
   }
   |
   v
3. Gemini ejecuta automaticamente:
   a. buscar_en_siek(ruc) -> Cliente existe?
   b. Si no existe -> buscar_info_empresa(empresa)
   c. analizar_requerimiento(texto)
   |
   v
4. Procesar respuesta:
   - Si cliente en SIEK -> siek_cliente = 2
   - Si datos IA -> siek_cliente = 1, guardar ia_cliente_*
   - Si nada -> siek_cliente = 0
   |
   v
5. UPDATE lead SET siek_cliente, ia_cliente_doc, ia_cliente_sector, ia_cliente_razon_social
```

---

## Variables de Entorno Requeridas

```bash
# API de Google Gemini
GOOGLE_API=AIza...

# API de SIEK (para buscar clientes)
API_KEY_KSSD=tu_api_key

# URL base de la aplicacion
NEXT_PUBLIC_APP_URL=https://tu-dominio.com
```

---

## Endpoints HTTP

### POST /api/gemini/orchestrator

**Request:**
```json
{
  "message": "Analiza este lead...",
  "conversationHistory": [],
  "context": {
    "leadId": 123,
    "empresa": "Empresa ABC"
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "He encontrado la informacion del cliente...",
  "gatewaysCalled": ["gateway_leads"],
  "functionsCalled": [
    {
      "name": "buscar_en_siek",
      "args": { "ruc": "20123456789" },
      "result": { "success": true, "encontrado": true, "data": {...} }
    }
  ],
  "conversationHistory": [...]
}
```

### POST /api/gemini/buscar-ruc

**Request:**
```json
{
  "nombreEmpresa": "Minera Los Andes",
  "departamento": "Arequipa",
  "contexto": "mineria de cobre"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ruc": "20456789012",
    "sector_rubro": "Mineria",
    "razon_social": "MINERA LOS ANDES S.A.C."
  }
}
```

---

## Resumen de Rutas de Archivos

```
frontend/
+-- lib/
|   +-- gemini/
|       +-- core/
|       |   +-- types.ts              # Tipos TypeScript
|       |   +-- base-gateway.ts       # Clase base abstracta
|       |   +-- orchestrator.ts       # Orquestador principal
|       +-- config/
|       |   +-- gemini-config.ts      # Config de Gemini
|       |   +-- gateway-registry.ts   # Registro de gateways
|       +-- gateways/
|           +-- leads/
|               +-- gateway.ts        # Gateway de leads
|               +-- index.ts          # Exports
|               +-- tools/
|                   +-- buscar-en-siek.ts
|                   +-- analizar-requerimiento.ts
|                   +-- buscar-info-empresa.ts
+-- app/
|   +-- api/
|       +-- gemini/
|           +-- orchestrator/
|           |   +-- route.ts          # POST /api/gemini/orchestrator
|           +-- buscar-ruc/
|               +-- route.ts          # POST /api/gemini/buscar-ruc
+-- components/
    +-- ventas/
        +-- ClienteDataModal.tsx      # Modal que usa el orchestrator
        +-- LeadsTable.tsx            # Tabla con boton AUTO
        +-- LeadDetailModal.tsx       # Modal de detalle del lead
```

---

## Notas para Migracion a Python

1. **Gemini SDK:** Puedes usar `google-generativeai` de Python, pero la API REST directa es mas flexible para function calling.

2. **Tipos:** Usa `TypedDict` o `dataclasses` para los tipos en Python.

3. **Async:** Considera usar `aiohttp` para llamadas async a Gemini API.

4. **Logging:** Reemplaza `console.log` por el modulo `logging` de Python.

5. **Validacion:** Usa `pydantic` para validar parametros de entrada.

6. **Google Search en Gemini 2.0+:**
   ```python
   tools = [{"google_search": {}}]  # Sintaxis para Gemini 2.0+
   ```
