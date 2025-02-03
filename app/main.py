# main.py

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
# Permite solicitudes desde atusaludlicoreria.com y kossodo.estilovisual.com, etc.
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

# Carpeta base donde se encuentran las subcarpetas
FTP_BASE_FOLDER = "/marketing/calificacion/categorias"
# Versión HTTP (ruta pública) para mostrar las imágenes en <img src="...">
HTTP_BASE_URL = "https://kossodo.estilovisual.com/marketing/calificacion/categorias"

# ----------------------------------------------------------------------
# MAPEO SEGMENTO -> CARPETA
# ----------------------------------------------------------------------
SEGMENTO_MAPPING = {
    # Salud / Investigación
    "Articulos Informaticos - TI": "Salud_Investigacion",
    "Salud": "Salud_Investigacion",
    "Investigación": "Salud_Investigacion",
    "Farmaceutica": "Salud_Investigacion",
    "Drogueria": "Salud_Investigacion",
    "Laboratorio Particular": "Salud_Investigacion",
    "Fabricante de Materiales Medicos y Odontológico": "Salud_Investigacion",
    "Muestras Organicas": "Salud_Investigacion",
    "Salud y Belleza": "Salud_Investigacion",

    # Industria / Manufactura
    "Imprenta": "Industria_Manufactura",
    "Textil y Confecciones": "Industria_Manufactura",
    "Fabricante de Equipo/Producto Eléctrico": "Industria_Manufactura",
    "Metal Mecánicas": "Industria_Manufactura",
    "Fabricante de Vidrio": "Industria_Manufactura",
    "Químicas": "Industria_Manufactura",
    "Fabricación de artículos de papel/cartón": "Industria_Manufactura",
    "Plástico y Caucho": "Industria_Manufactura",

    # Comercio / Distribución
    "Comercio": "Comercio_Distribucion",
    "Almacenamiento y Deposito": "Comercio_Distribucion",
    "Revendedor": "Comercio_Distribucion",
    "Importación": "Comercio_Distribucion",
    "Venta de productos de primera necesidad": "Comercio_Distribucion",

    # Construcción / Servicios
    "Empresa de Limpieza y Fumigación": "Construccion_Servicios",
    "Construcción": "Construccion_Servicios",
    "Contratista": "Construccion_Servicios",
    "Servicios": "Construccion_Servicios",

    # Minería
    "Mineras No Metálicas": "Mineria",
    "Mineria": "Mineria",
    "Energía y Aguas": "Mineria",
    "Petroquimica": "Mineria",
    "Hidrocarburos": "Mineria",

    # Pesca / Alimentos
    "Aguas y Bebidas": "Pesca_Alimentos",
    "Pesca": "Pesca_Alimentos",
    "Agropecuarias y Agroindustriales": "Pesca_Alimentos",
    "Alimentos": "Pesca_Alimentos",

    # Educación / Consultoría
    "Educacion": "Educacion_Consultoria",
    "Consultor": "Educacion_Consultoria",
    "Docente": "Educacion_Consultoria",

    # Otros
    "Competencia": "Otros",
    "Publico": "Otros",
    "Uso propio": "Otros",
    "Varios": "Otros",
    "Organización No Gubernamental": "Otros"
}


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
    Incluye la columna `calificacion` y, si es necesario, agrega la columna `observaciones`.
    """
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
        idcalificacion INT AUTO_INCREMENT PRIMARY KEY,
        asesor VARCHAR(255) NOT NULL,
        nombres VARCHAR(255) NOT NULL,
        ruc VARCHAR(50) NOT NULL,
        correo VARCHAR(255) NOT NULL,
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
        # Si la columna ya existe, ignorar
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

    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor()
        create_table_if_not_exists(cursor)

        insert_query = f"""
        INSERT INTO `{TABLE_NAME}` (asesor, nombres, ruc, correo)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (asesor, nombres, ruc, correo))
        cnx.commit()

        # ID insertado
        idcalificacion = cursor.lastrowid
        numero_consulta = f"CONS-{idcalificacion:06d}"

    except mysql.connector.Error as err:
        app.logger.error(f"Error al insertar los datos en la base de datos: {err}")
        return jsonify({'status': 'error', 'message': 'Error al insertar los datos en la base de datos.'}), 500
    finally:
        cursor.close()
        cnx.close()

    # Enviar la encuesta
    nombre_cliente = nombres
    correo_cliente = correo
    encuesta_response, status_code = enviar_encuesta(
        nombre_cliente,
        correo_cliente,
        asesor,
        numero_consulta
    )
    if status_code != 200:
        return jsonify(encuesta_response), status_code

    return jsonify({'status': 'success', 'message': 'Datos guardados y encuesta enviada correctamente.'}), 200


@app.route('/encuesta', methods=['GET'])
def encuesta():
    """
    Endpoint que recibe los parámetros unique_id y calificacion
    y actualiza la calificación en la base de datos.
    Luego redirige a la página correspondiente.
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
            # Ya tiene calificación
            return redirect("https://atusaludlicoreria.com/kssd/firma/encuesta-ya-respondida.html")

        # Actualizar calificación
        update_query = f"""
            UPDATE {TABLE_NAME}
            SET calificacion = %s
            WHERE idcalificacion = %s
        """
        cursor.execute(update_query, (calificacion, unique_id))
        cnx.commit()

        # Redirige a la pantalla de "Gracias" con ?unique_id=
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
    unique_id = request.args.get('unique_id')
    if not unique_id:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro unique_id'}), 400

    # 1. RUC desde BD
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT ruc FROM envio_de_encuestas WHERE idcalificacion = %s", (unique_id,))
    row = cursor.fetchone()
    cursor.close()
    cnx.close()
    if not row:
        return jsonify({'status': 'error', 'message': 'No se encontró ese unique_id.'}), 404

    ruc_db = row[0]
    app.logger.info(f"(DEBUG) Para unique_id={unique_id}, RUC BD='{ruc_db}', len={len(ruc_db)}")

    # 2. Consumir la API
    try:
        response = requests.get("http://209.45.52.219:8090/mkt/lista-clientes", timeout=10)
        data = response.json()

        ruc_db_clean = ruc_db.strip()
        segmento_encontrado = None

        for cliente in data:
            numero_doc_api = str(cliente.get("NumeroDocumento", "")).strip()
            # LOG
            app.logger.info(f"(DEBUG) Comparo BD='{ruc_db_clean}' vs API='{numero_doc_api}'")

            if numero_doc_api == ruc_db_clean:
                segmento_encontrado = cliente.get("Segmento", "")
                break

        if not segmento_encontrado:
            segmento_encontrado = "Otros"
    except Exception as e:
        app.logger.error(f"Error consultando API: {e}")
        segmento_encontrado = "Otros"


    # Resto del código para mapear 'segmento_encontrado' a carpeta, listar en FTP, etc.
    carpeta = SEGMENTO_MAPPING.get(segmento_encontrado, "Otros")

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

    image_urls = [
        f"{HTTP_BASE_URL}/{carpeta}/{filename}"
        for filename in image_filenames
    ]

    return jsonify({
        'status': 'success',
        'segmento': segmento_encontrado,
        'carpeta': carpeta,
        'image_urls': image_urls
    }), 200

@app.route("/test-api")
def test_api():
    import requests
    url = "http://209.45.52.219:8090/mkt/lista-clientes"
    try:
        response = requests.get(url, timeout=10)
        return f"Status Code: {response.status_code}\nResponse: {response.text[:500]}"
    except requests.exceptions.RequestException as e:
        return f"Error: {e}", 500


@app.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    app.run()
