# wix.py
from flask import Blueprint, request, jsonify
from .db import get_db_connection  # Importamos la función de conexión

# Crea el Blueprint (puedes llamarlo como quieras)
wix_bp = Blueprint('wix_bp', __name__)

# Ajusta según el nombre real de tu tabla
TABLE_NAME = "envio_de_encuestas"  # Ejemplo. O "WIX" si así se llama tu tabla.

@wix_bp.route('/records', methods=['GET'])
def get_records():
    """
    Endpoint para obtener todos los registros de la tabla.
    GET /records
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
    Endpoint para insertar un nuevo registro en la tabla.
    POST /records
    Se espera un JSON en el body con campos como:
      {
        "nombre_apellido": "...",
        "empresa": "...",
        "telefono2": "...",
        "ruc_dni": "...",
        "correo": "...",
        "treq_requerimiento": "...",
        "observacion": "..."
      }
    """
    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    data = request.get_json()  # Obtenemos el body JSON enviado
    if not data:
        return jsonify({'status': 'error', 'message': 'No se recibieron datos JSON'}), 400

    try:
        cursor = cnx.cursor(dictionary=True)
        query = f"""
            INSERT INTO `{TABLE_NAME}`
            (nombre_apellido, empresa, telefono2, ruc_dni, correo, treq_requerimiento, observacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        values = (
            data.get('nombre_apellido'),
            data.get('empresa'),
            data.get('telefono2'),
            data.get('ruc_dni'),
            data.get('correo'),
            data.get('treq_requerimiento'),
            data.get('observacion')
        )
        cursor.execute(query, values)
        cnx.commit()
        return jsonify({'status': 'success', 'message': 'Registro insertado exitosamente'}), 201
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        cnx.close()
