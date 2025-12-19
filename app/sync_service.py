"""
Sync Service - Servicio de sincronizacion de leads con sistema externo

Maneja el envio de leads a un sistema externo y la confirmacion de recepcion.
Incluye manejo de estados: pendiente, enviado, confirmado, error, timeout.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple

try:
    from app.db import get_db_connection
except ImportError:
    from db import get_db_connection


# Configuracion
EXTERNAL_ENDPOINT = os.getenv("SYNC_EXTERNAL_ENDPOINT", "https://httpbin.org/post")  # Ficticio por ahora
SYNC_TIMEOUT_HOURS = int(os.getenv("SYNC_TIMEOUT_HOURS", "24"))
SYNC_ENABLED = os.getenv("SYNC_ENABLED", "true").lower() == "true"


def asegurar_columnas_sync() -> bool:
    """
    Asegura que existan las columnas de sincronizacion en la tabla WIX.
    Retorna True si se ejecuto correctamente.
    """
    cnx = get_db_connection()
    if cnx is None:
        print("[SyncService] ERROR: No se pudo conectar a la BD")
        return False

    try:
        cursor = cnx.cursor()

        columnas = [
            ("sync_status", "VARCHAR(20) DEFAULT 'pendiente'"),
            ("sync_sent_at", "DATETIME NULL"),
            ("sync_confirmed_at", "DATETIME NULL"),
            ("sync_error", "TEXT NULL"),
            ("sync_external_id", "VARCHAR(100) NULL"),
        ]

        for col_name, col_type in columnas:
            try:
                cursor.execute(f"ALTER TABLE WIX ADD COLUMN {col_name} {col_type}")
                cnx.commit()
                print(f"[SyncService] Columna {col_name} agregada a tabla WIX")
            except Exception:
                # La columna ya existe
                pass

        return True

    except Exception as e:
        print(f"[SyncService] ERROR al asegurar columnas: {e}")
        return False

    finally:
        cursor.close()
        cnx.close()


def obtener_lead_completo(record_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene todos los datos de un lead por su ID.
    """
    cnx = get_db_connection()
    if cnx is None:
        return None

    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM WIX WHERE id = %s", (record_id,))
        lead = cursor.fetchone()

        # Convertir datetime a string para JSON
        if lead:
            for key, value in lead.items():
                if isinstance(value, datetime):
                    lead[key] = value.isoformat()

        return lead

    except Exception as e:
        print(f"[SyncService] ERROR al obtener lead {record_id}: {e}")
        return None

    finally:
        cursor.close()
        cnx.close()


def actualizar_estado_sync(
    record_id: int,
    status: str,
    error: Optional[str] = None,
    external_id: Optional[str] = None
) -> bool:
    """
    Actualiza el estado de sincronizacion de un lead.

    Estados validos: pendiente, enviado, confirmado, error, timeout
    """
    cnx = get_db_connection()
    if cnx is None:
        return False

    try:
        cursor = cnx.cursor()

        if status == "enviado":
            cursor.execute("""
                UPDATE WIX SET
                    sync_status = %s,
                    sync_sent_at = NOW(),
                    sync_error = NULL
                WHERE id = %s
            """, (status, record_id))

        elif status == "confirmado":
            cursor.execute("""
                UPDATE WIX SET
                    sync_status = %s,
                    sync_confirmed_at = NOW(),
                    sync_external_id = %s,
                    sync_error = NULL
                WHERE id = %s
            """, (status, external_id, record_id))

        elif status in ["error", "timeout"]:
            cursor.execute("""
                UPDATE WIX SET
                    sync_status = %s,
                    sync_error = %s
                WHERE id = %s
            """, (status, error, record_id))

        else:  # pendiente u otro
            cursor.execute("""
                UPDATE WIX SET sync_status = %s WHERE id = %s
            """, (status, record_id))

        cnx.commit()
        print(f"[SyncService] Lead {record_id} actualizado a estado: {status}")
        return True

    except Exception as e:
        print(f"[SyncService] ERROR al actualizar estado de lead {record_id}: {e}")
        return False

    finally:
        cursor.close()
        cnx.close()


