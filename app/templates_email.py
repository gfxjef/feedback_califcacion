"""
Templates de email para diferentes tipos de envío de encuestas
"""

def get_email_template_ventas(nombre_cliente, documento, base_url, unique_id, tipo):
    """Template de email para el área de Ventas"""
    
    # Preparar texto del número de documento
    documento_texto = ""
    if documento:
        documento_texto = f'<p style="font-size:19px; color:#6cb79a; margin:10px 0; font-weight:bold;">Número de orden de trabajo: {documento}</p>'

    html_body = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Encuesta de Satisfacción - Ventas</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, sans-serif;">
    <!-- Contenedor principal -->
    <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#f4f4f4" style="padding:0.5rem 0;">
        <tr>
            <td align="center" valign="top">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:700px; border:1px solid #ddd; background-color:#ffffff;">
                    <!-- Encabezado con imagen -->
                    <tr>
                        <td style="padding:0; margin:0;" align="center">
                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/mail_calif_1.webp"
                                alt="Header"
                                style="display:block; border:none; width:100%; max-width:100%; height:auto;">
                        </td>
                    </tr>
                    <!-- Saludo al usuario -->
                    <tr>
                        <td align="center" style="padding:20px;">
                            <h1 style="font-size: 24px; margin: 0; color:#3e4660;">
                                Hola, <span style="font-weight:bold; color:#3e4660;">{nombre_cliente}</span>
                            </h1>
                            {documento_texto}
                        </td>
                    </tr>
                    <!-- Imagen Opinión Importante -->
                    <tr>
                        <td align="center" style="padding:5px;">
                            <img src="http://atusaludlicoreria.com/feedback/opinion_importante.jpg"
                                 alt="Opinión Importante"
                                 style="display:block; border:none; width:auto; max-width:100%; height:auto;">
                        </td>
                    </tr>
                    <!-- Texto específico para Ventas -->
                    <tr>
                        <td align="center" style="padding:15px 20px;">
                            <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0; text-align:center;">
                                Su <strong>orden de trabajo</strong> ha sido creada y se encuentra en proceso de
                                atención. <strong>Valoramos su opinion</strong> y lo invitamos a seleccionar una de
                                las opciones para indicarnos cómo percibio nuestra atención.
                            </p>
                        </td>
                    </tr>
                    <!-- Escala de calificación 1-10 con imágenes individuales -->
                    <tr>
                        <td align="center" style="padding:0px 20px 20px 20px;">
                            <p style="font-size:18px; color:#3e4660; margin-bottom:15px; font-weight:bold;">
                                Realiza tu calificación del 1 al 10:
                            </p>
                            <!-- Etiquetas Nada/Bastante Satisfecho -->
                            <table border="0" cellspacing="0" cellpadding="0" style="width:100%; max-width:500px; margin:0 auto 10px auto;">
                                <tr>
                                    <td style="font-size:14px; color:#666; text-align:left;">Nada<br/>Satisfecho</td>
                                    <td style="font-size:14px; color:#666; text-align:right;">Bastante<br/>Satisfecho</td>
                                </tr>
                            </table>
                            <!-- Imágenes individuales clickeables -->
                            <table border="0" cellspacing="2" cellpadding="2" style="text-align:center; margin:0 auto;">
                                <tr>"""

    # Generar los 10 botones con imágenes individuales
    for i in range(1, 11):
        link = f"{base_url}/encuesta?unique_id={unique_id}&calificacion={i}&tipo={tipo}"
        html_body += f"""
                                    <td style="padding:1px;">
                                        <a href="{link}" target="_blank" style="text-decoration:none;">
                                            <img src="https://atusaludlicoreria.com/feedback/{i}.jpg" 
                                                 alt="Calificación {i}" 
                                                 title="Calificación {i}"
                                                 style="display:block; border:none; width:auto; height:auto; max-width:45px;">
                                        </a>
                                    </td>"""

    html_body += f"""
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Texto final común -->
                    <tr>
                        <td align="center" style="padding:20px;">
                            <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0 0 15px 0; text-align:center;">
                                En el Grupo Kossodo valoramos la comunicación interna
                                y extema. Por ello su retroalimentación es esencial para
                                seguir mejorando nuestros procesos.
                            </p>
                            <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0; text-align:center;">
                                Conozca más sobre nuestro
                                catálogo de productos y sercicios:
                            </p>
                        </td>
                    </tr>
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
                    <!-- Footer legal -->
                    <tr>
                        <td align="center" style="padding:20px 15px 15px 15px; border-top:1px solid #e0e0e0;">
                            <p style="font-size:11px; color:#999999; line-height:1.4; margin:0; text-align:center;">
                                Este correo ha sido enviado automáticamente por nuestro sistema. La información proporcionada será empleada exclusivamente para optimizar nuestra atención y canales de comunicación. Sus comentarios serán tratados con estricta confidencialidad y no compartidos con terceros sin su autorización. Por favor, no responda a este mensaje; no es monitoreado. Si requiere asistencia adicional, contáctenos en info@kossodo.com.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    return html_body


