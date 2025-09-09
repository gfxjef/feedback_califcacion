from flask import Blueprint, request, jsonify
import requests

try:
    # Importaciones del paquete app (para Render/producción)
    from app.db import get_db_connection
except ImportError:
    # Importaciones relativas (para desarrollo con run_app.py)
    from db import get_db_connection

wix_bp = Blueprint('wix_bp', __name__)
TABLE_NAME = "WIX"  # Nombre exacto de la tabla en tu BD

@wix_bp.route('/records', methods=['GET'])
def get_records():
    """
    GET /wix/records
    Devuelve todos los registros de la tabla WIX.
    """
    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor(dictionary=True)
        query = f"SELECT * FROM `{TABLE_NAME}`;"
        cursor.execute(query)
        records = cursor.fetchall()
        return jsonify({'status': 'success', 'records': records}), 200
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        cnx.close()

@wix_bp.route('/records', methods=['POST'])
def insert_record():
    """
    POST /wix/records
    Endpoint orquestador para WIX.
    Recibe datos desde WIX y los envía a los endpoints independientes:
    1. BD endpoint (con origen="WIX")
    2. EmailOctopus endpoint
    
    Espera un JSON con:
      - nombre_apellido
      - empresa
      - telefono2
      - ruc_dni
      - correo
      - treq_requerimiento
    """
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No se recibieron datos JSON.'}), 400

    # Campos obligatorios
    required_fields = [
        "nombre_apellido",
        "empresa",
        "telefono2",
        "ruc_dni",
        "correo",
        "treq_requerimiento"
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Falta el campo {field}.'}), 400

    # Preparar datos para BD con origen WIX
    bd_data = data.copy()
    bd_data["origen"] = "WIX"
    
    # Variables para tracking de resultados
    bd_success = False
    octopus_success = False
    bd_response = None
    octopus_response = None

    # 1. Enviar a BD endpoint
    try:
        bd_url = request.host_url + "bd/records"
        bd_response = requests.post(bd_url, json=bd_data, headers={'Content-Type': 'application/json'})
        if bd_response.status_code == 201:
            bd_success = True
            print(f"✅ BD: Datos guardados exitosamente con origen WIX")
        else:
            print(f"⚠️  BD: Error al guardar - Status {bd_response.status_code}: {bd_response.text}")
    except Exception as e:
        print(f"❌ BD: Error de conexión - {str(e)}")

    # 2. Enviar a EmailOctopus endpoint
    try:
        octopus_url = request.host_url + "octopus/contacts"
        octopus_data = {
            "correo": data["correo"],
            "nombre_apellido": data["nombre_apellido"],
            "empresa": data["empresa"],
            "ruc_dni": data["ruc_dni"]
        }
        octopus_response = requests.post(octopus_url, json=octopus_data, headers={'Content-Type': 'application/json'})
        if octopus_response.status_code == 200:
            octopus_success = True
            print(f"✅ EmailOctopus: Contacto enviado exitosamente")
        else:
            print(f"⚠️  EmailOctopus: Error al enviar - Status {octopus_response.status_code}: {octopus_response.text}")
    except Exception as e:
        print(f"❌ EmailOctopus: Error de conexión - {str(e)}")

    # Preparar respuesta basada en resultados
    if bd_success and octopus_success:
        return jsonify({
            'status': 'success', 
            'message': 'Datos procesados exitosamente en BD y EmailOctopus.',
            'bd_success': True,
            'octopus_success': True
        }), 201
    elif bd_success and not octopus_success:
        return jsonify({
            'status': 'partial_success', 
            'message': 'Datos guardados en BD, pero falló envío a EmailOctopus.',
            'bd_success': True,
            'octopus_success': False
        }), 201
    elif not bd_success and octopus_success:
        return jsonify({
            'status': 'partial_success', 
            'message': 'Datos enviados a EmailOctopus, pero falló guardado en BD.',
            'bd_success': False,
            'octopus_success': True
        }), 201
    else:
        return jsonify({
            'status': 'error', 
            'message': 'Error al procesar datos tanto en BD como en EmailOctopus.',
            'bd_success': False,
            'octopus_success': False
        }), 500
