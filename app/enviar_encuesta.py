import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def enviar_encuesta(nombre_cliente, correo_cliente, asesor, numero_consulta):
    if not (nombre_cliente and correo_cliente and asesor and numero_consulta):
        return {'status': 'error', 'message': 'Faltan parámetros'}, 400

    unique_id = numero_consulta.replace("CONS-", "")
    base_url = "https://feedback-califcacion.onrender.com"
    link_bueno = f"{base_url}/encuesta?unique_id={unique_id}&calificacion=Bueno"
    link_regular = f"{base_url}/encuesta?unique_id={unique_id}&calificacion=Regular"
    link_malo = f"{base_url}/encuesta?unique_id={unique_id}&calificacion=Malo"

    html_body = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Encuesta de Satisfacción</title>
    </head>
    <body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, sans-serif;">
      <!-- Contenido del correo con imágenes y enlaces -->
      <!-- ... (contenido HTML igual al proporcionado anteriormente) ... -->
    </body>
    </html>
    """

    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.environ.get('EMAIL_USER')
        sender_password = os.environ.get('EMAIL_PASSWORD')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Encuesta de Satisfacción - Consulta #{numero_consulta}"
        msg['From'] = sender_email
        msg['To'] = correo_cliente

        part_html = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part_html)

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, correo_cliente, msg.as_string())
        server.quit()

        return {'status': 'ok', 'message': 'Encuesta enviada correctamente'}, 200
    except Exception as e:
        return {'status': 'error', 'message': f'Error al enviar el correo: {str(e)}'}, 500