def get_email_template_operaciones(nombre_cliente, documento, base_url, unique_id, tipo):
    """Template de email para el área de Operaciones"""
    
    # Preparar texto del número de documento
    documento_texto = ""
    if documento:
        documento_texto = f'<p style="font-size:19px; color:#6cb79a; margin:10px 0; font-weight:bold;">Número de orden de trabajo: {documento}</p>'

    html_body = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Encuesta de Satisfacción - Operaciones</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, sans-serif;">
    <!-- Contenedor principal -->
    <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#f4f4f4" style="padding:0.5rem 0;">
        <tr>
            <td align="center" valign="top">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:700px; border:1px solid #ddd; background-color:#ffffff;">
                    <!-- Encabezado con imagen -->
                    <tr>
                        <td style="padding:0; margin:0;" align="center">
                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/mail_calif_1.webp"
                                alt="Header"
                                style="display:block; border:none; width:100%; max-width:100%; height:auto;">
                        </td>
                    </tr>
                    <!-- Saludo al usuario -->
                    <tr>
                        <td align="center" style="padding:20px;">
                            <h1 style="font-size: 24px; margin: 0; color:#3e4660;">
                                Hola, <span style="font-weight:bold; color:#3e4660;">{nombre_cliente}</span>
                            </h1>
                            {documento_texto}
                        </td>
                    </tr>
                    <!-- Imagen Opinión Importante -->
                    <tr>
                        <td align="center" style="padding:5px;">
                            <img src="http://atusaludlicoreria.com/feedback/opinion_importante.jpg"
                                 alt="Opinión Importante"
                                 style="display:block; border:none; width:auto; max-width:100%; height:auto;">
                        </td>
                    </tr>
                    <!-- Texto específico para Operaciones -->
                    <tr>
                        <td align="center" style="padding:15px 20px;">
                            <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0; text-align:center;">
                                Su <strong>orden de Trabajo</strong> ah sido culminada. <strong>Valoramos su
                                opinion</strong> y lo invitamos a seleccionar una de las opciones para
                                indicarnos córno percibio nuestra atención en este proceso.
                            </p>
                        </td>
                    </tr>
                    <!-- Escala de calificación 1-10 con imágenes individuales -->
                    <tr>
                        <td align="center" style="padding:0px 20px 20px 20px;">
                            <p style="font-size:18px; color:#3e4660; margin-bottom:15px; font-weight:bold;">
                                Realiza tu calificación del 1 al 10:
                            </p>
                            <!-- Etiquetas Nada/Bastante Satisfecho -->
                            <table border="0" cellspacing="0" cellpadding="0" style="width:100%; max-width:500px; margin:0 auto 10px auto;">
                                <tr>
                                    <td style="font-size:14px; color:#666; text-align:left;">Nada<br/>Satisfecho</td>
                                    <td style="font-size:14px; color:#666; text-align:right;">Bastante<br/>Satisfecho</td>
                                </tr>
                            </table>
                            <!-- Imágenes individuales clickeables -->
                            <table border="0" cellspacing="2" cellpadding="2" style="text-align:center; margin:0 auto;">
                                <tr>"""

    # Generar los 10 botones con imágenes individuales
    for i in range(1, 11):
        link = f"{base_url}/encuesta?unique_id={unique_id}&calificacion={i}&tipo={tipo}"
        html_body += f"""
                                    <td style="padding:1px;">
                                        <a href="{link}" target="_blank" style="text-decoration:none;">
                                            <img src="https://atusaludlicoreria.com/feedback/{i}.jpg" 
                                                 alt="Calificación {i}" 
                                                 title="Calificación {i}"
                                                 style="display:block; border:none; width:auto; height:auto; max-width:45px;">
                                        </a>
                                    </td>"""

    html_body += f"""
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Texto final común -->
                    <tr>
                        <td align="center" style="padding:20px;">
                            <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0 0 15px 0; text-align:center;">
                                En el Grupo Kossodo valoramos la comunicación interna
                                y extema. Por ello su retroalimentación es esencial para
                                seguir mejorando nuestros procesos.
                            </p>
                            <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0; text-align:center;">
                                Conozca más sobre nuestro
                                catálogo de productos y sercicios:
                            </p>
                        </td>
                    </tr>
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
                    <!-- Footer legal -->
                    <tr>
                        <td align="center" style="padding:20px 15px 15px 15px; border-top:1px solid #e0e0e0;">
                            <p style="font-size:11px; color:#999999; line-height:1.4; margin:0; text-align:center;">
                                Este correo ha sido enviado automáticamente por nuestro sistema. La información proporcionada será empleada exclusivamente para optimizar nuestra atención y canales de comunicación. Sus comentarios serán tratados con estricta confidencialidad y no compartidos con terceros sin su autorización. Por favor, no responda a este mensaje; no es monitoreado. Si requiere asistencia adicional, contáctenos en info@kossodo.com.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    return html_body


