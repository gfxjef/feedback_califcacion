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

    # Construir el HTML del correo (estructura con tablas para mejor compatibilidad)
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
    
    <!-- Contenedor principal -->
    <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#f4f4f4" style="padding:1rem 0;">
        <tr>
            <td align="center" valign="top">
                <table width="700" border="0" cellspacing="0" cellpadding="0" style="border:1px solid #ddd; background-color:#ffffff;">
                    <!-- Encabezado con imagen -->
                    <tr>
                        <td style="padding:0; margin:0;" align="center">
                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/mail_calif_1.webp"
                                alt="Header"
                                style="display:block; border:none; width:700px; max-width:700px; height:auto;">
                        </td>
                    </tr>

                    <!-- Saludo al usuario -->
                    <tr>
                        <td align="center" style="padding:20px;">
                            <h1 style="font-size: 24px; margin: 0; color:#000;">
                                Hola, <span style="font-weight:bold; background: -webkit-linear-gradient(#6ab79d, #3a4263, #ef8535); -webkit-background-clip: text; -webkit-text-fill-color: transparent; color: transparent;">
                                    {nombre_cliente}
                                </span>
                            </h1>
                        </td>
                    </tr>

                    <!-- Texto / Imagen de mensaje -->
                    <tr>
                        <td align="center" style="padding:10px;">
                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/mail_calif_2.webp"
                                 alt="Mensaje"
                                 style="display:block; border:none; width:700px; max-width:90%; height:auto;">
                        </td>
                    </tr>

                    <!-- Bloque de votación -->
                    <tr>
                        <td align="center" style="padding:10px;">
                            <table border="0" cellspacing="0" cellpadding="0" style="text-align:center;">
                                <tr>
                                    <td>
                                        <a href="{link_bueno}" target="_blank" style="text-decoration:none;">
                                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/bueno.webp"
                                                 alt="Bueno"
                                                 style="display:block; border:none; width:133px; height:auto; margin:0 auto;">
                                        </a>
                                    </td>
                                    <td>
                                        <a href="{link_regular}" target="_blank" style="text-decoration:none;">
                                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/regular.webp"
                                                 alt="Regular"
                                                 style="display:block; border:none; width:133px; height:auto; margin:0 auto;">
                                        </a>
                                    </td>
                                    <td>
                                        <a href="{link_malo}" target="_blank" style="text-decoration:none;">
                                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/malo.webp"
                                                 alt="Malo"
                                                 style="display:block; border:none; width:133px; height:auto; margin:0 auto;">
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Imagen extra -->
                    <tr>
                        <td align="center" style="padding:0;">
                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/mail_calif_3.webp"
                                 alt="Extras"
                                 style="display:block; border:none; width:700px; max-width:700px; height:auto;">
                        </td>
                    </tr>

                    <!-- Bloque de marcas: dos columnas -->
                    <tr>
                        <td align="center" style="padding:0;">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="text-align:center;">
                                <tr>
                                    <td width="50%" valign="top" style="padding:0;">
                                        <a href="https://www.kossodo.com" target="_blank" style="text-decoration:none;">
                                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/mail_calif_4.webp"
                                                 alt="Marcas 1"
                                                 style="display:block; border:none; width:100%; height:auto;">
                                        </a>
                                    </td>
                                    <td width="50%" valign="top" style="padding:0;">
                                        <a href="https://www.kossomet.com" target="_blank" style="text-decoration:none;">
                                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/mail_calif_5.webp"
                                                 alt="Marcas 2"
                                                 style="display:block; border:none; width:100%; height:auto;">
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                </table> <!-- Fin contenedor interno (700px) -->
            </td>
        </tr>
    </table> <!-- Fin contenedor principal -->
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

        part_html = MIMEText(html_body, 'html', 'utf-8')
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