def enviar_lead_a_sistema_externo(record_id: int) -> Dict[str, Any]:
    """
    Envia un lead al sistema externo.

    Returns:
        Dict con:
            - success: bool
            - message: str
            - external_response: dict (si aplica)
    """
    if not SYNC_ENABLED:
        return {
            "success": False,
            "message": "Sincronizacion deshabilitada (SYNC_ENABLED=false)",
            "skipped": True
        }

    # Obtener datos completos del lead
    lead_data = obtener_lead_completo(record_id)

    if not lead_data:
        return {
            "success": False,
            "message": f"Lead {record_id} no encontrado"
        }

    print(f"[SyncService] Enviando lead {record_id} a {EXTERNAL_ENDPOINT}")

    try:
        # Preparar payload
        payload = {
            "source": "feedback_califcacion",
            "timestamp": datetime.now().isoformat(),
            "lead": lead_data
        }

        # Enviar al sistema externo
        response = requests.post(
            EXTERNAL_ENDPOINT,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Source-System": "feedback_califcacion",
                "X-Record-ID": str(record_id)
            },
            timeout=30
        )

        if response.ok:
            # Exito - marcar como enviado
            actualizar_estado_sync(record_id, "enviado")

            print(f"[SyncService] Lead {record_id} enviado exitosamente")

            return {
                "success": True,
                "message": f"Lead {record_id} enviado exitosamente",
                "status_code": response.status_code,
                "external_response": response.json() if response.text else {}
            }
        else:
            # Error HTTP - mantener como pendiente
            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            actualizar_estado_sync(record_id, "pendiente", error=error_msg)

            print(f"[SyncService] ERROR al enviar lead {record_id}: {error_msg}")

            return {
                "success": False,
                "message": error_msg,
                "status_code": response.status_code
            }

    except requests.exceptions.Timeout:
        error_msg = "Timeout al conectar con sistema externo"
        actualizar_estado_sync(record_id, "pendiente", error=error_msg)

        print(f"[SyncService] TIMEOUT al enviar lead {record_id}")

        return {
            "success": False,
            "message": error_msg
        }

    except requests.exceptions.ConnectionError as e:
        error_msg = f"Error de conexion: {str(e)[:100]}"
        actualizar_estado_sync(record_id, "pendiente", error=error_msg)

        print(f"[SyncService] ERROR de conexion al enviar lead {record_id}")

        return {
            "success": False,
            "message": error_msg
        }

    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        actualizar_estado_sync(record_id, "pendiente", error=error_msg)

        print(f"[SyncService] ERROR inesperado al enviar lead {record_id}: {e}")

        return {
            "success": False,
            "message": error_msg
        }


