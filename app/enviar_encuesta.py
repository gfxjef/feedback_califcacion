import os
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

    unique_id = numero_consulta.replace("CONS-", "")
    base_url = "https://gfxjef.pythonanywhere.com/calificacion_firma"
    
    # Generar enlaces
    link_bueno = f"{base_url}/encuesta?unique_id={unique_id}&calificacion=Bueno"
    link_regular = f"{base_url}/encuesta?unique_id={unique_id}&calificacion=Regular"
    link_malo = f"{base_url}/encuesta?unique_id={unique_id}&calificacion=Malo"

    # Construir el HTML del correo
    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mailing Layout</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 1rem;
            }}

            .container {{
                width: 700px;
                background-color: white;
                border: 1px solid #ddd;
                margin: 0 auto;
            }}

            .header {{
                text-align: center;
                padding: 0;
                background-color: white;
            }}

            .header img {{
                width: 100%;
                height: auto;
                display: block;
            }}

            .body {{
                padding: 0;
                background-color: white;
                text-align: center;
            }}

            .usuario {{
                text-align: center;
                font-size: 2rem;
                background-color: white;
                padding: 20px 0;
            }}

            .usuario b {{
                font-weight: bold;
                background: linear-gradient(to right, #6ab79d, #3a4263, #ef8535);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                color: transparent;
            }}

            .texto {{
                text-align: center;
                margin: 20px 0;
            }}

            .votacion {{
                display: inline-flex;
                justify-content: center;
                align-items: center;
                gap: 0;
                background-color: white;
                padding: 0;
                margin: 0 auto;
            }}

            .votacion a {{
                display: block;
                text-align: center;
                width: 133px; /* Ajustado para que los tres botones ocupen exactamente 400px */
                padding: 0;
                margin: 0;
            }}

            .votacion img {{
                width: 100%;
                height: auto;
                cursor: pointer;
                transition: transform 0.3s ease;
                display: block;
                margin: 0;
                padding: 0;
            }}

            .votacion img:hover {{
                transform: scale(1.1);
            }}

            .extras img, .marcas img {{
                width: 100%;
                height: auto;
                display: block;
            }}

            .marcas {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 0;
                gap: 0;
                background-color: white;
            }}

            @media (max-width: 600px) {{
                .container {{
                    width: 100%;
                }}
                
                .votacion {{
                    width: 100%;
                }}
                
                .votacion a {{
                    width: 33.33%;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://kossodo.estilovisual.com/marketing/calificacion/califiac.png" alt="Header">
            </div>
            <div class="body">
                <div class="usuario">
                    <p>Hola, <b>{nombre_cliente}</b></p>
                </div>
                <div class="texto">
                    <img src="https://kossodo.estilovisual.com/marketing/calificacion/esperamos.jpg" alt="Mensaje">
                </div>
                <div class="votacion">
                    <a href="{link_bueno}">
                        <img src="https://kossodo.estilovisual.com/marketing/firmas/img/bueno.jpg" alt="Bueno">
                    </a>
                    <a href="{link_regular}">
                        <img src="https://kossodo.estilovisual.com/marketing/firmas/img/regular.jpg" alt="Regular">
                    </a>
                    <a href="{link_malo}">
                        <img src="https://kossodo.estilovisual.com/marketing/firmas/img/malo.jpg" alt="Malo">
                    </a>
                </div>
                <div class="extras">
                    <img src="https://kossodo.estilovisual.com/marketing/calificacion/back1.jpg" alt="Extras">
                </div>
                <div class="marcas">
                    <div class="izquierda">
                        <a href="https://www.kossodo.com" target="_blank">
                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/back2d.jpg" alt="Marcas">
                        </a>
                    </div>
                    <div class="derecha">
                        <a href="https://www.kossomet.com" target="_blank">
                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/back2.jpg" alt="Marcas">
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        # Configuración SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.environ.get('EMAIL_USER')
        sender_password = os.environ.get('EMAIL_PASSWORD')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Encuesta de Satisfacción - Consulta #{numero_consulta}"
        msg['From'] = sender_email
        msg['To'] = correo_cliente

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