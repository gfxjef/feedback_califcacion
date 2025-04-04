import os
import re
import requests
import mysql.connector
from mysql.connector import errorcode
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import ftplib

# Importa la función de conexión de db.py
from .db import get_db_connection
from .enviar_encuesta import enviar_encuesta
from .login import login_bp
from .roles_menu import roles_menu_bp
from .Mailing.wix import wix_bp

app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={r"/*": {"origins": [
    "https://atusaludlicoreria.com",
    "https://kossodo.estilovisual.com",
    "https://www.kossodo.com"
]}})

TABLE_NAME = "envio_de_encuestas"

def create_table_if_not_exists(cursor):
    """
    Crea la tabla envio_de_encuestas si no existe.
    Incluye las columnas calificacion, segmento, tipo, grupo y, si es necesario,
    agrega las columnas observaciones y documento.
    También se agrega la columna fecha_califacion para registrar el momento de la calificación.
    """
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        idcalificacion INT AUTO_INCREMENT PRIMARY KEY,
        asesor VARCHAR(255) NOT NULL,
        nombres VARCHAR(255) NOT NULL,
        ruc VARCHAR(50) NOT NULL,
        correo VARCHAR(255) NOT NULL,
        documento VARCHAR(255) NULL,
        segmento VARCHAR(255),
        tipo VARCHAR(50),
        grupo VARCHAR(255),
        calificacion VARCHAR(50),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        fecha_califacion DATETIME NULL
    ) ENGINE=InnoDB;
    """
    cursor.execute(create_table_query)

    # Agregar la columna observaciones si no existe
    try:
        add_observaciones_query = f"""
        ALTER TABLE {TABLE_NAME}
        ADD COLUMN observaciones TEXT NULL AFTER calificacion;
        """
        cursor.execute(add_observaciones_query)
    except mysql.connector.Error as err:
        if err.errno == 1060:  # Columna duplicada
            pass
        else:
            raise

    # Agregar la columna documento si no existe (en caso de que la tabla ya exista)
    try:
        add_documento_query = f"""
        ALTER TABLE {TABLE_NAME}
        ADD COLUMN documento VARCHAR(255) NULL AFTER correo;
        """
        cursor.execute(add_documento_query)
    except mysql.connector.Error as err:
        if err.errno == 1060:
            pass
        else:
            raise

    # Agregar la columna tipo si no existe
    try:
        add_tipo_query = f"""
        ALTER TABLE {TABLE_NAME}
        ADD COLUMN tipo VARCHAR(50) NULL AFTER segmento;
        """
        cursor.execute(add_tipo_query)
    except mysql.connector.Error as err:
        if err.errno == 1060:
            pass
        else:
            raise

    # Agregar la columna grupo si no existe
    try:
        add_grupo_query = f"""
        ALTER TABLE {TABLE_NAME}
        ADD COLUMN grupo VARCHAR(255) NULL AFTER tipo;
        """
        cursor.execute(add_grupo_query)
    except mysql.connector.Error as err:
        if err.errno == 1060:
            pass
        else:
            raise

    # Agregar la columna fecha_califacion si no existe
    try:
        add_fecha_califacion_query = f"""
        ALTER TABLE {TABLE_NAME}
        ADD COLUMN fecha_califacion DATETIME NULL AFTER timestamp;
        """
        cursor.execute(add_fecha_califacion_query)
    except mysql.connector.Error as err:
        if err.errno == 1060:
            pass
        else:
            raise
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200


@app.route('/submit', methods=['POST'])
def submit():
    """
    Recibe datos desde un JSON y registra esos datos en la BD.
    Además, envía una encuesta por correo.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'status': 'error', 'message': 'Falta el body JSON'}), 400

    asesor = data.get('asesor')
    nombres = data.get('nombres')
    ruc = data.get('ruc')
    correo = data.get('correo')
    tipo = data.get('tipo', '')
    grupo = data.get('grupo')  # Campo "grupo" ahora es opcional
    documento = data.get('documento') or None  # Campo opcional

    # Validación de campos requeridos (se omite "grupo" al no ser obligatorio)
    if not all([asesor, nombres, ruc, correo]):
        return jsonify({'status': 'error', 'message': 'Faltan campos por completar.'}), 400

    # Validar formato del correo
    if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
        return jsonify({'status': 'error', 'message': 'Correo electrónico inválido.'}), 400

    # Validar RUC (debe ser numérico y tener 11 dígitos)
    if not ruc.isdigit() or len(ruc) != 11:
        return jsonify({'status': 'error', 'message': 'RUC inválido. Debe contener 11 dígitos.'}), 400

    # Se asigna el segmento "Otros"
    segmento = "Otros"

    # Insertar los datos en la BD
    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor()
        create_table_if_not_exists(cursor)

        insert_query = f"""
        INSERT INTO {TABLE_NAME} (asesor, nombres, ruc, correo, documento, segmento, tipo, grupo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (asesor, nombres, ruc, correo, documento, segmento, tipo, grupo))
        cnx.commit()

        idcalificacion = cursor.lastrowid
        numero_consulta = f"CONS-{idcalificacion:06d}"
    except mysql.connector.Error as err:
        print(f"Error al insertar los datos en la base de datos: {err}")
        return jsonify({'status': 'error', 'message': 'Error al insertar los datos en la base de datos.'}), 500
    finally:
        cursor.close()
        cnx.close()

    # Enviar la encuesta (la función enviar_encuesta se encarga de la validación y el envío múltiple)
    encuesta_response, status_code = enviar_encuesta(
        nombre_cliente=nombres,
        correo_cliente=correo,
        asesor=asesor,
        numero_consulta=numero_consulta,
        tipo=tipo
    )

    if status_code != 200:
        return jsonify(encuesta_response), status_code

    return jsonify({'status': 'success', 'message': 'Datos guardados y encuesta enviada correctamente.'}), 200


@app.route('/encuesta', methods=['GET'])
def encuesta():
    unique_id = request.args.get('unique_id')
    calificacion = request.args.get('calificacion')

    if not all([unique_id, calificacion]):
        return jsonify({'status': 'error', 'message': 'Parámetros faltantes (unique_id y calificacion).'}), 400

    valid_calificaciones = ["Bueno", "Regular", "Malo"]
    if calificacion not in valid_calificaciones:
        return jsonify({'status': 'error', 'message': 'Calificación inválida. Solo se permite Bueno, Regular o Malo.'}), 400

    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor()
        select_query = f"SELECT calificacion FROM {TABLE_NAME} WHERE idcalificacion = %s"
        cursor.execute(select_query, (unique_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({'status': 'error', 'message': 'No se encontró el registro con ese unique_id.'}), 404

        calificacion_actual = row[0]
        # Si ya hay una calificación previa, redirige a "ya respondida"
        if calificacion_actual and calificacion_actual.strip():
            return redirect("https://kossodo.estilovisual.com/kossomet/califacion/paginas/encuesta-ya-respondida.html")

        update_query = f"""
            UPDATE {TABLE_NAME}
            SET calificacion = %s, fecha_califacion = CURRENT_TIMESTAMP
            WHERE idcalificacion = %s
        """
        cursor.execute(update_query, (calificacion, unique_id))
        cnx.commit()

        # Redirigir según la calificación
        if calificacion == "Malo":
            return redirect(f"https://kossodo.estilovisual.com/kossomet/califacion/paginas/encuesta_lamentamos.html?unique_id={unique_id}")
        else:
            return redirect(f"https://kossodo.estilovisual.com/kossomet/califacion/paginas/encuesta-gracias.html?unique_id={unique_id}")

    except mysql.connector.Error as err:
        print(f"Error al actualizar la calificación: {err}")
        return jsonify({'status': 'error', 'message': 'Error al actualizar la calificación.'}), 500
    finally:
        cursor.close()
        cnx.close()


# (El resto de los endpoints permanece sin cambios)

# Registrar blueprints
app.register_blueprint(login_bp)
app.register_blueprint(roles_menu_bp)
app.register_blueprint(wix_bp, url_prefix='/wix')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
