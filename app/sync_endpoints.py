"""
Sync Endpoints - Blueprint para sincronizacion de leads con sistema externo

Endpoints de Leads (listado y filtros):
- GET  /sync/leads          - Lista todos los leads con filtros (asignado, asesor, fecha, origen)
- GET  /sync/leads/stats    - Estadisticas de asignacion de leads
- GET  /sync/leads/asesores - Lista de asesores disponibles para filtros
- GET  /sync/pending        - Lista leads pendientes de confirmacion (legacy)

Endpoints de Sincronizacion:
- GET  /sync/stats          - Estadisticas de sincronizacion
- GET  /sync/status/{id}    - Estado de un lead especifico
- POST /sync/confirm        - Confirma recepcion de un lead (llamado por sistema externo)
- POST /sync/retry/{id}     - Reintenta envio de un lead
- POST /sync/send/{id}      - Envia manualmente un lead
- POST /sync/check-timeouts - Verifica y marca timeouts
- POST /sync/init           - Inicializa columnas de sync
"""

from flask import Blueprint, request, jsonify

try:
    from app.sync_service import (
        enviar_lead_a_sistema_externo,
        confirmar_recepcion,
        obtener_leads_pendientes,
        obtener_estadisticas_sync,
        obtener_lead_completo,
        verificar_timeouts,
        asegurar_columnas_sync,
        obtener_todos_los_leads,
        obtener_asesores_disponibles,
        obtener_estadisticas_asignacion,
        SYNC_ENABLED,
        EXTERNAL_ENDPOINT,
        SYNC_TIMEOUT_HOURS
    )
except ImportError:
    from sync_service import (
        enviar_lead_a_sistema_externo,
        confirmar_recepcion,
        obtener_leads_pendientes,
        obtener_estadisticas_sync,
        obtener_lead_completo,
        verificar_timeouts,
        asegurar_columnas_sync,
        obtener_todos_los_leads,
        obtener_asesores_disponibles,
        obtener_estadisticas_asignacion,
        SYNC_ENABLED,
        EXTERNAL_ENDPOINT,
        SYNC_TIMEOUT_HOURS
    )


sync_bp = Blueprint('sync_bp', __name__)


@sync_bp.route('/leads', methods=['GET'])
def get_all_leads():
    """
    GET /sync/leads

    Lista todos los leads con filtros opcionales de asignación.

    Query params:
        - asignado: true/false - Filtrar por estado de asignación
        - asesor: string - Filtrar por asesor específico
        - fecha_desde: YYYY-MM-DD - Fecha mínima de asignación
        - fecha_hasta: YYYY-MM-DD - Fecha máxima de asignación
        - origen: string - Filtrar por origen (WIX, UNKNOWN, etc.)
        - limit: int - Máximo de registros (default: sin limite)
        - offset: int - Registros a saltar para paginación

    Returns:
        JSON con lista de leads, total y filtros aplicados
    """
    # Parsear parámetros
    asignado_param = request.args.get('asignado', None)
    asignado = None
    if asignado_param is not None:
        asignado = asignado_param.lower() == 'true'

    asesor = request.args.get('asesor', None)
    fecha_desde = request.args.get('fecha_desde', None)
    fecha_hasta = request.args.get('fecha_hasta', None)
    origen = request.args.get('origen', None)
    limit = request.args.get('limit', 10000, type=int)  # Sin limite por defecto
    offset = request.args.get('offset', 0, type=int)

    # Obtener leads
    leads, total = obtener_todos_los_leads(
        asignado=asignado,
        asesor=asesor,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        origen=origen,
        limit=limit,
        offset=offset
    )

    return jsonify({
        'status': 'success',
        'total': total,
        'returned': len(leads),
        'offset': offset,
        'limit': limit,
        'filters': {
            'asignado': asignado,
            'asesor': asesor,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'origen': origen
        },
        'leads': leads
    }), 200


