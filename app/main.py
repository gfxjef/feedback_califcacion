import os
import re
import requests
import mysql.connector
from mysql.connector import errorcode
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS  # <--- Importante
import ftplib

from .enviar_encuesta import enviar_encuesta

app = Flask(__name__)

# ----------------------------------------------------------------------
# CONFIGURACIÓN DE CORS
# ----------------------------------------------------------------------
CORS(app, resources={r"/*": {"origins": [
    "https://atusaludlicoreria.com",
    "https://kossodo.estilovisual.com"
]}})

# ----------------------------------------------------------------------
# CONFIGURACIÓN DE LA BASE DE DATOS
# ----------------------------------------------------------------------
DB_CONFIG = {
    'user': os.environ.get('MYSQL_USER'),
    'password': os.environ.get('MYSQL_PASSWORD'),
    'host': os.environ.get('MYSQL_HOST'),
    'database': os.environ.get('MYSQL_DATABASE'),
    'port': 3306
}

TABLE_NAME = "envio_de_encuestas"

# ----------------------------------------------------------------------
# CONFIGURACIÓN DE FTP
# ----------------------------------------------------------------------
FTP_HOST = "75.102.23.104"  # server.estilovisual.com
FTP_USER = "kossodo_kossodo.estilovisual.com"
FTP_PASS = "kossodo2024##"

FTP_BASE_FOLDER = "/marketing/calificacion/categorias"
HTTP_BASE_URL = "https://kossodo.estilovisual.com/marketing/calificacion/categorias"

# Se elimina el diccionario SEGMENTO_MAPPING ya que no se utilizará.

def get_db_connection():
    """
    Establece la conexión con la base de datos.
    Retorna el objeto de conexión si es exitoso o None si falla.
    """
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            app.logger.error("Error de acceso a la base de datos: Usuario o contraseña incorrectos")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            app.logger.error("La base de datos no existe")
        else:
            app.logger.error(f"Error de conexión a la base de datos: {err}")
        return None

def create_table_if_not_exists(cursor):
    """
    Crea la tabla `envio_de_encuestas` si no existe.
    Incluye la columna `calificacion`, `segmento` y, si es necesario, agrega la columna `observaciones`.
    """
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
        idcalificacion INT AUTO_INCREMENT PRIMARY KEY,
        asesor VARCHAR(255) NOT NULL,
        nombres VARCHAR(255) NOT NULL,
        ruc VARCHAR(50) NOT NULL,
        correo VARCHAR(255) NOT NULL,
        segmento VARCHAR(255),
        calificacion VARCHAR(50),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """
    cursor.execute(create_table_query)

    # Agregar la columna observaciones si no existe
    try:
        add_column_query = f"""
        ALTER TABLE `{TABLE_NAME}`
        ADD COLUMN `observaciones` TEXT NULL AFTER `calificacion`;
        """
        cursor.execute(add_column_query)
    except mysql.connector.Error as err:
        if err.errno == 1060:  # Duplicate column name
            pass
        else:
            raise

@app.route('/submit', methods=['POST'])
def submit():
    """
    Endpoint que recibe datos desde un formulario (asesor, nombres, ruc, correo)
    y registra esos datos en la base de datos. Además, envía una encuesta por correo.
    """
    asesor = request.form.get('asesor')
    nombres = request.form.get('nombres')
    ruc = request.form.get('ruc')
    correo = request.form.get('correo')

    if not all([asesor, nombres, ruc, correo]):
        return jsonify({'status': 'error', 'message': 'Faltan campos por completar.'}), 400

    # Validar correo
    if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
        return jsonify({'status': 'error', 'message': 'Correo electrónico inválido.'}), 400

    # Validar RUC => 11 dígitos
    if not ruc.isdigit() or len(ruc) != 11:
        return jsonify({'status': 'error', 'message': 'RUC inválido. Debe contener 11 dígitos.'}), 400

    # Eliminamos la búsqueda por RUC para obtener el sector.
    segmento = "Otros"

    # Insertar los datos en la tabla de encuestas
    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor()
        create_table_if_not_exists(cursor)

        insert_query = f"""
        INSERT INTO `{TABLE_NAME}` (asesor, nombres, ruc, correo, segmento)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (asesor, nombres, ruc, correo, segmento))
        cnx.commit()

        idcalificacion = cursor.lastrowid
        numero_consulta = f"CONS-{idcalificacion:06d}"
    except mysql.connector.Error as err:
        app.logger.error(f"Error al insertar los datos en la base de datos: {err}")
        return jsonify({'status': 'error', 'message': 'Error al insertar los datos en la base de datos.'}), 500
    finally:
        cursor.close()
        cnx.close()

    # Enviar la encuesta
    encuesta_response, status_code = enviar_encuesta(
        nombre_cliente=nombres,
        correo_cliente=correo,
        asesor=asesor,
        numero_consulta=numero_consulta
    )
    if status_code != 200:
        return jsonify(encuesta_response), status_code

    return jsonify({'status': 'success', 'message': 'Datos guardados y encuesta enviada correctamente.'}), 200