def confirmar_recepcion(record_id: int, external_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Confirma que el sistema externo recibio y proceso el lead.

    Args:
        record_id: ID del lead en nuestra BD
        external_id: ID asignado por el sistema externo (opcional)

    Returns:
        Dict con success y message
    """
    # Verificar que el lead existe
    lead = obtener_lead_completo(record_id)

    if not lead:
        return {
            "success": False,
            "message": f"Lead {record_id} no encontrado"
        }

    # Verificar estado actual
    current_status = lead.get("sync_status", "pendiente")

    if current_status == "confirmado":
        return {
            "success": True,
            "message": f"Lead {record_id} ya estaba confirmado",
            "already_confirmed": True
        }

    # Actualizar a confirmado
    success = actualizar_estado_sync(record_id, "confirmado", external_id=external_id)

    if success:
        print(f"[SyncService] Lead {record_id} confirmado (external_id: {external_id})")
        return {
            "success": True,
            "message": f"Lead {record_id} confirmado exitosamente",
            "external_id": external_id
        }
    else:
        return {
            "success": False,
            "message": f"Error al confirmar lead {record_id}"
        }


def obtener_leads_pendientes(
    status: Optional[str] = None,
    limit: int = 100
) -> Tuple[List[Dict], int]:
    """
    Obtiene leads segun su estado de sincronizacion.

    Args:
        status: Filtrar por estado (None = todos los no confirmados)
        limit: Maximo de registros a retornar

    Returns:
        Tupla con (lista de leads, total de registros)
    """
    cnx = get_db_connection()
    if cnx is None:
        return [], 0

    try:
        cursor = cnx.cursor(dictionary=True)

        # Asegurar columnas existen
        asegurar_columnas_sync()

        if status:
            # Filtrar por estado especifico
            cursor.execute("""
                SELECT id, nombre_apellido, empresa, correo, origen,
                       sync_status, sync_sent_at, sync_confirmed_at, sync_error,
                       submission_time
                FROM WIX
                WHERE sync_status = %s
                ORDER BY submission_time DESC
                LIMIT %s
            """, (status, limit))
        else:
            # Todos los no confirmados
            cursor.execute("""
                SELECT id, nombre_apellido, empresa, correo, origen,
                       sync_status, sync_sent_at, sync_confirmed_at, sync_error,
                       submission_time
                FROM WIX
                WHERE sync_status != 'confirmado' OR sync_status IS NULL
                ORDER BY submission_time DESC
                LIMIT %s
            """, (limit,))

        leads = cursor.fetchall()

        # Convertir datetime a string
        for lead in leads:
            for key, value in lead.items():
                if isinstance(value, datetime):
                    lead[key] = value.isoformat()

        # Obtener total
        if status:
            cursor.execute("SELECT COUNT(*) as total FROM WIX WHERE sync_status = %s", (status,))
        else:
            cursor.execute("SELECT COUNT(*) as total FROM WIX WHERE sync_status != 'confirmado' OR sync_status IS NULL")

        total = cursor.fetchone()["total"]

        return leads, total

    except Exception as e:
        print(f"[SyncService] ERROR al obtener leads pendientes: {e}")
        return [], 0

    finally:
        cursor.close()
        cnx.close()


def obtener_estadisticas_sync() -> Dict[str, Any]:
    """
    Obtiene estadisticas de sincronizacion.
    """
    cnx = get_db_connection()
    if cnx is None:
        return {"error": "No se pudo conectar a la BD"}

    try:
        cursor = cnx.cursor(dictionary=True)

        # Asegurar columnas existen
        asegurar_columnas_sync()

        cursor.execute("""
            SELECT
                sync_status,
                COUNT(*) as cantidad
            FROM WIX
            GROUP BY sync_status
        """)

        stats_raw = cursor.fetchall()

        stats = {
            "pendiente": 0,
            "enviado": 0,
            "confirmado": 0,
            "error": 0,
            "timeout": 0,
            "sin_estado": 0
        }

        for row in stats_raw:
            status = row["sync_status"] or "sin_estado"
            stats[status] = row["cantidad"]

        # Total
        stats["total"] = sum(stats.values())

        return stats

    except Exception as e:
        print(f"[SyncService] ERROR al obtener estadisticas: {e}")
        return {"error": str(e)}

    finally:
        cursor.close()
        cnx.close()


def verificar_timeouts() -> int:
    """
    Verifica leads enviados que no han sido confirmados dentro del timeout.
    Marca como 'timeout' los que exceden el limite.

    Returns:
        Cantidad de leads marcados como timeout
    """
    cnx = get_db_connection()
    if cnx is None:
        return 0

    try:
        cursor = cnx.cursor()

        # Marcar como timeout los que excedan el limite
        cursor.execute("""
            UPDATE WIX
            SET sync_status = 'timeout',
                sync_error = %s
            WHERE sync_status = 'enviado'
              AND sync_sent_at < DATE_SUB(NOW(), INTERVAL %s HOUR)
        """, (f"Sin confirmacion despues de {SYNC_TIMEOUT_HOURS} horas", SYNC_TIMEOUT_HOURS))

        affected = cursor.rowcount
        cnx.commit()

        if affected > 0:
            print(f"[SyncService] {affected} leads marcados como timeout")

        return affected

    except Exception as e:
        print(f"[SyncService] ERROR al verificar timeouts: {e}")
        return 0

    finally:
        cursor.close()
        cnx.close()


def obtener_todos_los_leads(
    asignado: Optional[bool] = None,
    asesor: Optional[str] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    origen: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Tuple[List[Dict], int]:
    """
    Obtiene todos los leads con filtros opcionales.

    Args:
        asignado: True=solo asignados, False=solo sin asignar, None=todos
        asesor: Filtrar por asesor asignado (asesor_in)
        fecha_desde: Fecha minima de submission_time (YYYY-MM-DD)
        fecha_hasta: Fecha maxima de submission_time (YYYY-MM-DD)
        origen: Filtrar por origen (WIX, UNKNOWN, etc.)
        limit: Maximo de registros a retornar
        offset: Registros a saltar (para paginacion)

    Returns:
        Tupla con (lista de leads, total de registros)
    """
    cnx = get_db_connection()
    if cnx is None:
        return [], 0

    try:
        cursor = cnx.cursor(dictionary=True)

        # Construir query dinamicamente
        base_query = """
            SELECT
                id, nombre_apellido, empresa, telefono2, ruc_dni, correo,
                treq_requerimiento, origen, submission_time, observacion,
                asesor_in, fecha_asignacion,
                siek_cliente, ia_cliente_doc, ia_cliente_sector,
                ia_cliente_razon_social, ia_tipo_requerimiento, ia_confianza,
                sync_status, sync_sent_at, sync_confirmed_at
            FROM WIX
            WHERE 1=1
        """

        count_query = "SELECT COUNT(*) as total FROM WIX WHERE 1=1"

        params = []
        conditions = ""

        # Filtro por asignacion
        if asignado is True:
            conditions += " AND (asesor_in IS NOT NULL AND asesor_in != '' AND fecha_asignacion IS NOT NULL)"
        elif asignado is False:
            conditions += " AND (asesor_in IS NULL OR asesor_in = '' OR fecha_asignacion IS NULL)"

        # Filtro por asesor
        if asesor:
            conditions += " AND asesor_in = %s"
            params.append(asesor)

        # Filtro por fecha desde
        if fecha_desde:
            conditions += " AND DATE(submission_time) >= %s"
            params.append(fecha_desde)

        # Filtro por fecha hasta
        if fecha_hasta:
            conditions += " AND DATE(submission_time) <= %s"
            params.append(fecha_hasta)

        # Filtro por origen
        if origen:
            conditions += " AND origen = %s"
            params.append(origen)

        # Query final con ordenamiento y paginacion
        final_query = base_query + conditions + " ORDER BY submission_time DESC LIMIT %s OFFSET %s"
        final_count_query = count_query + conditions

        # Ejecutar count primero
        cursor.execute(final_count_query, params)
        total = cursor.fetchone()["total"]

        # Ejecutar query principal
        cursor.execute(final_query, params + [limit, offset])
        leads = cursor.fetchall()

        # Convertir datetime a string y agregar campo calculado 'asignado'
        for lead in leads:
            for key, value in lead.items():
                if isinstance(value, datetime):
                    lead[key] = value.isoformat()

            # Campo calculado: esta asignado?
            lead['asignado'] = bool(
                lead.get('asesor_in') and
                lead.get('fecha_asignacion')
            )

        return leads, total

    except Exception as e:
        print(f"[SyncService] ERROR al obtener leads: {e}")
        return [], 0

    finally:
        cursor.close()
        cnx.close()


def obtener_asesores_disponibles() -> List[str]:
    """
    Obtiene la lista de asesores que tienen leads asignados.
    Util para filtros en el frontend.
    """
    cnx = get_db_connection()
    if cnx is None:
        return []

    try:
        cursor = cnx.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT asesor_in
            FROM WIX
            WHERE asesor_in IS NOT NULL AND asesor_in != ''
            ORDER BY asesor_in
        """)

        asesores = [row["asesor_in"] for row in cursor.fetchall()]
        return asesores

    except Exception as e:
        print(f"[SyncService] ERROR al obtener asesores: {e}")
        return []

    finally:
        cursor.close()
        cnx.close()


