#enviar_encuesta.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def enviar_encuesta(nombre_cliente, correo_cliente, asesor, numero_consulta):
    """
    Envía un correo con los enlaces de encuesta (Bueno, Regular, Malo).
    Retorna un dict con 'status' y 'message', y el código de estado HTTP.
    """
    # Validaciones básicas
    if not (nombre_cliente and correo_cliente and asesor and numero_consulta):
        return {'status': 'error', 'message': 'Faltan parámetros'}, 400

    # unique_id es el idcalificacion (quitando el prefijo CONS- de numero_consulta)
    unique_id = numero_consulta.replace("CONS-", "")

    # Construir el HTML del correo
    base_url = "https://gfxjef.pythonanywhere.com/calificacion_firma"
    link_bueno = f"{base_url}/encuesta?unique_id={unique_id}&calificacion=Bueno"
    link_regular = f"{base_url}/encuesta?unique_id={unique_id}&calificacion=Regular"
    link_malo = f"{base_url}/encuesta?unique_id={unique_id}&calificacion=Malo"

    html_body = f"""
    <div style="text-align: center; font-family: 'Roboto', sans-serif;">
      <p style="font-size: 44px; margin: 0 auto; max-width: 600px;
         background: linear-gradient(to right, #ef8e35, #67b098);
         -webkit-background-clip: text; color: transparent;">
        <strong>Califica su atención</strong>
      </p>
      <br>
      <p style="font-size: 14px; color: #4d4d4d; margin: 0 auto; max-width: 600px;">
        Hola {nombre_cliente},<br><br>
        Esperamos haber resuelto tus consultas de la mejor manera.
        Por favor, selecciona un rostro según cómo percibiste la atención recibida:
      </p>
      <div style="margin-top: 10px;">
        <a href="{link_bueno}" style="text-decoration: none;">
          <img src="https://kossodo.estilovisual.com/marketing/firmas/img/bueno.jpg" alt="Bueno" width="100">
        </a>
        <a href="{link_regular}" style="text-decoration: none;">
          <img src="https://kossodo.estilovisual.com/marketing/firmas/img/regular.jpg" alt="Regular" width="100">
        </a>
        <a href="{link_malo}" style="text-decoration: none;">
          <img src="https://kossodo.estilovisual.com/marketing/firmas/img/malo.jpg" alt="Malo" width="100">
        </a>
      </div>
    </div>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    """

    try:
        # Configuración SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "analista.mkt@kossodo.com"
        sender_password = "kfmklqrzzrengbhk"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Encuesta de Satisfacción - Consulta #{numero_consulta}"
        msg['From'] = sender_email
        msg['To'] = correo_cliente

        # Parte HTML
        part_html = MIMEText(html_body, 'html')
        msg.attach(part_html)

        # Enviar correo
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, correo_cliente, msg.as_string())
        server.quit()

        return {'status': 'ok', 'message': 'Encuesta enviada correctamente'}, 200

    except Exception as e:
        return {'status': 'error', 'message': f'Error al enviar el correo: {str(e)}'}, 500
