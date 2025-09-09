from flask import Blueprint, request, jsonify

try:
    # Importaciones del paquete app (para Render/producción)
    from app.Mailing.octopus import add_contact_to_octopus
except ImportError:
    # Importaciones relativas (para desarrollo con run_app.py)
    from Mailing.octopus import add_contact_to_octopus

octopus_bp = Blueprint('octopus_bp', __name__)

@octopus_bp.route('/contacts', methods=['POST'])
def add_octopus_contact():
    """
    POST /octopus/contacts
    Envía un contacto directamente a EmailOctopus.
    Espera un JSON con:
      - correo (email_address)
      - nombre_apellido
      - empresa
      - ruc_dni
    
    Este endpoint es completamente independiente de la base de datos.
    Solo envía información a EmailOctopus API.
    """
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No se recibieron datos JSON.'}), 400

    # Campos obligatorios para EmailOctopus
    required_fields = [
        "correo",           # email_address
        "nombre_apellido",  # FirstName
        "empresa",          # COMPANY
        "ruc_dni"          # RUC
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Falta el campo {field} requerido para EmailOctopus.'}), 400

    try:
        # Llamar directamente a la función de EmailOctopus
        oct_response = add_contact_to_octopus(
            email_address=data["correo"],
            nombre_apellido=data["nombre_apellido"],
            empresa=data["empresa"],
            ruc_dni=data["ruc_dni"]
        )
        
        # Evaluar la respuesta de EmailOctopus
        if oct_response.status_code in [200, 201]:
            return jsonify({
                'status': 'success',
                'message': 'Contacto enviado exitosamente a EmailOctopus.',
                'octopus_status': oct_response.status_code,
                'octopus_response': oct_response.json() if oct_response.content else None
            }), 200
        else:
            # Error en EmailOctopus pero no es error crítico del endpoint
            return jsonify({
                'status': 'warning',
                'message': 'Error al enviar contacto a EmailOctopus.',
                'octopus_status': oct_response.status_code,
                'octopus_error': oct_response.text
            }), 200
            
    except ValueError as ve:
        # Error de configuración (API_KEY o LIST_ID faltantes)
        return jsonify({
            'status': 'error',
            'message': f'Error de configuración: {str(ve)}'
        }), 500
    except Exception as e:
        # Error general
        return jsonify({
            'status': 'error',
            'message': f'Error interno al procesar contacto: {str(e)}'
        }), 500

@octopus_bp.route('/status', methods=['GET'])
def octopus_status():
    """
    GET /octopus/status
    Verifica el estado de la configuración de EmailOctopus.
    """
    import os
    
    api_key = os.environ.get('OCTOPUS_API_KEY')
    list_id = os.environ.get('OCTOPUS_LIST_ID')
    
    status = {
        'api_key_configured': bool(api_key),
        'list_id_configured': bool(list_id),
        'ready': bool(api_key and list_id)
    }
    
    return jsonify({
        'status': 'success',
        'octopus_config': status
    }), 200