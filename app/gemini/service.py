"""
Gemini Service - Servicio de alto nivel para analisis automatico de leads

Este servicio es el punto de entrada principal para integrar
el sistema de orquestacion Gemini con los endpoints de leads.

Proporciona una funcion simple: analizar_lead_automatico()
que toma los datos de un lead y retorna el analisis completo.
"""

from typing import Dict, Any, Optional
from datetime import datetime

try:
    from app.gemini.core.orchestrator import GatewayOrchestrator
    from app.gemini.gateways.leads.gateway import GatewayLeads
    from app.gemini.config import GEMINI_CONFIG, SYSTEM_INSTRUCTION
    from app.db import get_db_connection
except ImportError:
    from gemini.core.orchestrator import GatewayOrchestrator
    from gemini.gateways.leads.gateway import GatewayLeads
    from gemini.config import GEMINI_CONFIG, SYSTEM_INSTRUCTION
    from db import get_db_connection


def crear_orchestrator() -> GatewayOrchestrator:
    """Crea una instancia del orchestrator con el gateway de leads"""
    gateway_leads = GatewayLeads()
    return GatewayOrchestrator(
        gateways=[gateway_leads],
        config=GEMINI_CONFIG
    )


def construir_mensaje_lead(lead_data: Dict[str, Any]) -> str:
    """
    Construye el mensaje para enviar a Gemini basado en los datos del lead

    Args:
        lead_data: Datos del lead (empresa, ruc_dni, treq_requerimiento, origen)

    Returns:
        Mensaje formateado para Gemini
    """
    partes = ["Analiza este lead:"]

    # Empresa
    empresa = lead_data.get("empresa", "").strip()
    if empresa:
        partes.append(f"- Empresa: {empresa}")

    # RUC/DNI
    ruc_dni = lead_data.get("ruc_dni", "").strip() if lead_data.get("ruc_dni") else ""
    if ruc_dni:
        partes.append(f"- RUC del lead: {ruc_dni}")

    # Requerimiento
    requerimiento = lead_data.get("treq_requerimiento", "").strip() if lead_data.get("treq_requerimiento") else ""
    if requerimiento:
        partes.append(f"- Requerimiento: {requerimiento}")

    # Origen
    origen = lead_data.get("origen", "").strip() if lead_data.get("origen") else ""
    if origen:
        partes.append(f"- Origen: {origen}")

    return "\n".join(partes)