def get_email_template_coordinador(nombre_cliente, documento, base_url, unique_id, tipo):
    """Template de email para Coordinador (Conformidad) - mantiene diseño original"""
    
    # Preparar texto del número de documento
    documento_texto = ""
    if documento:
        documento_texto = f'<p style="font-size:19px; color:#6cb79a; margin:10px 0; font-weight:bold;">Número de orden de trabajo: {documento}</p>'

    html_body = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Encuesta de Satisfacción - Coordinación</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, sans-serif;">
    <!-- Contenedor principal -->
    <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#f4f4f4" style="padding:0.5rem 0;">
        <tr>
            <td align="center" valign="top">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:700px; border:1px solid #ddd; background-color:#ffffff;">
                    <!-- Encabezado con imagen -->
                    <tr>
                        <td style="padding:0; margin:0;" align="center">
                            <img src="https://kossodo.estilovisual.com/marketing/calificacion/mail_calif_1.webp"
                                alt="Header"
                                style="display:block; border:none; width:100%; max-width:100%; height:auto;">
                        </td>
                    </tr>
                    <!-- Saludo al usuario -->
                    <tr>
                        <td align="center" style="padding:20px;">
                            <h1 style="font-size: 24px; margin: 0; color:#3e4660;">
                                Hola, <span style="font-weight:bold; color:#3e4660;">{nombre_cliente}</span>
                            </h1>
                            {documento_texto}
                        </td>
                    </tr>
                    <!-- Imagen Opinión Importante -->
                    <tr>
                        <td align="center" style="padding:5px;">
                            <img src="http://atusaludlicoreria.com/feedback/opinion_importante.jpg"
                                 alt="Opinión Importante"
                                 style="display:block; border:none; width:auto; max-width:100%; height:auto;">
                        </td>
                    </tr>
                    <!-- Texto específico para Coordinador -->
                    <tr>
                        <td align="center" style="padding:15px 20px;">"""

    # Texto específico según el tipo
    if tipo == "Ventas (OC)":
        texto_especifico = """Su <strong>orden de compra</strong> ha sido creada y se encuentra en proceso de
                            atención. <strong>Valoramos su opinion</strong> y lo invitamos a seleccionar una de
                            las opciones para indicarnos cómo percibio nuestra atención."""
    else:
        texto_especifico = """<strong>Valoramos su opinion</strong> y lo invitamos a seleccionar una de
                            las opciones para indicarnos cómo percibio nuestro servicio."""

    html_body += f"""
                            <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0; text-align:center;">
                                {texto_especifico}
                            </p>
                        </td>
                    </tr>
                    <!-- Escala de calificación 1-10 con imágenes individuales -->
                    <tr>
                        <td align="center" style="padding:0px 20px 20px 20px;">
                            <p style="font-size:18px; color:#3e4660; margin-bottom:15px; font-weight:bold;">
                                Realiza tu calificación del 1 al 10:
                            </p>
                            <!-- Etiquetas Nada/Bastante Satisfecho -->
                            <table border="0" cellspacing="0" cellpadding="0" style="width:100%; max-width:500px; margin:0 auto 10px auto;">
                                <tr>
                                    <td style="font-size:14px; color:#666; text-align:left;">Nada<br/>Satisfecho</td>
                                    <td style="font-size:14px; color:#666; text-align:right;">Bastante<br/>Satisfecho</td>
                                </tr>
                            </table>
                            <!-- Imágenes individuales clickeables -->
                            <table border="0" cellspacing="2" cellpadding="2" style="text-align:center; margin:0 auto;">
                                <tr>"""

    # Generar los 10 botones con imágenes individuales
    for i in range(1, 11):
        link = f"{base_url}/encuesta?unique_id={unique_id}&calificacion={i}&tipo={tipo}"
        html_body += f"""
                                    <td style="padding:1px;">
                                        <a href="{link}" target="_blank" style="text-decoration:none;">
                                            <img src="https://atusaludlicoreria.com/feedback/{i}.jpg" 
                                                 alt="Calificación {i}" 
                                                 title="Calificación {i}"
                                                 style="display:block; border:none; width:auto; height:auto; max-width:45px;">
                                        </a>
                                    </td>"""

    html_body += f"""
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Texto final común -->
                    <tr>
                        <td align="center" style="padding:20px;">
                            <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0 0 15px 0; text-align:center;">
                                En el Grupo Kossodo valoramos la comunicación interna
                                y extema. Por ello su retroalimentación es esencial para
                                seguir mejorando nuestros procesos.
                            </p>
                            <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0; text-align:center;">
                                Conozca más sobre nuestro
                                catálogo de productos y sercicios:
                            </p>
                        </td>
                    </tr>
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
                    <!-- Footer legal -->
                    <tr>
                        <td align="center" style="padding:20px 15px 15px 15px; border-top:1px solid #e0e0e0;">
                            <p style="font-size:11px; color:#999999; line-height:1.4; margin:0; text-align:center;">
                                Este correo ha sido enviado automáticamente por nuestro sistema. La información proporcionada será empleada exclusivamente para optimizar nuestra atención y canales de comunicación. Sus comentarios serán tratados con estricta confidencialidad y no compartidos con terceros sin su autorización. Por favor, no responda a este mensaje; no es monitoreado. Si requiere asistencia adicional, contáctenos en info@kossodo.com.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    return html_body