@app.route('/encuesta', methods=['GET'])
def encuesta():
    """
    Endpoint que recibe los parámetros unique_id y calificacion,
    actualiza la calificación en la base de datos y redirige a la página correspondiente.
    """
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
        if calificacion_actual and calificacion_actual.strip():
            return redirect("https://atusaludlicoreria.com/kssd/firma/encuesta-ya-respondida.html")

        update_query = f"""
            UPDATE {TABLE_NAME}
            SET calificacion = %s
            WHERE idcalificacion = %s
        """
        cursor.execute(update_query, (calificacion, unique_id))
        cnx.commit()

        return redirect(f"https://atusaludlicoreria.com/kssd/firma/encuesta-gracias.html?unique_id={unique_id}")

    except mysql.connector.Error as err:
        app.logger.error(f"Error al actualizar la calificación: {err}")
        return jsonify({'status': 'error', 'message': 'Error al actualizar la calificación.'}), 500
    finally:
        cursor.close()
        cnx.close()

@app.route('/observaciones', methods=['POST'])
def guardar_observaciones():
    """
    Recibe JSON: { "unique_id": ..., "comentario": ... }
    y actualiza la columna 'observaciones' en el registro correspondiente.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'status': 'error', 'message': 'Falta el body JSON'}), 400

    unique_id = data.get('unique_id')
    comentario = data.get('comentario')
    if not unique_id or not comentario:
        return jsonify({'status': 'error', 'message': 'Faltan unique_id o comentario'}), 400

    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la BD'}), 500

    try:
        cursor = cnx.cursor()
        select_query = f"SELECT idcalificacion FROM {TABLE_NAME} WHERE idcalificacion = %s"
        cursor.execute(select_query, (unique_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'status': 'error', 'message': 'No se encontró ese unique_id.'}), 404

        update_query = f"UPDATE {TABLE_NAME} SET observaciones = %s WHERE idcalificacion = %s"
        cursor.execute(update_query, (comentario, unique_id))
        cnx.commit()

        return jsonify({'status': 'success', 'message': 'Comentario guardado correctamente'}), 200
    except mysql.connector.Error as err:
        app.logger.error(f"Error al actualizar observaciones: {err}")
        return jsonify({'status': 'error', 'message': 'Error al actualizar observaciones'}), 500
    finally:
        cursor.close()
        cnx.close()

@app.route('/segmento_imagenes', methods=['GET'])
def segmento_imagenes():
    """
    Endpoint que, a partir del unique_id, obtiene las imágenes del segmento.
    Ahora se utiliza directamente la carpeta 'Otros' sin buscar el sector por RUC.
    """
    unique_id = request.args.get('unique_id')
    if not unique_id:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro unique_id'}), 400

    # Asignamos directamente el segmento y carpeta a "Otros"
    segmento_encontrado = "Otros"
    carpeta = "Otros"

    image_filenames = []
    try:
        ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
        ftp.cwd(f"{FTP_BASE_FOLDER}/{carpeta}")
        files = ftp.nlst()

        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
        image_filenames = [f for f in files if f.lower().endswith(valid_extensions)]
        ftp.quit()
    except ftplib.all_errors as e:
        app.logger.error(f"Error FTP: {e}")

    image_urls = [f"{HTTP_BASE_URL}/{carpeta}/{filename}" for filename in image_filenames]

    return jsonify({
        'status': 'success',
        'segmento': segmento_encontrado,
        'carpeta': carpeta,
        'image_urls': image_urls
    }), 200

@app.route('/promo_click', methods=['POST'])
def promo_click():
    """
    Recibe JSON con:
      { "unique_id": "000123", "promo": "promo_mira" }
    Busca el registro en la tabla `envio_de_encuestas` y actualiza la primera columna de promoción (promo1 a promo5) que esté vacía,
    asignándole el valor recibido y la hora actual en su correspondiente campo time_promoX.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'status': 'error', 'message': 'Falta el body JSON'}), 400

    unique_id = data.get('unique_id')
    promo = data.get('promo')
    if not unique_id or not promo:
        return jsonify({'status': 'error', 'message': 'Faltan unique_id o promo'}), 400

    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la BD'}), 500

    try:
        # Consultar los campos promo1 a promo5 para saber cuál está libre
        cursor = cnx.cursor(dictionary=True)
        select_query = f"SELECT promo1, promo2, promo3, promo4, promo5 FROM {TABLE_NAME} WHERE idcalificacion = %s"
        cursor.execute(select_query, (unique_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'status': 'error', 'message': 'No se encontró ese unique_id.'}), 404

        # Buscar la primera columna promo vacía
        promo_slot = None
        slot_number = None
        for i in range(1, 6):
            if not row.get(f'promo{i}'):
                promo_slot = f'promo{i}'
                slot_number = i
                break

        if not promo_slot:
            return jsonify({'status': 'error', 'message': 'Se han llenado todas las promociones.'}), 400

        # Actualizar la columna encontrada y el campo time_promo correspondiente (se asume que la BD usa NOW())
        update_query = f"UPDATE {TABLE_NAME} SET {promo_slot} = %s, time_promo{slot_number} = NOW() WHERE idcalificacion = %s"
        cursor.execute(update_query, (promo, unique_id))
        cnx.commit()

        return jsonify({'status': 'success', 'message': f'Promoción guardada en {promo_slot}'}), 200

    except mysql.connector.Error as err:
        app.logger.error(f"Error al actualizar promo: {err}")
        return jsonify({'status': 'error', 'message': 'Error al actualizar promoción.'}), 500
    finally:
        cursor.close()
        cnx.close()

@app.route('/test_api', methods=['GET'])
def test_api():
    """
    Endpoint de prueba para obtener el segmento a partir de un RUC fijo.
    Ahora se retorna siempre 'Otros' como segmento.
    """
    ruc = "20100119227"
    return jsonify({
        "ruc": ruc,
        "segmento": "Otros",
        "razon_social": "Sin información"
    }), 200

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
