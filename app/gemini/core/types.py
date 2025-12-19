"""
Tipos e interfaces para el sistema Gemini Orchestrator
Basado en Google Gemini Function Calling API
Adaptado para Python/Flask
"""

from typing import TypedDict, List, Dict, Any, Optional, Literal


# ============================================================================
# TIPOS DE GEMINI API
# ============================================================================

class PropertyDefinition(TypedDict, total=False):
    """Definicion de una propiedad en los parametros de funcion"""
    type: Literal["string", "number", "boolean", "object", "array"]
    description: str
    enum: Optional[List[str]]


class FunctionParameters(TypedDict):
    """Parametros de una funcion"""
    type: Literal["object"]
    properties: Dict[str, PropertyDefinition]
    required: Optional[List[str]]


class FunctionDeclaration(TypedDict):
    """Declaracion de una funcion para Gemini Function Calling"""
    name: str
    description: str
    parameters: FunctionParameters


class FunctionCall(TypedDict, total=False):
    """Llamada a funcion solicitada por Gemini"""
    name: str
    args: Dict[str, Any]
    result: Optional[Any]


class FunctionResponse(TypedDict):
    """Respuesta de una funcion ejecutada"""
    name: str
    response: Any


class Part(TypedDict, total=False):
    """Parte de un mensaje (texto o llamada a funcion)"""
    text: Optional[str]
    functionCall: Optional[FunctionCall]
    functionResponse: Optional[FunctionResponse]


class Content(TypedDict):
    """Contenido de mensaje en conversacion con Gemini"""
    role: Literal["user", "model", "function"]
    parts: List[Part]


# ============================================================================
# TIPOS DEL ORCHESTRATOR
# ============================================================================

class GatewayContext(TypedDict, total=False):
    """Contexto compartido entre gateways"""
    userId: Optional[str]
    sessionId: Optional[str]
    metadata: Optional[Dict[str, Any]]


class GatewayInfo(TypedDict):
    """Informacion de un gateway registrado"""
    name: str
    description: str
    actions: List[str]
    totalActions: int


class OrchestratorInfo(TypedDict):
    """Informacion completa del orchestrator"""
    orchestrator: str
    totalGateways: int
    gateways: Dict[str, GatewayInfo]
    model: str


class ChatOptions(TypedDict, total=False):
    """Opciones para el chat del orchestrator"""
    message: str
    conversationHistory: Optional[List[Content]]
    context: Optional[GatewayContext]
    maxIterations: Optional[int]
    systemInstruction: Optional[str]


class OrchestratorMetadata(TypedDict, total=False):
    """Metadata de la respuesta del orchestrator"""
    totalTokens: Optional[int]
    executionTime: Optional[int]
    iterations: Optional[int]


class OrchestratorResponse(TypedDict, total=False):
    """Respuesta del orchestrator"""
    success: bool
    response: str
    gatewaysCalled: Optional[List[str]]
    functionsCalled: Optional[List[FunctionCall]]
    conversationHistory: List[Content]
    metadata: Optional[OrchestratorMetadata]
    error: Optional[str]


# ============================================================================
# TIPOS DE CONFIGURACION
# ============================================================================

class GeminiConfig(TypedDict, total=False):
    """Configuracion de Gemini API"""
    model: str
    api_key: str
    temperature: Optional[float]
    max_output_tokens: Optional[int]
    top_p: Optional[float]
    top_k: Optional[int]


class GenerationConfig(TypedDict, total=False):
    """Configuracion de generacion de Gemini"""
    temperature: Optional[float]
    topP: Optional[float]
    topK: Optional[int]
    maxOutputTokens: Optional[int]


# ============================================================================
# TIPOS DE GATEWAYS ESPECIFICOS
# ============================================================================

class ClienteSIEK(TypedDict, total=False):
    """Cliente de la API SIEK"""
    TipoDocumento: str
    NumeroDocumento: str
    RazonSocial: str
    Segmento: str
    AsesorAsignado: str
    Departamento: str
    Provincia: str
    Distrito: str
    Filtro01: Optional[str]
    Filtro02: Optional[str]
    Filtro03: Optional[str]


class BuscarEnSIEKResult(TypedDict, total=False):
    """Resultado de busqueda en SIEK"""
    success: bool
    encontrado: bool
    data: Optional[ClienteSIEK]
    mensaje: Optional[str]


class AnalizarRequerimientoResult(TypedDict, total=False):
    """Resultado de analisis de requerimiento"""
    success: bool
    tipo_requerimiento: Literal["compra_producto", "servicio_tecnico"]
    confianza: Literal["alta", "media", "baja"]
    keywords: List[str]
    razonamiento: str
    error: Optional[str]


class BuscarInfoEmpresaResult(TypedDict, total=False):
    """Resultado de busqueda de informacion de empresa"""
    success: bool
    ruc: Optional[str]
    sector_rubro: Optional[str]
    razon_social_completa: Optional[str]
    confianza: Literal["alta", "media", "baja"]
    fuente: Literal["web", "inferencia", "no_encontrado"]
    error: Optional[str]


class LeadData(TypedDict, total=False):
    """Datos de un lead"""
    id: int
    nombre_apellido: str
    empresa: str
    telefono2: str
    ruc_dni: str
    correo: str
    treq_requerimiento: str
    origen: str
    observacion: Optional[str]