def get_email_template_lamentamos_ventas(nombre_cliente, documento, base_url, unique_id, tipo):
    """Template de email para Ventas cuando la calificación es baja (1-3)"""
    
    # Preparar texto del documento
    documento_texto = f'<p style="color:#6cb79a; font-size:19px; font-weight:bold; margin:15px 0; text-align:center;">Número de orden de trabajo: {documento}</p>' if documento else ""
    
    html_body = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Queremos Mejorar - Ventas</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, sans-serif;">
    <!-- Contenedor principal -->
    <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#f4f4f4" style="padding:0.5rem 0;">
        <tr>
            <td align="center" valign="top">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:700px; border:1px solid #ddd; background-color:#ffffff;">
                    <!-- Encabezado con imagen -->
                    <tr>
                        <td style="padding:0; margin:0;" align="center">
                            <img src="https://atusaludlicoreria.com/feedback/calif_reg.jpg"
                                alt="Header"
                                style="display:block; border:none; width:100%; max-width:100%; height:auto;">
                        </td>
                    </tr>
                    <!-- Texto principal -->
                    <tr>
                        <td align="center" style="padding:25px 20px 15px 20px;">
                            <div style="width:80%; margin:0 auto;">
                                <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0; text-align:center;">
                                    En <strong>Grupo Kossodo</strong> nos interesa conocer su experiencia. Sus
                                    comentarios son esenciales para <strong>mejorar la calidad de
                                    nuestro servicio</strong>. Por favor, seleccione cuál de los siguientes
                                    procesos motivó su calificación:
                                </p>
                            </div>
                        </td>
                    </tr>
                    <!-- Número de orden -->
                    <tr>
                        <td align="center" style="padding:0px 20px 15px 20px;">
                            {documento_texto}
                        </td>
                    </tr>
                    <!-- Botones de feedback específicos para Ventas -->
                    <tr>
                        <td align="center" style="padding:0px 20px 20px 20px;">
                            <table border="0" cellspacing="3" cellpadding="5" style="margin:0 auto;">
                                <tr>
                                    <td>
                                        <a href="{base_url}/feedback_especifico?unique_id={unique_id}&tipo={tipo}&motivo=falta_informacion" 
                                           style="display:block; background-color:#e8e8e8; color:#555; padding:15px 20px; text-decoration:none; border-radius:25px; text-align:center; font-size:20px; margin:2px 0;">
                                            Falta de información sobre servicios
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <a href="{base_url}/feedback_especifico?unique_id={unique_id}&tipo={tipo}&motivo=demora_respuesta" 
                                           style="display:block; background-color:#e8e8e8; color:#555; padding:15px 20px; text-decoration:none; border-radius:25px; text-align:center; font-size:20px; margin:2px 0;">
                                            Demora en respuesta a consultas
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <a href="{base_url}/feedback_especifico?unique_id={unique_id}&tipo={tipo}&motivo=presion_venta" 
                                           style="display:block; background-color:#e8e8e8; color:#555; padding:15px 20px; text-decoration:none; border-radius:25px; text-align:center; font-size:20px; margin:2px 0;">
                                            Sensación de presión en la venta
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <a href="{base_url}/feedback_especifico?unique_id={unique_id}&tipo={tipo}&motivo=incapacidad_resolver" 
                                           style="display:block; background-color:#e8e8e8; color:#555; padding:15px 20px; text-decoration:none; border-radius:25px; text-align:center; font-size:20px; margin:2px 0;">
                                            Incapacidad para resolver dudas
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Texto de agradecimiento -->
                    <tr>
                        <td align="center" style="padding:20px;">
                            <div style="width:80%; margin:0 auto;">
                                <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0; text-align:center;">
                                    Agradecemos el tiempo dedicado a compartir su
                                    opinión. Sus comentarios serán revisados por nuestro
                                    equipo para optimizar cada etapa de atención.
                                </p>
                            </div>
                        </td>
                    </tr>
                    <!-- Footer legal -->
                    <tr>
                        <td align="center" style="padding:20px 15px 15px 15px; border-top:1px solid #e0e0e0;">
                            <p style="font-size:11px; color:#999999; line-height:1.4; margin:0; text-align:center;">
                                Este correo ha sido enviado automáticamente por nuestro sistema. La información proporcionada será empleada exclusivamente para optimizar nuestra atención y canales de comunicación. Sus comentarios serán tratados con estricta confidencialidad y no compartidos con terceros sin su autorización. Por favor, no responda a este mensaje; no es monitoreado. Si requiere asistencia adicional, contáctenos en info@kossodo.com.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    return html_body


