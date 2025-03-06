from flask import Blueprint, request, jsonify
from .db import get_db_connection  # Asegúrate de que db.py está en el mismo paquete o ajusta la importación

wix_bp = Blueprint('wix_bp', __name__)
TABLE_NAME = "WIX"  # Nombre exacto de la tabla

@wix_bp.route('/records', methods=['GET'])
def get_records():
    """
    Endpoint para obtener todos los registros de la tabla WIX.
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
    Endpoint para insertar un nuevo registro en la tabla WIX.
    Se espera recibir un JSON con los siguientes campos:
      - nombre_apellido
      - empresa
      - telefono2
      - ruc_dni
      - correo
      - treq_requerimiento
      - observacion
    La columna id y submission_time se generan automáticamente.
    """
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No se recibieron datos JSON.'}), 400

    # Validación de campos obligatorios
    required_fields = ["nombre_apellido", "empresa", "telefono2", "ruc_dni", "correo", "treq_requerimiento", "observacion"]
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Falta el campo {field}.'}), 400

    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor()
        insert_query = f"""
            INSERT INTO `{TABLE_NAME}` 
            (nombre_apellido, empresa, telefono2, ruc_dni, correo, treq_requerimiento, observacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        values = (
            data["nombre_apellido"],
            data["empresa"],
            data["telefono2"],
            data["ruc_dni"],
            data["correo"],
            data["treq_requerimiento"],
            data["observacion"]
        )
        cursor.execute(insert_query, values)
        cnx.commit()
        return jsonify({'status': 'success', 'message': 'Registro insertado correctamente.'}), 201
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        cnx.close()
