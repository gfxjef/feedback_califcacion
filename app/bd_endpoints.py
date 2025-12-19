from flask import Blueprint, request, jsonify

try:
    # Importaciones del paquete app (para Render/producción)
    from app.db import get_db_connection
    from app.Mailing.octopus import add_contact_to_octopus
    from app.Mailing.send_lead_notification import send_lead_notification_email
    from app.gemini.service import analizar_lead_automatico
except ImportError:
    # Importaciones relativas (para desarrollo con run_app.py)
    from db import get_db_connection
    from Mailing.octopus import add_contact_to_octopus
    from Mailing.send_lead_notification import send_lead_notification_email
    from gemini.service import analizar_lead_automatico

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
    Inserta un nuevo registro en la tabla WIX, envía a EmailOctopus y notifica condicionalmente.

    CAMPOS OBLIGATORIOS:
      - nombre_apellido
      - empresa
      - telefono2
      - correo

    CAMPOS OPCIONALES:
      - ruc_dni (puede ser null)
      - treq_requerimiento (puede ser null)
      - origen (default: "UNKNOWN")
      - asesor_tecnico (se mapea a asesor_in)
      - observacion (puede ser null)
      - submission_time (default: NOW())

    FUNCIONALIDADES:
    1. Inserta en BD con todos los campos
    2. Envía automáticamente a EmailOctopus
    3. Envía notificación SOLO si treq_requerimiento tiene contenido
    """
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No se recibieron datos JSON.'}), 400

    # Campos obligatorios - solo 4 campos esenciales
    required_fields = [
        "nombre_apellido",
        "empresa",
        "telefono2",
        "correo"
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({'status': 'error', 'message': f'Falta el campo {field}.'}), 400

    # Campos opcionales con valores por defecto
    origen = data.get("origen", "UNKNOWN")
    ruc_dni = data.get("ruc_dni", None)
    treq_requerimiento = data.get("treq_requerimiento", None)
    asesor_tecnico = data.get("asesor_tecnico", None)  # Se mapea a asesor_in
    observacion = data.get("observacion", None)

    # Manejo de submission_time - puede venir del cliente o usar NOW()
    submission_time_custom = data.get("submission_time", None)

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

        # Insertar el registro con todos los campos (incluyendo opcionales)
        if submission_time_custom:
            # Si se proporciona submission_time personalizado
            insert_query = f"""
                INSERT INTO `{TABLE_NAME}`
                (nombre_apellido, empresa, telefono2, ruc_dni, correo, treq_requerimiento, origen, submission_time, observacion, asesor_in)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            values = (
                data["nombre_apellido"],
                data["empresa"],
                data["telefono2"],
                ruc_dni,
                data["correo"],
                treq_requerimiento,
                origen,
                submission_time_custom,
                observacion,
                asesor_tecnico
            )
        else:
            # Usar NOW() para submission_time
            insert_query = f"""
                INSERT INTO `{TABLE_NAME}`
                (nombre_apellido, empresa, telefono2, ruc_dni, correo, treq_requerimiento, origen, submission_time, observacion, asesor_in)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s);
            """
            values = (
                data["nombre_apellido"],
                data["empresa"],
                data["telefono2"],
                ruc_dni,
                data["correo"],
                treq_requerimiento,
                origen,
                observacion,
                asesor_tecnico
            )
        cursor.execute(insert_query, values)
        cnx.commit()
        
        # Obtener el ID del registro insertado
        record_id = cursor.lastrowid

        # NUEVA FUNCIONALIDAD: Enviar a EmailOctopus
        try:
            oct_response = add_contact_to_octopus(
                email_address=data["correo"],
                nombre_apellido=data["nombre_apellido"],
                empresa=data["empresa"],
                ruc_dni=ruc_dni or ""  # Enviar string vacío si es None
            )
            if oct_response.status_code not in [200, 201]:
                print("Error al agregar el contacto a Octopus:", oct_response.text)
        except Exception as octopus_error:
            print(f"⚠️ Error al enviar a EmailOctopus: {octopus_error}")

        # NUEVA FUNCIONALIDAD: Notificación condicional
        notification_sent = False
        if treq_requerimiento and treq_requerimiento.strip():  # Solo si tiene contenido
            try:
                # Preparar datos del lead para la notificación
                lead_notification_data = {
                    'nombre_apellido': data["nombre_apellido"],
                    'empresa': data["empresa"],
                    'telefono2': data["telefono2"],
                    'correo': data["correo"],
                    'ruc_dni': ruc_dni or "",
                    'treq_requerimiento': treq_requerimiento,
                    'origen': origen,
                    'submission_time': submission_time_custom or 'Recién registrado'
                }

                # Enviar notificación
                notification_result, notification_status = send_lead_notification_email(lead_notification_data)

                if notification_result['status'] == 'ok':
                    print(f"✅ Notificación de lead enviada: {notification_result['message']}")
                    notification_sent = True
                elif notification_result['status'] == 'error':
                    print(f"❌ Error en notificación de lead: {notification_result['message']}")

            except Exception as notification_error:
                print(f"⚠️ Error al enviar notificación de lead: {notification_error}")

        # ANÁLISIS AUTOMÁTICO CON GEMINI IA
        gemini_result = None
        gemini_analyzed = False
        try:
            lead_data_gemini = {
                'empresa': data["empresa"],
                'ruc_dni': ruc_dni,
                'treq_requerimiento': treq_requerimiento,
                'origen': origen
            }

            gemini_result = analizar_lead_automatico(lead_data_gemini, record_id)

            if gemini_result.get('success'):
                gemini_analyzed = True
                print(f"✅ Análisis Gemini completado para lead {record_id}: siek_cliente={gemini_result.get('siek_cliente')}")
            else:
                print(f"⚠️ Análisis Gemini sin resultados: {gemini_result.get('error', 'Sin datos suficientes')}")

        except Exception as gemini_error:
            # Error en Gemini no debe afectar el flujo principal
            print(f"⚠️ Error en análisis Gemini (no crítico): {gemini_error}")

        return jsonify({
            'status': 'success',
            'message': 'Registro insertado correctamente en BD.',
            'record_id': record_id,
            'origen': origen,
            'notification_sent': notification_sent,
            'gemini_analyzed': gemini_analyzed
        }), 201
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        cnx.close()