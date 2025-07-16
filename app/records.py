# records.py
from flask import Blueprint, jsonify

try:
    # Importaciones del paquete app (para Render/producción)
    from app.db import get_db_connection
except ImportError:
    # Importaciones relativas (para desarrollo con run_app.py)
    from db import get_db_connection
# Ojo: TABLE_NAME podría ser "envio_de_encuestas" u otra.

records_bp = Blueprint('records_bp', __name__)
TABLE_NAME = "envio_de_encuestas"

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
