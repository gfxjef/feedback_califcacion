"""
Core module for Gemini Orchestration
"""

try:
    from app.gemini.core.types import (
        GeminiConfig,
        FunctionDeclaration,
        FunctionCall,
        FunctionResponse,
        OrchestratorResponse,
        BuscarEnSIEKResult,
        AnalizarRequerimientoResult,
        BuscarInfoEmpresaResult
    )
    from app.gemini.core.base_gateway import BaseGateway
    from app.gemini.core.orchestrator import GatewayOrchestrator
except ImportError:
    from gemini.core.types import (
        GeminiConfig,
        FunctionDeclaration,
        FunctionCall,
        FunctionResponse,
        OrchestratorResponse,
        BuscarEnSIEKResult,
        AnalizarRequerimientoResult,
        BuscarInfoEmpresaResult
    )
    from gemini.core.base_gateway import BaseGateway
    from gemini.core.orchestrator import GatewayOrchestrator

__all__ = [
    'GeminiConfig',
    'FunctionDeclaration',
    'FunctionCall',
    'FunctionResponse',
    'OrchestratorResponse',
    'BuscarEnSIEKResult',
    'AnalizarRequerimientoResult',
    'BuscarInfoEmpresaResult',
    'BaseGateway',
    'GatewayOrchestrator'
]
