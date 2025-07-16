import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from templates_email import (
    get_email_template_ventas, 
    get_email_template_operaciones, 
    get_email_template_coordinador
)

def enviar_encuesta(nombre_cliente, correo_cliente, asesor, numero_consulta, tipo, documento=None):
    """
    Envía un correo con escala de calificación del 1 al 10.
    Retorna un dict con 'status' y 'message', y el código de estado HTTP.
    """
    # Validaciones básicas
    if not (nombre_cliente and correo_cliente and asesor and numero_consulta):
        return {'status': 'error', 'message': 'Faltan parámetros'}, 400

    # --- NUEVA SECCIÓN: Procesar correos y validación de dominios internos ---
    email_list = [email.strip() for email in correo_cliente.split(',') if email.strip()]

    # Si alguno de los correos es de dominio interno, no se envía el correo
    forbidden_domains = ["@kossodo.com", "@kossomet.com", "@universocientifico.com"]
    for email in email_list:
        for domain in forbidden_domains:
            if email.lower().endswith(domain):
                return {'status': 'ok', 'message': 'No se envió correo para correos internos'}, 200
    # -------------------------------------------------------------------------

    # --- FILTRO DE TESTING: Solo enviar emails a gfxjef@gmail.com ---
    EMAIL_TESTING = "gfxjef@gmail.com"
    
    # Verificar si algún email en la lista es el email de testing
    emails_validos_testing = [email for email in email_list if email.lower() == EMAIL_TESTING.lower()]
    
    if not emails_validos_testing:
        # Si ningún email es de testing, simular envío exitoso sin enviar realmente
        print(f"🚧 MODO TESTING: Email NO enviado a {correo_cliente} (solo se envía a {EMAIL_TESTING})")
        return {'status': 'ok', 'message': f'Email simulado correctamente (modo testing - solo se envía a {EMAIL_TESTING})'}, 200
    else:
        # Solo procesar el email de testing
        email_list = emails_validos_testing
        print(f"✅ MODO TESTING: Email SÍ se enviará a {EMAIL_TESTING}")
    # -------------------------------------------------------------------------

    # Extraer el unique_id desde el número de consulta (ej: "CONS-000123")
    unique_id = numero_consulta.replace("CONS-", "")

    # URL base donde se ubica el endpoint /encuesta
    base_url = "https://feedback-califcacion.onrender.com"

    # Generar el HTML según el tipo de envío usando templates separados
    if tipo == "Ventas" or tipo == "Ventas (OT)" or tipo == "Ventas (OC)":
        html_body = get_email_template_ventas(nombre_cliente, documento, base_url, unique_id, tipo)
    elif tipo == "Operaciones":
        html_body = get_email_template_operaciones(nombre_cliente, documento, base_url, unique_id, tipo)
    elif tipo == "Coordinador (Conformidad)" or tipo == "Entregado":
        html_body = get_email_template_coordinador(nombre_cliente, documento, base_url, unique_id, tipo)
    else:
        # Template por defecto (Coordinador)
        html_body = get_email_template_coordinador(nombre_cliente, documento, base_url, unique_id, tipo)

    try:
        # Configuración SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.environ.get('EMAIL_USER')      # Usuario SMTP
        sender_password = os.environ.get('EMAIL_PASSWORD')  # Contraseña SMTP

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Encuesta de Satisfacción - Consulta #{numero_consulta}"
        msg['From'] = "Kossodo S.A.C. <jcamacho@kossodo.com>"
        msg['To'] = ", ".join(email_list)

        part_html = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part_html)

        # Enviar correo a la lista de correos
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email_list, msg.as_string())
        server.quit()

        return {'status': 'ok', 'message': 'Encuesta enviada correctamente'}, 200

    except Exception as e:
        return {'status': 'error', 'message': f'Error al enviar el correo: {str(e)}'}, 500