def obtener_estadisticas_asignacion() -> Dict[str, Any]:
    """
    Obtiene estadisticas de asignacion de leads.
    """
    cnx = get_db_connection()
    if cnx is None:
        return {"error": "No se pudo conectar a la BD"}

    try:
        cursor = cnx.cursor(dictionary=True)

        # Total de leads
        cursor.execute("SELECT COUNT(*) as total FROM WIX")
        total = cursor.fetchone()["total"]

        # Leads asignados
        cursor.execute("""
            SELECT COUNT(*) as asignados
            FROM WIX
            WHERE asesor_in IS NOT NULL AND asesor_in != '' AND fecha_asignacion IS NOT NULL
        """)
        asignados = cursor.fetchone()["asignados"]

        # Leads sin asignar
        sin_asignar = total - asignados

        # Por asesor
        cursor.execute("""
            SELECT asesor_in, COUNT(*) as cantidad
            FROM WIX
            WHERE asesor_in IS NOT NULL AND asesor_in != ''
            GROUP BY asesor_in
            ORDER BY cantidad DESC
        """)
        por_asesor = {row["asesor_in"]: row["cantidad"] for row in cursor.fetchall()}

        # Por origen
        cursor.execute("""
            SELECT origen, COUNT(*) as cantidad
            FROM WIX
            GROUP BY origen
            ORDER BY cantidad DESC
        """)
        por_origen = {row["origen"] or "sin_origen": row["cantidad"] for row in cursor.fetchall()}

        return {
            "total": total,
            "asignados": asignados,
            "sin_asignar": sin_asignar,
            "porcentaje_asignados": round((asignados / total * 100) if total > 0 else 0, 1),
            "por_asesor": por_asesor,
            "por_origen": por_origen
        }

    except Exception as e:
        print(f"[SyncService] ERROR al obtener estadisticas de asignacion: {e}")
        return {"error": str(e)}

    finally:
        cursor.close()
        cnx.close()
