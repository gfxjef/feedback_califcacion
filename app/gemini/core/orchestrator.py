"""
GatewayOrchestrator - Orquestador principal del sistema Gemini

Coordina multiples gateways y maneja la comunicacion con Gemini API
Implementa el patron Orchestrator para sistemas multi-dominio

Basado en la arquitectura del sistema original TypeScript
"""

import time
import requests
from typing import List, Dict, Any, Optional

try:
    from app.gemini.core.base_gateway import BaseGateway
    from app.gemini.core.types import (
        Content, FunctionCall, FunctionResponse,
        OrchestratorResponse, OrchestratorInfo, GeminiConfig
    )
    from app.gemini.config import GEMINI_CONFIG, SYSTEM_INSTRUCTION
except ImportError:
    from gemini.core.base_gateway import BaseGateway
    from gemini.core.types import (
        Content, FunctionCall, FunctionResponse,
        OrchestratorResponse, OrchestratorInfo, GeminiConfig
    )
    from gemini.config import GEMINI_CONFIG, SYSTEM_INSTRUCTION


class GatewayOrchestrator:
    """Orquestador de gateways con integracion a Gemini API"""

    def __init__(self, gateways: List[BaseGateway], config: Optional[Dict] = None):
        self.gateways: Dict[str, BaseGateway] = {}
        self.config = config or GEMINI_CONFIG
        self.generation_config = {
            "temperature": self.config.get("temperature", 0.7),
            "topP": self.config.get("top_p", 0.95),
            "topK": self.config.get("top_k", 40),
            "maxOutputTokens": self.config.get("max_output_tokens", 2048),
        }

        # Registrar gateways
        for gateway in gateways:
            self.register_gateway(gateway)

        print(f"[Orchestrator] Inicializado con {len(self.gateways)} gateway(s)")

    # ============================================================================
    # GESTION DE GATEWAYS
    # ============================================================================

    def register_gateway(self, gateway: BaseGateway) -> None:
        """Registra un nuevo gateway"""
        name = gateway.get_gateway_name()

        if name in self.gateways:
            print(f"[Orchestrator] WARNING: Gateway ya registrado: {name}")
            return

        self.gateways[name] = gateway
        print(f"[Orchestrator] Gateway registrado: {name}")

    def get_gateway(self, name: str) -> Optional[BaseGateway]:
        """Obtiene un gateway por nombre"""
        return self.gateways.get(name)

    def get_all_function_declarations(self) -> List[Dict]:
        """Obtiene todas las declaraciones de funciones de todos los gateways"""
        declarations = []

        for gateway in self.gateways.values():
            gateway_declarations = gateway.get_function_declarations()

            for declaration in gateway_declarations:
                declarations.append({
                    "name": declaration["name"],
                    "description": declaration["description"],
                    "parameters": declaration["parameters"],
                })

        return declarations

    # ============================================================================
    # COMUNICACION CON GEMINI
    # ============================================================================

    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Content]] = None,
        max_iterations: int = 10,
        system_instruction: Optional[str] = None
    ) -> OrchestratorResponse:
        """
        Procesa una consulta del usuario usando Gemini Function Calling

        Args:
            message: Mensaje del usuario
            conversation_history: Historial de conversacion previo
            max_iterations: Maximo de iteraciones del loop
            system_instruction: Instruccion del sistema personalizada

        Returns:
            OrchestratorResponse con el resultado
        """
        start_time = time.time()

        print(f"[Orchestrator] Procesando consulta: {message[:100]}...")

        try:
            # Preparar contenido inicial
            contents: List[Content] = [
                *(conversation_history or []),
                {
                    "role": "user",
                    "parts": [{"text": message}]
                }
            ]

            functions_called: List[FunctionCall] = []
            gateways_called: List[str] = []
            iterations = 0

            # Loop de Function Calling (maximo max_iterations iteraciones)
            while iterations < max_iterations:
                iterations += 1

                # Llamar a Gemini API
                response = self._call_gemini_api(
                    contents,
                    system_instruction or SYSTEM_INSTRUCTION
                )

                if not response or "candidates" not in response or len(response["candidates"]) == 0:
                    raise Exception("Respuesta vacia de Gemini API")

                candidate = response["candidates"][0]
                content = candidate.get("content", {})

                # Agregar respuesta de Gemini al historial
                contents.append(content)

                # Verificar si hay llamadas a funciones
                parts = content.get("parts", [])
                function_calls = [
                    p["functionCall"] for p in parts
                    if "functionCall" in p
                ]

                if not function_calls:
                    # No hay mas llamadas a funciones, extraer texto final
                    text_parts = [p.get("text", "") for p in parts if "text" in p]
                    final_response = "\n".join(text_parts)

                    execution_time = int((time.time() - start_time) * 1000)
                    print(f"[Orchestrator] Completado en {execution_time}ms")

                    return {
                        "success": True,
                        "response": final_response,
                        "gatewaysCalled": list(set(gateways_called)),
                        "functionsCalled": functions_called,
                        "conversationHistory": contents,
                        "metadata": {
                            "executionTime": execution_time,
                            "iterations": iterations,
                            "totalTokens": response.get("usageMetadata", {}).get("totalTokenCount")
                        }
                    }

                # Ejecutar todas las llamadas a funciones
                function_responses: List[Dict] = []

                for fc in function_calls:
                    function_name = fc.get("name", "")
                    function_args = fc.get("args", {})

                    print(f"[Orchestrator] Ejecutando funcion: {function_name}", function_args)

                    try:
                        # Buscar el gateway que tiene esta funcion
                        gateway = self._find_gateway_for_function(function_name)

                        if not gateway:
                            raise Exception(f"No se encontro gateway para la funcion: {function_name}")

                        gateway_name = gateway.get_gateway_name()
                        if gateway_name not in gateways_called:
                            gateways_called.append(gateway_name)

                        # Ejecutar la funcion
                        result = gateway.execute(function_name, function_args)

                        # Guardar la llamada con su resultado
                        functions_called.append({
                            "name": function_name,
                            "args": function_args,
                            "result": result
                        })

                        function_responses.append({
                            "name": function_name,
                            "response": result
                        })

                    except Exception as e:
                        error_message = str(e)
                        print(f"[Orchestrator] ERROR ejecutando {function_name}: {error_message}")

                        error_result = {
                            "success": False,
                            "error": error_message
                        }

                        # Guardar la llamada fallida con su error
                        functions_called.append({
                            "name": function_name,
                            "args": function_args,
                            "result": error_result
                        })

                        function_responses.append({
                            "name": function_name,
                            "response": error_result
                        })

                # Agregar respuestas de funciones al historial
                contents.append({
                    "role": "function",
                    "parts": [
                        {"functionResponse": fr}
                        for fr in function_responses
                    ]
                })

                # Continuar el loop para que Gemini procese las respuestas

            # Si llegamos aqui, superamos el maximo de iteraciones
            raise Exception(f"Superado el maximo de iteraciones ({max_iterations})")

        except Exception as e:
            error_message = str(e)
            print(f"[Orchestrator] ERROR: {error_message}")

            return {
                "success": False,
                "response": "",
                "error": error_message,
                "conversationHistory": []
            }

    def _call_gemini_api(self, contents: List[Content], system_instruction: str) -> Dict:
        """Llama a la API de Gemini"""
        model = self.config.get("model", "gemini-2.0-flash-exp")
        api_key = self.config.get("api_key", "")

        if not api_key:
            raise Exception("API Key de Gemini no configurada (GOOGLE_API)")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        request_body = {
            "contents": contents,
            "tools": [
                {
                    "functionDeclarations": self.get_all_function_declarations()
                }
            ],
            "generationConfig": self.generation_config
        }

        # Agregar system instruction si esta presente
        if system_instruction:
            request_body["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        response = requests.post(
            url,
            json=request_body,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if not response.ok:
            error_text = response.text
            raise Exception(f"Gemini API error {response.status_code}: {error_text}")

        return response.json()

    def _find_gateway_for_function(self, function_name: str) -> Optional[BaseGateway]:
        """Encuentra el gateway que contiene una funcion especifica"""
        for gateway in self.gateways.values():
            if gateway.has_action(function_name):
                return gateway
        return None

    # ============================================================================
    # INFORMACION Y UTILIDADES
    # ============================================================================

    def get_info(self) -> OrchestratorInfo:
        """Obtiene informacion completa del orchestrator"""
        gateways_info = {}

        for name, gateway in self.gateways.items():
            gateways_info[name] = gateway.get_info()

        return {
            "orchestrator": "GatewayOrchestrator",
            "totalGateways": len(self.gateways),
            "gateways": gateways_info,
            "model": self.config.get("model", "")
        }

    def list_gateways(self) -> List[str]:
        """Lista los nombres de todos los gateways registrados"""
        return list(self.gateways.keys())

    def get_health(self) -> Dict:
        """Verifica el estado del orchestrator"""
        return {
            "status": "healthy" if len(self.gateways) > 0 else "unhealthy",
            "totalGateways": len(self.gateways),
            "model": self.config.get("model", "")
        }