@sync_bp.route('/leads/stats', methods=['GET'])
def get_leads_assignment_stats():
    """
    GET /sync/leads/stats

    Obtiene estadísticas de asignación de leads.

    Returns:
        JSON con estadísticas: total, asignados, sin_asignar, por_asesor, por_origen
    """
    stats = obtener_estadisticas_asignacion()

    if 'error' in stats:
        return jsonify({
            'status': 'error',
            'message': stats['error']
        }), 500

    return jsonify({
        'status': 'success',
        'statistics': stats
    }), 200


@sync_bp.route('/leads/asesores', methods=['GET'])
def get_asesores_list():
    """
    GET /sync/leads/asesores

    Obtiene lista de asesores disponibles para filtros.

    Returns:
        JSON con lista de asesores únicos
    """
    asesores = obtener_asesores_disponibles()

    return jsonify({
        'status': 'success',
        'asesores': asesores,
        'total': len(asesores)
    }), 200


@sync_bp.route('/pending', methods=['GET'])
def get_pending_leads():
    """
    GET /sync/pending

    Lista leads pendientes de confirmacion.

    Query params:
        - status: Filtrar por estado (pendiente, enviado, error, timeout)
        - limit: Maximo de registros (default: 100)

    Returns:
        JSON con lista de leads y total
    """
    status = request.args.get('status', None)
    limit = request.args.get('limit', 100, type=int)

    # Validar status
    valid_statuses = ['pendiente', 'enviado', 'error', 'timeout', None]
    if status and status not in valid_statuses:
        return jsonify({
            'status': 'error',
            'message': f'Estado invalido. Valores permitidos: {valid_statuses[:-1]}'
        }), 400

    leads, total = obtener_leads_pendientes(status=status, limit=limit)

    return jsonify({
        'status': 'success',
        'total': total,
        'returned': len(leads),
        'filter_status': status or 'todos (no confirmados)',
        'leads': leads
    }), 200


@sync_bp.route('/stats', methods=['GET'])
def get_sync_stats():
    """
    GET /sync/stats

    Obtiene estadisticas de sincronizacion.

    Returns:
        JSON con conteo por estado
    """
    stats = obtener_estadisticas_sync()

    if 'error' in stats:
        return jsonify({
            'status': 'error',
            'message': stats['error']
        }), 500

    return jsonify({
        'status': 'success',
        'config': {
            'sync_enabled': SYNC_ENABLED,
            'external_endpoint': EXTERNAL_ENDPOINT,
            'timeout_hours': SYNC_TIMEOUT_HOURS
        },
        'statistics': stats
    }), 200


@sync_bp.route('/status/<int:record_id>', methods=['GET'])
def get_lead_sync_status(record_id: int):
    """
    GET /sync/status/{id}

    Obtiene el estado de sincronizacion de un lead especifico.

    Returns:
        JSON con datos del lead y su estado de sync
    """
    lead = obtener_lead_completo(record_id)

    if not lead:
        return jsonify({
            'status': 'error',
            'message': f'Lead {record_id} no encontrado'
        }), 404

    return jsonify({
        'status': 'success',
        'lead': {
            'id': lead.get('id'),
            'nombre_apellido': lead.get('nombre_apellido'),
            'empresa': lead.get('empresa'),
            'correo': lead.get('correo'),
            'origen': lead.get('origen'),
            'submission_time': lead.get('submission_time')
        },
        'sync': {
            'status': lead.get('sync_status', 'pendiente'),
            'sent_at': lead.get('sync_sent_at'),
            'confirmed_at': lead.get('sync_confirmed_at'),
            'external_id': lead.get('sync_external_id'),
            'error': lead.get('sync_error')
        }
    }), 200