def get_email_template_lamentamos_operaciones(nombre_cliente, documento, base_url, unique_id, tipo):
    """Template de email para Operaciones cuando la calificación es baja (1-3)"""
    
    # Preparar texto del documento
    documento_texto = f'<p style="color:#6cb79a; font-size:19px; font-weight:bold; margin:15px 0; text-align:center;">Número de orden: {documento}</p>' if documento else ""
    
    html_body = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Queremos Mejorar - Operaciones</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, sans-serif;">
    <!-- Contenedor principal -->
    <table width="100%" border="0" cellspacing="0" cellpadding="0" bgcolor="#f4f4f4" style="padding:0.5rem 0;">
        <tr>
            <td align="center" valign="top">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:700px; border:1px solid #ddd; background-color:#ffffff;">
                    <!-- Encabezado con imagen -->
                    <tr>
                        <td style="padding:0; margin:0;" align="center">
                            <img src="https://atusaludlicoreria.com/feedback/calif_reg.jpg"
                                alt="Header"
                                style="display:block; border:none; width:100%; max-width:100%; height:auto;">
                        </td>
                    </tr>
                    <!-- Texto principal -->
                    <tr>
                        <td align="center" style="padding:25px 20px 15px 20px;">
                            <div style="width:80%; margin:0 auto;">
                                <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0; text-align:center;">
                                    En <strong>Grupo Kossodo</strong> nos interesa conocer su experiencia. Sus
                                    comentarios son esenciales para <strong>mejorar la calidad de
                                    nuestro servicio</strong>. Por favor, seleccione cuál de los siguientes
                                    procesos motivó su calificación:
                                </p>
                            </div>
                        </td>
                    </tr>
                    <!-- Número de orden -->
                    <tr>
                        <td align="center" style="padding:0px 20px 15px 20px;">
                            {documento_texto}
                        </td>
                    </tr>
                    <!-- Botones de feedback específicos para Operaciones -->
                    <tr>
                        <td align="center" style="padding:0px 20px 20px 20px;">
                            <table border="0" cellspacing="3" cellpadding="5" style="margin:0 auto;">
                                <tr>
                                    <td>
                                        <a href="{base_url}/feedback_especifico?unique_id={unique_id}&tipo={tipo}&motivo=comunicacion_deficiente" 
                                           style="display:block; background-color:#e8e8e8; color:#555; padding:15px 20px; text-decoration:none; border-radius:25px; text-align:center; font-size:20px; margin:2px 0;">
                                            Comunicación deficiente para coordinar servicio
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <a href="{base_url}/feedback_especifico?unique_id={unique_id}&tipo={tipo}&motivo=fecha_lejana" 
                                           style="display:block; background-color:#e8e8e8; color:#555; padding:15px 20px; text-decoration:none; border-radius:25px; text-align:center; font-size:20px; margin:2px 0;">
                                            Fecha disponible muy lejana
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <a href="{base_url}/feedback_especifico?unique_id={unique_id}&tipo={tipo}&motivo=incumplimiento_fecha" 
                                           style="display:block; background-color:#e8e8e8; color:#555; padding:15px 20px; text-decoration:none; border-radius:25px; text-align:center; font-size:20px; margin:2px 0;">
                                            Incumplimiento de fecha acordada
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <a href="{base_url}/feedback_especifico?unique_id={unique_id}&tipo={tipo}&motivo=atencion_insatisfactoria" 
                                           style="display:block; background-color:#e8e8e8; color:#555; padding:15px 20px; text-decoration:none; border-radius:25px; text-align:center; font-size:20px; margin:2px 0;">
                                            Atención técnica insatisfactoria
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <a href="{base_url}/feedback_especifico?unique_id={unique_id}&tipo={tipo}&motivo=demora_informes" 
                                           style="display:block; background-color:#e8e8e8; color:#555; padding:15px 20px; text-decoration:none; border-radius:25px; text-align:center; font-size:20px; margin:2px 0;">
                                            Demora en la entrega de informes
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <a href="{base_url}/feedback_especifico?unique_id={unique_id}&tipo={tipo}&motivo=demora_consultas" 
                                           style="display:block; background-color:#e8e8e8; color:#555; padding:15px 20px; text-decoration:none; border-radius:25px; text-align:center; font-size:20px; margin:2px 0;">
                                            Demora en la Respuestas a consultas técnicas
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Texto de agradecimiento -->
                    <tr>
                        <td align="center" style="padding:20px;">
                            <div style="width:80%; margin:0 auto;">
                                <p style="font-size:18px; color:#2b3352; line-height:1.2; letter-spacing:-0.3px; margin:0; text-align:center;">
                                    Agradecemos el tiempo dedicado a compartir su
                                    opinión. Sus comentarios serán revisados por nuestro
                                    equipo para optimizar cada etapa de atención.
                                </p>
                            </div>
                        </td>
                    </tr>
                    <!-- Footer legal -->
                    <tr>
                        <td align="center" style="padding:20px 15px 15px 15px; border-top:1px solid #e0e0e0;">
                            <p style="font-size:11px; color:#999999; line-height:1.4; margin:0; text-align:center;">
                                Este correo ha sido enviado automáticamente por nuestro sistema. La información proporcionada será empleada exclusivamente para optimizar nuestra atención y canales de comunicación. Sus comentarios serán tratados con estricta confidencialidad y no compartidos con terceros sin su autorización. Por favor, no responda a este mensaje; no es monitoreado. Si requiere asistencia adicional, contáctenos en info@kossodo.com.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    
    return html_body