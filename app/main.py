import os
import re
import requests
import mysql.connector
from mysql.connector import errorcode
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import ftplib

# Importaciones del paquete app para compatibilidad con Gunicorn en producción
try:
    # Intenta importaciones del paquete (para Render/producción)
    from app.db import get_db_connection
    from app.enviar_encuesta import enviar_encuesta, enviar_email_lamentamos
    from app.login import login_bp
    from app.roles_menu import roles_menu_bp
    from app.Mailing.wix import wix_bp
    from app.Mailing.octopus_endpoints import octopus_bp
    from app.bd_endpoints import bd_bp
    from app.records import records_bp
except ImportError:
    # Si falla, usa importaciones relativas (para desarrollo con run_app.py)
    from db import get_db_connection
    from enviar_encuesta import enviar_encuesta, enviar_email_lamentamos
    from login import login_bp
    from roles_menu import roles_menu_bp
    from Mailing.wix import wix_bp
    from Mailing.octopus_endpoints import octopus_bp
    from bd_endpoints import bd_bp
    from records import records_bp

app = Flask(__name__)

# Configuración de CORS
CORS(app, resources={r"/*": {"origins": [
    "https://atusaludlicoreria.com",
    "https://kossodo.estilovisual.com",
    "https://www.kossodo.com",
    "https://www.kossomet.com"
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
        tipo=tipo,
        documento=documento
    )

    if status_code != 200:
        return jsonify(encuesta_response), status_code

    return jsonify({'status': 'success', 'message': 'Datos guardados y encuesta enviada correctamente.'}), 200


@app.route('/encuesta', methods=['GET'])
def encuesta():
    unique_id = request.args.get('unique_id')
    calificacion = request.args.get('calificacion')
    tipo = request.args.get('tipo')  # Capturamos el parámetro tipo

    if not all([unique_id, calificacion]):
        return jsonify({'status': 'error', 'message': 'Parámetros faltantes (unique_id y calificacion).'}), 400

    # Validar que la calificación sea un número del 1 al 10
    if not calificacion:
        return jsonify({'status': 'error', 'message': 'Calificación es requerida.'}), 400
    
    try:
        calificacion_num = int(calificacion)
        if calificacion_num < 1 or calificacion_num > 10:
            return jsonify({'status': 'error', 'message': 'Calificación inválida. Solo se permite del 1 al 10.'}), 400
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Calificación debe ser un número del 1 al 10.'}), 400

    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor(dictionary=True)
        select_query = f"SELECT calificacion FROM {TABLE_NAME} WHERE idcalificacion = %s"
        cursor.execute(select_query, (unique_id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({'status': 'error', 'message': 'No se encontró el registro con ese unique_id.'}), 404

        calificacion_actual = row['calificacion']
        # Si ya hay una calificación previa, redirige a "ya respondida"
        if calificacion_actual and str(calificacion_actual).strip():
            return redirect("https://kossodo.estilovisual.com/kossomet/califacion/paginas/encuesta-ya-respondida.html")

        update_query = f"""
            UPDATE {TABLE_NAME}
            SET calificacion = %s, fecha_califacion = CURRENT_TIMESTAMP
            WHERE idcalificacion = %s
        """
        cursor.execute(update_query, (calificacion_num, unique_id))
        cnx.commit()

        # Lógica de redirección según la nueva escala numérica
        # Calificaciones 1-3: Insatisfecho (equivalente a "Malo") - Email de lamentamos
        # Calificaciones 4-7: Regular 
        # Calificaciones 8-10: Satisfecho (equivalente a "Bueno")
        
        if calificacion_num <= 3:
            # CALIFICACIÓN BAJA (1-3): Enviar email de lamentamos + redirigir
            tipo_param = (tipo or "").strip()
            
            # --- ENVÍO AUTOMÁTICO DE EMAIL DE LAMENTAMOS ---
            try:
                # Obtener datos completos del cliente desde la base de datos
                cursor_datos = cnx.cursor(dictionary=True)
                query_datos = f"""
                    SELECT asesor, nombres, correo, documento, tipo, segmento, grupo 
                    FROM {TABLE_NAME} 
                    WHERE idcalificacion = %s
                """
                cursor_datos.execute(query_datos, (unique_id,))
                datos_cliente = cursor_datos.fetchone()
                cursor_datos.close()
                
                if datos_cliente:
                    # Generar número de consulta con validación
                    try:
                        unique_id_int = int(unique_id) if unique_id else 0
                        numero_consulta = f"CONS-{unique_id_int:06d}"
                    except (ValueError, TypeError):
                        numero_consulta = f"CONS-{unique_id or 'UNKNOWN'}"
                    
                    # Enviar email de lamentamos automáticamente
                    print(f"📧 Enviando email de lamentamos automático para calificación {calificacion_num}")
                    resultado_email, codigo_email = enviar_email_lamentamos(
                        nombre_cliente=datos_cliente['nombres'],
                        correo_cliente=datos_cliente['correo'],
                        numero_consulta=numero_consulta,
                        tipo=datos_cliente['tipo'] or tipo_param,
                        documento=datos_cliente['documento']
                    )
                    
                    if codigo_email == 200:
                        print(f"✅ Email de lamentamos enviado exitosamente: {resultado_email['message']}")
                    else:
                        print(f"⚠️  Error enviando email de lamentamos: {resultado_email['message']}")
                        
                else:
                    print(f"⚠️  No se encontraron datos del cliente para unique_id: {unique_id}")
                    
            except Exception as e:
                print(f"❌ Error enviando email de lamentamos automático: {e}")
                # Continuamos con la redirección aunque falle el email
            
            # --- REDIRECCIÓN SEGÚN EL TIPO (como antes) ---
            if tipo_param in ["Ventas", "Ventas (OT)", "Ventas (OC)"]:
                # Redirige a la página de lamentación para Ventas
                return redirect(f"https://kossodo.estilovisual.com/kossomet/califacion/paginas/encuesta_lamentamos_ventas.html?unique_id={unique_id}")
            elif tipo_param in ["Operaciones"]:
                # Redirige a la página de lamentación para Operaciones
                return redirect(f"https://kossodo.estilovisual.com/kossomet/califacion/paginas/encuesta_lamentamos_operaciones.html?unique_id={unique_id}")
            else:
                # Para Coordinador (Conformidad) u otro, redirige a la página de lamentación de coordinación
                return redirect(f"https://kossodo.estilovisual.com/kossomet/califacion/paginas/encuesta_lamentamos_coordinacion.html?unique_id={unique_id}")
        else:
            # Para calificaciones 5-10 redirige a la página de agradecimiento
            return redirect(f"https://kossodo.estilovisual.com/kossomet/califacion/paginas/encuesta-gracias.html?unique_id={unique_id}")

    except mysql.connector.Error as err:
        print(f"Error al actualizar la calificación: {err}")
        return jsonify({'status': 'error', 'message': 'Error al actualizar la calificación.'}), 500
    finally:
        cursor.close()
        cnx.close()




@app.route('/observaciones', methods=['POST'])
def guardar_observaciones():
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
        print(f"Error al actualizar observaciones: {err}")
        return jsonify({'status': 'error', 'message': 'Error al actualizar observaciones'}), 500
    finally:
        cursor.close()
        cnx.close()

@app.route('/segmento_imagenes', methods=['GET'])
def segmento_imagenes():
    unique_id = request.args.get('unique_id')
    if not unique_id:
        return jsonify({'status': 'error', 'message': 'Falta el parámetro unique_id'}), 400

    carpeta = "Otros"
    try:
        ftp = ftplib.FTP("75.102.23.104", "kossodo_kossodo.estilovisual.com", "kossodo2024##")
        ftp.cwd(f"/marketing/calificacion/categorias/{carpeta}")
        files = ftp.nlst()
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
        image_filenames = [f for f in files if f.lower().endswith(valid_extensions)]
        ftp.quit()
    except ftplib.all_errors as e:
        print(f"Error FTP: {e}")
        return jsonify({'status': 'error', 'message': 'Error al acceder vía FTP'}), 500

    image_urls = [f"https://kossodo.estilovisual.com/marketing/calificacion/categorias/{carpeta}/{filename}"
                  for filename in image_filenames]
    return jsonify({
        'status': 'success',
        'image_urls': image_urls
    }), 200


@app.route('/feedback_especifico', methods=['GET'])
def guardar_feedback_especifico():
    """Endpoint para guardar feedback específico cuando la calificación es baja (1-3)"""
    unique_id = request.args.get('unique_id')
    tipo = request.args.get('tipo')
    motivo = request.args.get('motivo')
    
    if not all([unique_id, tipo, motivo]):
        return jsonify({'status': 'error', 'message': 'Parámetros faltantes (unique_id, tipo, motivo).'}), 400

    cnx = get_db_connection()
    if cnx is None:
        return jsonify({'status': 'error', 'message': 'No se pudo conectar a la base de datos.'}), 500

    try:
        cursor = cnx.cursor(dictionary=True)
        
        # Verificar que el registro existe
        select_query = f"SELECT idcalificacion, observaciones FROM {TABLE_NAME} WHERE idcalificacion = %s"
        cursor.execute(select_query, (unique_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'status': 'error', 'message': 'No se encontró el registro con ese unique_id.'}), 404

        # --- VALIDACIÓN: Verificar si ya existe feedback específico ---
        observaciones_actual = row['observaciones'] or ""
        if "Feedback específico:" in observaciones_actual:
            # Si ya existe feedback específico, redirigir a "ya respondida"
            return redirect("https://kossodo.estilovisual.com/kossomet/califacion/paginas/encuesta-ya-respondida.html")
        # -------------------------------------------------------------------------

        # Preparar el texto del motivo según el tipo y motivo recibidos
        motivos_textos = {
            'ventas': {
                'falta_informacion': 'Falta de información sobre servicios',
                'demora_respuesta': 'Demora en respuesta a consultas',
                'presion_venta': 'Sensación de presión en la venta',
                'incapacidad_resolver': 'Incapacidad para resolver dudas'
            },
            'operaciones': {
                'comunicacion_deficiente': 'Comunicación deficiente para coordinar servicio',
                'fecha_lejana': 'Fecha disponible muy lejana',
                'incumplimiento_fecha': 'Incumplimiento de fecha acordada',
                'atencion_insatisfactoria': 'Atención técnica insatisfactoria',
                'demora_informes': 'Demora en la entrega de informes',
                'demora_consultas': 'Demora en la Respuestas a consultas técnicas'
            }
        }
        
        # Determinar el tipo normalizado
        tipo_normalizado = 'ventas' if tipo.lower() in ['ventas', 'ventas (ot)', 'ventas (oc)'] else 'operaciones'
        
        # Obtener el texto del motivo
        texto_motivo = motivos_textos.get(tipo_normalizado, {}).get(motivo, f"Motivo no especificado: {motivo}")
        
        # Actualizar las observaciones con el feedback específico (solo una vez)
        nuevo_feedback = f"Feedback específico: {texto_motivo}"
        observaciones_nuevas = nuevo_feedback
            
        update_query = f"UPDATE {TABLE_NAME} SET observaciones = %s WHERE idcalificacion = %s"
        cursor.execute(update_query, (observaciones_nuevas, unique_id))
        cnx.commit()

        # Redirigir a página de agradecimiento final por feedback específico
        return redirect("https://kossodo.estilovisual.com/kossomet/califacion/paginas/encuesta-gracias_final.html")

    except mysql.connector.Error as err:
        print(f"Error al guardar feedback específico: {err}")
        return jsonify({'status': 'error', 'message': 'Error al guardar feedback específico.'}), 500
    finally:
        cursor.close()
        cnx.close()


        
# Registrar blueprints
app.register_blueprint(login_bp)
app.register_blueprint(roles_menu_bp)
app.register_blueprint(wix_bp, url_prefix='/wix')
app.register_blueprint(octopus_bp, url_prefix='/octopus')
app.register_blueprint(bd_bp, url_prefix='/bd')
app.register_blueprint(records_bp)  # Registrar el blueprint de records


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
