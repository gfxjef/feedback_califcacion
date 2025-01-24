#app.py
import os

import re
from flask import Flask, request, jsonify, redirect  # Importa desde 'flask', no desde 'app'
from flask_cors import CORS
import mysql.connector
from mysql.connector import errorcode
from .enviar_encuesta import enviar_encuesta

app = Flask(__name__)  
# ----------------------------------------------------------------------
# CONFIGURACIÓN DE CORS
# ----------------------------------------------------------------------
# Permite solicitudes desde https://kossodo.estilovisual.com para TODAS las rutas.
CORS(app, origins=["https://kossodo.estilovisual.com"])

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
    Incluye la columna `calificacion` para almacenar las respuestas de la encuesta.
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

@app.route('/submit', methods=['POST'])
def submit():
    """
    Endpoint que recibe datos desde un formulario (asesor, nombres, ruc, correo)
    y registra esos datos en la base de datos. Además, envía una encuesta por correo.
    """
    # ------------------------------------------------------------------
    # 1. Obtener y Validar Datos del Formulario
    # ------------------------------------------------------------------
    asesor = request.form.get('asesor')
    nombres = request.form.get('nombres')
    ruc = request.form.get('ruc')
    correo = request.form.get('correo')

    if not all([asesor, nombres, ruc, correo]):
        return jsonify({'status': 'error', 'message': 'Faltan campos por completar.'}), 400

    # Validar el formato del correo
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if not EMAIL_REGEX.match(correo):
        return jsonify({'status': 'error', 'message': 'Correo electrónico inválido.'}), 400

    # Validar RUC => 11 dígitos
    if not ruc.isdigit() or len(ruc) != 11:
        return jsonify({'status': 'error', 'message': 'RUC inválido. Debe contener 11 dígitos.'}), 400

    # ------------------------------------------------------------------
    # 2. Conexión a la Base de Datos e Inserción
    # ------------------------------------------------------------------
    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor()
        # Crea la tabla si no existe
        create_table_if_not_exists(cursor)

        # Insertar el registro
        insert_query = f"""
        INSERT INTO `{TABLE_NAME}` (asesor, nombres, ruc, correo)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (asesor, nombres, ruc, correo))
        cnx.commit()

        # Obtener el ID insertado (idcalificacion)
        idcalificacion = cursor.lastrowid
        numero_consulta = f"CONS-{idcalificacion:06d}"

    except mysql.connector.Error as err:
        app.logger.error(f"Error al insertar los datos en la base de datos: {err}")
        return jsonify({'status': 'error', 'message': 'Error al insertar los datos en la base de datos.'}), 500

    finally:
        cursor.close()
        cnx.close()

    # ------------------------------------------------------------------
    # 3. Enviar la Encuesta por Correo
    # ------------------------------------------------------------------
    nombre_cliente = nombres
    correo_cliente = correo
    # Llamar a la función para enviar la encuesta
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
    """
    from app import redirect  # Asegúrate de tenerlo importado
    
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
        select_query = f"""
            SELECT calificacion 
            FROM {TABLE_NAME}
            WHERE idcalificacion = %s
        """
        cursor.execute(select_query, (unique_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({'status': 'error', 'message': 'No se encontró el registro con ese unique_id.'}), 404

        calificacion_actual = row[0]
        # Si ya estaba calificado:
        if calificacion_actual is not None and calificacion_actual.strip() != "":
            return redirect("https://atusaludlicoreria.com/kssd/firma/encuesta-ya-respondida.html")

        # Si no estaba calificado, lo guardamos:
        update_query = f"""
            UPDATE {TABLE_NAME}
            SET calificacion = %s
            WHERE idcalificacion = %s
        """
        cursor.execute(update_query, (calificacion, unique_id))
        cnx.commit()

        # Redireccionar a la pantalla de "Gracias"
        return redirect("https://atusaludlicoreria.com/kssd/firma/encuesta-gracias.html")

    except mysql.connector.Error as err:
        app.logger.error(f"Error al actualizar la calificación: {err}")
        return jsonify({'status': 'error', 'message': 'Error al actualizar la calificación.'}), 500

    finally:
        cursor.close()
        cnx.close()

@app.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    # Ejecución local (modo desarrollo).
    # En producción (PythonAnywhere), se maneja vía WSGI.
    app.run()
