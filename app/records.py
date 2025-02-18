# records.py
from flask import Blueprint, jsonify
from . import get_db_connection, TABLE_NAME  # Asegúrate de ajustar la importación según tu estructura

records_bp = Blueprint('records_bp', __name__)

@records_bp.route('/records', methods=['GET'])
def get_records():
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
