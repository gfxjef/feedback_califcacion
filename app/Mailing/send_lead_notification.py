import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    # Importaciones del paquete app (para Render/producción)
    from app.Mailing.lead_notification_template import create_lead_notification_email
except ImportError:
    # Importaciones relativas (para desarrollo con run_app.py)
    from Mailing.lead_notification_template import create_lead_notification_email


def send_lead_notification_email(lead_data):
    """
    Envía notificación por email cuando se recibe un nuevo lead.
    Funciona para cualquier origen - la lógica de cuándo enviar se controla desde el endpoint.

    Args:
        lead_data (dict): Datos del lead con campos:
            - nombre_apellido
            - empresa
            - telefono2
            - correo
            - ruc_dni
            - treq_requerimiento
            - origen
            - submission_time (opcional)

    Returns:
        dict: {'status': 'ok/error', 'message': str}, int (status_code)
    """
    
    # Notificación disponible para cualquier origen
    # La lógica de cuándo enviar se controla desde el endpoint que llama esta función
    
    # Verificar configuración de email
    sender_email = os.environ.get('EMAIL_USER')
    sender_password = os.environ.get('EMAIL_PASSWORD')
    notification_email = os.environ.get('LEAD_NOTIFICATION_EMAIL')
    
    if not all([sender_email, sender_password, notification_email]):
        print("❌ Error: Variables de entorno faltantes para notificación de leads")
        return {'status': 'error', 'message': 'Configuración de email incompleta para notificaciones'}, 500
    
    # Validar datos mínimos del lead
    required_fields = ['nombre_apellido', 'empresa', 'correo']
    for field in required_fields:
        if not lead_data.get(field):
            return {'status': 'error', 'message': f'Campo {field} faltante en datos del lead'}, 400
    
    try:
        # Generar HTML del email usando el template
        html_body = create_lead_notification_email(lead_data)
        
        # Configurar el mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🌟 Nuevo Lead ({lead_data.get('origen', 'UNKNOWN')}): {lead_data['nombre_apellido']} - {lead_data['empresa']}"
        msg['From'] = "Sistema Kossodo <jcamacho@kossodo.com>"
        msg['To'] = notification_email
        
        # Adjuntar HTML
        part_html = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part_html)
        
        # Enviar email
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [notification_email], msg.as_string())
        server.quit()
        
        print(f"✅ Notificación de lead {lead_data.get('origen', 'UNKNOWN')} enviada a {notification_email}")
        return {'status': 'ok', 'message': f'Notificación enviada correctamente a {notification_email}'}, 200
        
    except Exception as e:
        print(f"❌ Error enviando notificación de lead: {e}")
        return {'status': 'error', 'message': f'Error al enviar notificación: {str(e)}'}, 500


def validate_lead_notification_config():
    """
    Valida que las variables de entorno necesarias estén configuradas.
    
    Returns:
        dict: Status de la configuración
    """
    config_status = {
        'email_user': bool(os.environ.get('EMAIL_USER')),
        'email_password': bool(os.environ.get('EMAIL_PASSWORD')),
        'notification_email': bool(os.environ.get('LEAD_NOTIFICATION_EMAIL')),
    }
    
    config_status['ready'] = all(config_status.values())
    
    return config_status