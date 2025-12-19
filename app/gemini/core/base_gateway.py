"""
BaseGateway - Clase base abstracta para todos los gateways

Todos los gateways deben heredar de esta clase e implementar
los metodos abstractos.

Basado en la arquitectura del sistema original TypeScript
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

try:
    from app.gemini.core.types import FunctionDeclaration, GatewayInfo, GatewayContext
except ImportError:
    from gemini.core.types import FunctionDeclaration, GatewayInfo, GatewayContext


class Logger:
    """Logger simple para los gateways"""

    def __init__(self, gateway_name: str):
        self.gateway_name = gateway_name

    def info(self, message: str, *args):
        print(f"[{self.gateway_name}] {message}", *args)

    def warn(self, message: str, *args):
        print(f"[{self.gateway_name}] WARNING: {message}", *args)

    def error(self, message: str, *args):
        print(f"[{self.gateway_name}] ERROR: {message}", *args)

    def debug(self, message: str, *args):
        print(f"[{self.gateway_name}] DEBUG: {message}", *args)


class BaseGateway(ABC):
    """Clase base abstracta para gateways"""

    def __init__(self, context: Optional[GatewayContext] = None):
        self.context = context
        self.logger = Logger(self.get_gateway_name())

    # ============================================================================
    # METODOS ABSTRACTOS (deben ser implementados por cada gateway)
    # ============================================================================

    @abstractmethod
    def get_gateway_name(self) -> str:
        """
        Retorna el nombre unico del gateway
        Ejemplo: "gateway_leads", "gateway_ventas"
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Retorna la descripcion del gateway
        Ejemplo: "Gateway para gestion de leads y analisis de requerimientos"
        """
        pass

    @abstractmethod
    def get_function_declarations(self) -> List[FunctionDeclaration]:
        """
        Retorna las declaraciones de funciones disponibles en este gateway
        Estas funciones seran expuestas a Gemini para Function Calling
        """
        pass

    @abstractmethod
    def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        """
        Ejecuta una accion especifica del gateway

        Args:
            action: Nombre de la accion a ejecutar
            params: Parametros de la accion

        Returns:
            Resultado de la ejecucion
        """
        pass

    # ============================================================================
    # METODOS PUBLICOS (implementados por la clase base)
    # ============================================================================

    def get_info(self) -> GatewayInfo:
        """Retorna informacion sobre el gateway"""
        declarations = self.get_function_declarations()

        return {
            "name": self.get_gateway_name(),
            "description": self.get_description(),
            "actions": [d["name"] for d in declarations],
            "totalActions": len(declarations)
        }

    def has_action(self, action: str) -> bool:
        """
        Valida que una accion exista en el gateway

        Args:
            action: Nombre de la accion a validar

        Returns:
            True si la accion existe
        """
        declarations = self.get_function_declarations()
        return any(d["name"] == action for d in declarations)

    def validate_params(self, action: str, params: Dict[str, Any]) -> bool:
        """
        Valida parametros contra la declaracion de una funcion

        Args:
            action: Nombre de la accion
            params: Parametros a validar

        Returns:
            True si los parametros son validos
        """
        declarations = self.get_function_declarations()
        declaration = next((d for d in declarations if d["name"] == action), None)

        if not declaration:
            self.logger.error(f"Accion no encontrada: {action}")
            return False

        # Validar parametros requeridos
        required = declaration.get("parameters", {}).get("required", [])
        for param in required:
            if param not in params:
                self.logger.error(f"Parametro requerido faltante: {param}")
                return False

        return True

    def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """
        Ejecuta una accion con validacion y manejo de errores

        Args:
            action: Nombre de la accion
            params: Parametros de la accion

        Returns:
            Resultado de la ejecucion
        """
        self.logger.info(f"Ejecutando accion: {action}", params)

        # Validar que la accion exista
        if not self.has_action(action):
            error = f"Accion no encontrada en {self.get_gateway_name()}: {action}"
            self.logger.error(error)
            return {"success": False, "error": error}

        # Validar parametros
        if not self.validate_params(action, params):
            error = f"Parametros invalidos para accion: {action}"
            self.logger.error(error)
            return {"success": False, "error": error}

        # Ejecutar accion
        try:
            result = self.execute_action(action, params)
            self.logger.info(f"Accion ejecutada exitosamente: {action}")
            return result
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Error ejecutando accion {action}: {error_message}")
            return {"success": False, "error": error_message}

    def set_context(self, context: GatewayContext) -> None:
        """Actualiza el contexto del gateway"""
        self.context = context

    def get_context(self) -> Optional[GatewayContext]:
        """Obtiene el contexto actual"""
        return self.context
