from flask import Blueprint, request, jsonify

try:
    # Importaciones del paquete app (para Render/producción)
    from app.db import get_db_connection
except ImportError:
    # Importaciones relativas (para desarrollo con run_app.py)
    from db import get_db_connection

bd_bp = Blueprint('bd_bp', __name__)
TABLE_NAME = "WIX"  # Nombre exacto de la tabla en tu BD

@bd_bp.route('/records', methods=['GET'])
def get_bd_records():
    """
    GET /bd/records
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

@bd_bp.route('/records', methods=['POST'])
def insert_bd_record():
    """
    POST /bd/records
    Inserta un nuevo registro en la tabla WIX con columna origen.
    Espera un JSON con:
      - nombre_apellido
      - empresa
      - telefono2
      - ruc_dni
      - correo
      - treq_requerimiento
      - origen (nuevo campo)
    
    La columna submission_time se asigna automáticamente con el timestamp actual.
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

    # Campo origen - si no se proporciona, usar "UNKNOWN"
    origen = data.get("origen", "UNKNOWN")

    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor()
        
        # Agregar columna origen si no existe
        try:
            add_origen_query = f"""
                ALTER TABLE `{TABLE_NAME}` 
                ADD COLUMN origen VARCHAR(50) DEFAULT 'UNKNOWN' AFTER treq_requerimiento;
            """
            cursor.execute(add_origen_query)
            cnx.commit()
        except Exception:
            # La columna ya existe, continuar
            pass

        # Insertar el registro con origen
        insert_query = f"""
            INSERT INTO `{TABLE_NAME}` 
            (nombre_apellido, empresa, telefono2, ruc_dni, correo, treq_requerimiento, origen, submission_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW());
        """
        values = (
            data["nombre_apellido"],
            data["empresa"],
            data["telefono2"],
            data["ruc_dni"],
            data["correo"],
            data["treq_requerimiento"],
            origen
        )
        cursor.execute(insert_query, values)
        cnx.commit()
        
        # Obtener el ID del registro insertado
        record_id = cursor.lastrowid

        return jsonify({
            'status': 'success', 
            'message': 'Registro insertado correctamente en BD.',
            'record_id': record_id,
            'origen': origen
        }), 201
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        cnx.close()