"""
GatewayLeads - Gateway para gestion de leads

Proporciona herramientas para:
- Buscar informacion de clientes en SIEK
- Analizar requerimientos (compra vs servicio tecnico)
- Buscar informacion de empresas (RUC, sector)

Este gateway orquesta el flujo completo de analisis de leads
usando Google Gemini para tomar decisiones inteligentes.

Basado en el codigo original TypeScript
"""

from typing import List, Dict, Any

try:
    from app.gemini.core.base_gateway import BaseGateway
    from app.gemini.core.types import FunctionDeclaration
    from app.gemini.gateways.leads.tools.buscar_en_siek import buscar_en_siek
    from app.gemini.gateways.leads.tools.analizar_requerimiento import analizar_requerimiento
    from app.gemini.gateways.leads.tools.buscar_info_empresa import buscar_info_empresa
    from app.gemini.config import FUNCTION_DECLARATIONS
except ImportError:
    from gemini.core.base_gateway import BaseGateway
    from gemini.core.types import FunctionDeclaration
    from gemini.gateways.leads.tools.buscar_en_siek import buscar_en_siek
    from gemini.gateways.leads.tools.analizar_requerimiento import analizar_requerimiento
    from gemini.gateways.leads.tools.buscar_info_empresa import buscar_info_empresa
    from gemini.config import FUNCTION_DECLARATIONS


class GatewayLeads(BaseGateway):
    """
    Gateway de Leads

    Permite a Gemini:
    1. Buscar clientes en base SIEK por RUC/DNI
    2. Analizar tipo de requerimiento (compra vs servicio)
    3. Buscar RUC y sector de empresas desconocidas
    """

    def __init__(self):
        super().__init__()

    def get_gateway_name(self) -> str:
        """Nombre unico del gateway"""
        return "gateway_leads"

    def get_description(self) -> str:
        """Descripcion del gateway para Gemini"""
        return (
            "Gateway para gestión y análisis de leads de ventas. "
            "Permite buscar información de clientes en la base SIEK, "
            "analizar requerimientos para clasificarlos, y buscar información "
            "de empresas desconocidas (RUC, sector/rubro) usando búsqueda web."
        )

    def get_function_declarations(self) -> List[FunctionDeclaration]:
        """Declaraciones de funciones para Gemini Function Calling"""
        return FUNCTION_DECLARATIONS

    def execute_action(self, action: str, params: Dict[str, Any]) -> Any:
        """
        Ejecuta una accion del gateway

        Args:
            action: Nombre de la accion a ejecutar
            params: Parametros de la accion

        Returns:
            Resultado de la accion
        """
        print(f"[GatewayLeads] Ejecutando accion: {action}", params)

        if action == "buscar_en_siek":
            return buscar_en_siek(
                ruc=params.get("ruc", "")
            )

        elif action == "analizar_requerimiento":
            return analizar_requerimiento(
                texto_requerimiento=params.get("texto_requerimiento", ""),
                empresa_nombre=params.get("empresa_nombre"),
                origen=params.get("origen")
            )

        elif action == "buscar_info_empresa":
            return buscar_info_empresa(
                nombre_empresa=params.get("nombre_empresa", ""),
                departamento=params.get("departamento"),
                contexto=params.get("contexto")
            )

        else:
            raise ValueError(
                f"Accion desconocida en GatewayLeads: {action}. "
                f"Acciones disponibles: buscar_en_siek, analizar_requerimiento, buscar_info_empresa"
            )