@sync_bp.route('/confirm', methods=['POST'])
def confirm_lead_reception():
    """
    POST /sync/confirm

    Confirma que el sistema externo recibio y proceso el lead.
    Este endpoint es llamado por el sistema externo.

    Body JSON:
        - record_id: int (requerido) - ID del lead en nuestra BD
        - external_id: string (opcional) - ID asignado por sistema externo

    Returns:
        JSON con resultado de la confirmacion
    """
    data = request.get_json()

    if not data:
        return jsonify({
            'status': 'error',
            'message': 'No se recibieron datos JSON'
        }), 400

    record_id = data.get('record_id')

    if not record_id:
        return jsonify({
            'status': 'error',
            'message': 'Falta el campo record_id'
        }), 400

    try:
        record_id = int(record_id)
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'record_id debe ser un numero entero'
        }), 400

    external_id = data.get('external_id')

    result = confirmar_recepcion(record_id, external_id)

    if result.get('success'):
        return jsonify({
            'status': 'success',
            'message': result['message'],
            'record_id': record_id,
            'external_id': external_id,
            'already_confirmed': result.get('already_confirmed', False)
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': result['message']
        }), 404


@sync_bp.route('/retry/<int:record_id>', methods=['POST'])
def retry_lead_sync(record_id: int):
    """
    POST /sync/retry/{id}

    Reintenta el envio de un lead al sistema externo.
    Util para leads con status pendiente, error o timeout.

    Returns:
        JSON con resultado del reintento
    """
    # Verificar que el lead existe
    lead = obtener_lead_completo(record_id)

    if not lead:
        return jsonify({
            'status': 'error',
            'message': f'Lead {record_id} no encontrado'
        }), 404

    # Verificar estado actual
    current_status = lead.get('sync_status', 'pendiente')

    if current_status == 'confirmado':
        return jsonify({
            'status': 'error',
            'message': f'Lead {record_id} ya esta confirmado, no requiere reintento'
        }), 400

    # Reintentar envio
    result = enviar_lead_a_sistema_externo(record_id)

    if result.get('success'):
        return jsonify({
            'status': 'success',
            'message': result['message'],
            'record_id': record_id,
            'new_status': 'enviado'
        }), 200
    elif result.get('skipped'):
        return jsonify({
            'status': 'warning',
            'message': result['message'],
            'record_id': record_id
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': result['message'],
            'record_id': record_id,
            'new_status': 'pendiente'
        }), 500


@sync_bp.route('/check-timeouts', methods=['POST'])
def check_sync_timeouts():
    """
    POST /sync/check-timeouts

    Verifica leads enviados que exceden el timeout sin confirmacion.
    Los marca con status 'timeout'.

    Este endpoint puede ser llamado periodicamente por un cron job.

    Returns:
        JSON con cantidad de leads marcados como timeout
    """
    affected = verificar_timeouts()

    return jsonify({
        'status': 'success',
        'message': f'{affected} leads marcados como timeout',
        'timeout_hours': SYNC_TIMEOUT_HOURS,
        'affected_count': affected
    }), 200


@sync_bp.route('/send/<int:record_id>', methods=['POST'])
def send_lead_manually(record_id: int):
    """
    POST /sync/send/{id}

    Envia manualmente un lead al sistema externo.
    Util para enviar leads que aun no han sido enviados.

    Returns:
        JSON con resultado del envio
    """
    # Verificar que el lead existe
    lead = obtener_lead_completo(record_id)

    if not lead:
        return jsonify({
            'status': 'error',
            'message': f'Lead {record_id} no encontrado'
        }), 404

    # Enviar
    result = enviar_lead_a_sistema_externo(record_id)

    if result.get('success'):
        return jsonify({
            'status': 'success',
            'message': result['message'],
            'record_id': record_id,
            'sync_status': 'enviado'
        }), 200
    elif result.get('skipped'):
        return jsonify({
            'status': 'warning',
            'message': result['message'],
            'record_id': record_id
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': result['message'],
            'record_id': record_id,
            'sync_status': 'pendiente'
        }), 500


@sync_bp.route('/init', methods=['POST'])
def initialize_sync_columns():
    """
    POST /sync/init

    Inicializa las columnas de sincronizacion en la tabla WIX.
    Solo necesario ejecutar una vez.

    Returns:
        JSON con resultado de la inicializacion
    """
    success = asegurar_columnas_sync()

    if success:
        return jsonify({
            'status': 'success',
            'message': 'Columnas de sincronizacion inicializadas correctamente'
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Error al inicializar columnas de sincronizacion'
        }), 500
