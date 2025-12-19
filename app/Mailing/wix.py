from flask import Blueprint, request, jsonify

try:
    # Importaciones del paquete app (para Render/producción)
    from app.db import get_db_connection
    from app.Mailing.octopus import add_contact_to_octopus
    from app.Mailing.send_lead_notification import send_lead_notification_email
    from app.gemini.service import analizar_lead_automatico
    from app.sync_service import enviar_lead_a_sistema_externo
except ImportError:
    # Importaciones relativas (para desarrollo con run_app.py)
    from db import get_db_connection
    from Mailing.octopus import add_contact_to_octopus
    from Mailing.send_lead_notification import send_lead_notification_email
    from gemini.service import analizar_lead_automatico
    from sync_service import enviar_lead_a_sistema_externo

wix_bp = Blueprint('wix_bp', __name__)
TABLE_NAME = "WIX"  # Nombre exacto de la tabla en tu BD

@wix_bp.route('/records', methods=['GET'])
def get_records():
    """
    GET /wix/records
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

@wix_bp.route('/records', methods=['POST'])
def insert_record():
    """
    POST /wix/records
    Inserta un nuevo registro en la tabla WIX con origen="WIX".
    Espera un JSON con:
      - nombre_apellido
      - empresa
      - telefono2
      - ruc_dni
      - correo
      - treq_requerimiento
    Luego, se envía el contacto a EmailOctopus.
    
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
        
        # Se agrega NOW() para que submission_time reciba la fecha y hora exacta
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
            "WIX"  # Origen fijo para WIX
        )
        cursor.execute(insert_query, values)
        cnx.commit()

        # Obtener el ID del registro insertado para Gemini
        record_id = cursor.lastrowid

        # Llamada a la función para enviar el contacto a EmailOctopus
        oct_response = add_contact_to_octopus(
            email_address=data["correo"],
            nombre_apellido=data["nombre_apellido"],
            empresa=data["empresa"],
            ruc_dni=data["ruc_dni"]
        )
        if oct_response.status_code not in [200, 201]:
            print("Error al agregar el contacto a Octopus:", oct_response.text)

        # NUEVA FUNCIONALIDAD: Enviar notificación de lead solo si es WIX
        try:
            # Preparar datos del lead para la notificación
            lead_notification_data = {
                'nombre_apellido': data["nombre_apellido"],
                'empresa': data["empresa"],
                'telefono2': data["telefono2"],
                'correo': data["correo"],
                'ruc_dni': data["ruc_dni"],
                'treq_requerimiento': data["treq_requerimiento"],
                'origen': "WIX",  # Siempre WIX para este endpoint
                'submission_time': 'Recién registrado'  # Se podría mejorar con timestamp real
            }
            
            # Enviar notificación (solo si origen=WIX, que es siempre true aquí)
            notification_result, notification_status = send_lead_notification_email(lead_notification_data)
            
            if notification_result['status'] == 'ok':
                print(f"✅ Notificación de lead WIX enviada: {notification_result['message']}")
            elif notification_result['status'] == 'error':
                print(f"❌ Error en notificación de lead: {notification_result['message']}")
            # Si es 'skipped', no se imprime nada (aunque no debería pasar aquí)
                
        except Exception as notification_error:
            # Error en notificación no debe afectar el flujo principal
            print(f"⚠️ Error al enviar notificación de lead WIX: {notification_error}")

        # ANÁLISIS AUTOMÁTICO CON GEMINI IA
        gemini_result = None
        try:
            lead_data_gemini = {
                'empresa': data["empresa"],
                'ruc_dni': data.get("ruc_dni"),
                'treq_requerimiento': data.get("treq_requerimiento"),
                'origen': "WIX"
            }

            gemini_result = analizar_lead_automatico(lead_data_gemini, record_id)

            if gemini_result.get('success'):
                print(f"✅ Análisis Gemini completado para lead {record_id}: siek_cliente={gemini_result.get('siek_cliente')}")
            else:
                print(f"⚠️ Análisis Gemini sin resultados: {gemini_result.get('error', 'Sin datos suficientes')}")

        except Exception as gemini_error:
            # Error en Gemini no debe afectar el flujo principal
            print(f"⚠️ Error en análisis Gemini (no crítico): {gemini_error}")

        # ENVÍO A SISTEMA EXTERNO (SINCRONIZACIÓN)
        sync_sent = False
        if record_id:
            try:
                sync_result = enviar_lead_a_sistema_externo(record_id)

                if sync_result.get('success'):
                    sync_sent = True
                    print(f"✅ Lead {record_id} enviado a sistema externo")
                elif sync_result.get('skipped'):
                    print(f"⏭️ Sincronización deshabilitada para lead {record_id}")
                else:
                    print(f"⚠️ Error al enviar lead {record_id} a sistema externo: {sync_result.get('message')}")

            except Exception as sync_error:
                # Error en sync no debe afectar el flujo principal
                print(f"⚠️ Error en sincronización (no crítico): {sync_error}")

        return jsonify({
            'status': 'success',
            'message': 'Registro insertado correctamente.',
            'record_id': record_id,
            'gemini_analyzed': gemini_result.get('success', False) if gemini_result else False,
            'sync_sent': sync_sent
        }), 201
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500
    finally:
        cursor.close()
        cnx.close()