def procesar_resultados_gemini(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa los resultados del orchestrator y extrae los datos relevantes

    Args:
        response: Respuesta del orchestrator

    Returns:
        Dict con los datos procesados para actualizar en BD
    """
    resultado = {
        "siek_cliente": 0,
        "ia_cliente_doc": None,
        "ia_cliente_sector": None,
        "ia_cliente_razon_social": None,
        "ia_tipo_requerimiento": None,
        "ia_confianza": None,
        "gemini_response": response.get("response", ""),
        "success": response.get("success", False)
    }

    if not response.get("success"):
        resultado["error"] = response.get("error", "Error desconocido")
        return resultado

    # Procesar funciones ejecutadas
    functions_called = response.get("functionsCalled", [])

    for fc in functions_called:
        name = fc.get("name", "")
        result = fc.get("result", {})

        if name == "buscar_en_siek":
            if result.get("encontrado"):
                # Cliente encontrado en SIEK
                resultado["siek_cliente"] = 2
                data = result.get("data", {})
                resultado["ia_cliente_doc"] = data.get("NumeroDocumento")
                resultado["ia_cliente_sector"] = data.get("Segmento")
                resultado["ia_cliente_razon_social"] = data.get("RazonSocial")

        elif name == "buscar_info_empresa":
            if result.get("success") and resultado["siek_cliente"] != 2:
                # Datos encontrados por IA (solo si no hay datos SIEK)
                if result.get("ruc") or result.get("sector_rubro"):
                    resultado["siek_cliente"] = 1
                    resultado["ia_cliente_doc"] = result.get("ruc")
                    resultado["ia_cliente_sector"] = result.get("sector_rubro")
                    resultado["ia_cliente_razon_social"] = result.get("razon_social_completa")
                    resultado["ia_confianza"] = result.get("confianza")

        elif name == "analizar_requerimiento":
            if result.get("success"):
                resultado["ia_tipo_requerimiento"] = result.get("tipo_requerimiento")
                # Solo actualizar confianza si no hay de buscar_info_empresa
                if not resultado["ia_confianza"]:
                    resultado["ia_confianza"] = result.get("confianza")

    return resultado


def actualizar_lead_en_bd(lead_id: int, datos: Dict[str, Any]) -> bool:
    """
    Actualiza el lead en la base de datos con los resultados del analisis

    Args:
        lead_id: ID del lead en la tabla WIX
        datos: Datos a actualizar

    Returns:
        True si se actualizo correctamente
    """
    cnx = get_db_connection()
    if cnx is None:
        print(f"[GeminiService] ERROR: No se pudo conectar a la BD para actualizar lead {lead_id}")
        return False

    try:
        cursor = cnx.cursor()

        # Verificar/agregar columnas si no existen
        columnas_nuevas = [
            ("ia_tipo_requerimiento", "VARCHAR(50)"),
            ("ia_confianza", "VARCHAR(20)"),
            ("ia_procesado", "DATETIME")
        ]

        for col_name, col_type in columnas_nuevas:
            try:
                cursor.execute(f"ALTER TABLE WIX ADD COLUMN {col_name} {col_type} NULL")
                cnx.commit()
                print(f"[GeminiService] Columna {col_name} agregada a tabla WIX")
            except Exception:
                # La columna ya existe
                pass

        # Actualizar el lead
        update_query = """
            UPDATE WIX SET
                siek_cliente = %s,
                ia_cliente_doc = %s,
                ia_cliente_sector = %s,
                ia_cliente_razon_social = %s,
                ia_tipo_requerimiento = %s,
                ia_confianza = %s,
                ia_procesado = %s
            WHERE id = %s
        """

        values = (
            datos.get("siek_cliente", 0),
            datos.get("ia_cliente_doc"),
            datos.get("ia_cliente_sector"),
            datos.get("ia_cliente_razon_social"),
            datos.get("ia_tipo_requerimiento"),
            datos.get("ia_confianza"),
            datetime.now(),
            lead_id
        )

        cursor.execute(update_query, values)
        cnx.commit()

        print(f"[GeminiService] Lead {lead_id} actualizado con datos de IA")
        return True

    except Exception as e:
        print(f"[GeminiService] ERROR al actualizar lead {lead_id}: {e}")
        return False

    finally:
        cursor.close()
        cnx.close()


def analizar_lead_automatico(lead_data: Dict[str, Any], lead_id: int) -> Dict[str, Any]:
    """
    Analiza un lead automaticamente usando Gemini y actualiza la BD

    Esta es la funcion principal que debe llamarse desde los endpoints
    /wix/records y /bd/records despues de insertar el lead.

    Args:
        lead_data: Datos del lead:
            - empresa: Nombre de la empresa
            - ruc_dni: RUC o DNI (opcional)
            - treq_requerimiento: Texto del requerimiento (opcional)
            - origen: Origen del lead (WIX, etc.)
        lead_id: ID del registro en la tabla WIX

    Returns:
        Dict con:
            - success: True si el analisis fue exitoso
            - siek_cliente: 0=no datos, 1=datos IA, 2=datos SIEK
            - ia_cliente_doc: RUC/DNI encontrado
            - ia_cliente_sector: Sector/rubro
            - ia_cliente_razon_social: Razon social
            - ia_tipo_requerimiento: compra_producto o servicio_tecnico
            - ia_confianza: alta, media o baja
            - gemini_response: Respuesta completa de Gemini
            - error: Mensaje de error (si aplica)
    """
    print(f"[GeminiService] Iniciando analisis automatico para lead {lead_id}")
    print(f"[GeminiService] Datos del lead: {lead_data}")

    try:
        # Verificar que hay datos suficientes para analizar
        empresa = lead_data.get("empresa", "").strip() if lead_data.get("empresa") else ""
        ruc_dni = lead_data.get("ruc_dni", "").strip() if lead_data.get("ruc_dni") else ""
        requerimiento = lead_data.get("treq_requerimiento", "").strip() if lead_data.get("treq_requerimiento") else ""

        if not empresa and not ruc_dni and not requerimiento:
            print(f"[GeminiService] Lead {lead_id} sin datos suficientes para analizar")
            return {
                "success": False,
                "error": "Sin datos suficientes para analizar (empresa, ruc_dni o requerimiento requeridos)"
            }

        # Crear orchestrator
        orchestrator = crear_orchestrator()

        # Construir mensaje
        mensaje = construir_mensaje_lead(lead_data)
        print(f"[GeminiService] Mensaje para Gemini: {mensaje}")

        # Ejecutar analisis
        response = orchestrator.chat(
            message=mensaje,
            system_instruction=SYSTEM_INSTRUCTION,
            max_iterations=10
        )

        print(f"[GeminiService] Respuesta del orchestrator: success={response.get('success')}")

        # Procesar resultados
        resultado = procesar_resultados_gemini(response)

        # Actualizar BD
        if resultado.get("success") or resultado.get("siek_cliente") > 0:
            actualizar_lead_en_bd(lead_id, resultado)

        print(f"[GeminiService] Analisis completado para lead {lead_id}: siek_cliente={resultado.get('siek_cliente')}")

        return resultado

    except Exception as e:
        error_msg = str(e)
        print(f"[GeminiService] ERROR en analisis de lead {lead_id}: {error_msg}")

        return {
            "success": False,
            "error": error_msg,
            "siek_cliente": 0,
            "ia_cliente_doc": None,
            "ia_cliente_sector": None,
            "ia_cliente_razon_social": None,
            "ia_tipo_requerimiento": None,
            "ia_confianza": None
        }
