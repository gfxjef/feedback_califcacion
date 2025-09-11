"""
Template HTML profesional para notificaciones de nuevos leads WIX.
"""

def create_lead_notification_email(lead_data: dict) -> str:
    """
    Crea el HTML del correo para notificación de nuevo lead WIX.
    
    Args:
        lead_data (dict): Datos del lead desde formulario WIX
        
    Returns:
        str: HTML del correo formateado
    """
    
    # Formatear datos del lead de forma segura
    nombre_cliente = lead_data.get('nombre_apellido', 'Cliente')
    empresa = lead_data.get('empresa', 'No especificada')
    telefono = lead_data.get('telefono2', 'No especificado')
    correo = lead_data.get('correo', 'No especificado')
    ruc_dni = lead_data.get('ruc_dni', 'No especificado')
    requerimiento = lead_data.get('treq_requerimiento', 'No especificado')
    origen = lead_data.get('origen', 'WIX')
    fecha_submission = lead_data.get('submission_time', 'No especificada')
    
    # Template HTML optimizado para clientes de email
    html_template = f"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="es">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nuevo Lead WIX: {nombre_cliente}</title>
        <!--[if mso]>
        <noscript>
            <xml>
                <o:OfficeDocumentSettings>
                    <o:AllowPNG/>
                    <o:PixelsPerInch>96</o:PixelsPerInch>
                </o:OfficeDocumentSettings>
            </xml>
        </noscript>
        <![endif]-->
    </head>
    <body style="margin:0;padding:0;background-color:#f8f9fa;font-family:Arial,sans-serif;">
        <!-- Wrapper table para centrar el contenido -->
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0;padding:0;background-color:#f8f9fa;">
            <tr>
                <td align="center" valign="top" style="padding:20px 0;">
                    <!-- Contenedor principal de 600px -->
                    <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                        <!-- Header con imagen -->
                        <tr>
                            <td style="padding:0;text-align:center">
                                <img src="https://redkossodo.s3.us-east-2.amazonaws.com/extras/headmail.png" 
                                     alt="Header Kossodo" 
                                     style="width:100%;max-width:600px;height:auto;display:block;margin:0;">
                            </td>
                        </tr>
                        
                        <!-- Título principal -->
                        <tr>
                            <td style="padding:30px 40px 20px 40px;">
                                <h1 style="margin:0;color:#2e3954;font-size:28px;font-weight:bold;line-height:1.3;font-family:Arial,sans-serif;text-align:center;">
                                    🌟 Nuevo Lead desde WIX
                                </h1>
                            </td>
                        </tr>
                        
                        <!-- Saludo personalizado -->
                        <tr>
                            <td style="padding:0 40px 25px 40px;">
                                <p style="margin:0;color:#555;font-size:18px;line-height:1.6;font-family:Arial,sans-serif;">
                                    Hola,
                                </p>
                                <p style="margin:15px 0 0 0;color:#555;font-size:16px;line-height:1.6;font-family:Arial,sans-serif;">
                                    Se ha recibido un nuevo lead desde el formulario WIX. A continuación encontrarás toda la información del cliente para su asignación:
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Información del lead -->
                        <tr>
                            <td style="padding:0 40px 30px 40px;">
                                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f8f9fa;border-radius:8px;padding:25px;">
                                    <tr>
                                        <td style="padding:0;">
                                            <h2 style="margin:0 0 20px 0;color:#2e3954;font-size:20px;font-weight:bold;font-family:Arial,sans-serif;">
                                                📋 Información del Cliente
                                            </h2>
                                            
                                            <!-- Datos del cliente en formato table -->
                                            <table role="presentation" width="100%" cellpadding="8" cellspacing="0" border="0" style="font-family:Arial,sans-serif;">
                                                <tr>
                                                    <td style="width:35%;color:#666;font-weight:600;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        👤 Cliente:
                                                    </td>
                                                    <td style="color:#333;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        <strong>{nombre_cliente}</strong>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="color:#666;font-weight:600;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        🏢 Empresa:
                                                    </td>
                                                    <td style="color:#333;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        {empresa}
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="color:#666;font-weight:600;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        📞 Teléfono:
                                                    </td>
                                                    <td style="color:#333;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        <a href="tel:{telefono}" style="color:#2e3954;text-decoration:none;">{telefono}</a>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="color:#666;font-weight:600;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        ✉️ Email:
                                                    </td>
                                                    <td style="color:#333;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        <a href="mailto:{correo}" style="color:#2e3954;text-decoration:none;">{correo}</a>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="color:#666;font-weight:600;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        📄 RUC/DNI:
                                                    </td>
                                                    <td style="color:#333;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        {ruc_dni}
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="color:#666;font-weight:600;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        🌐 Origen:
                                                    </td>
                                                    <td style="color:#333;font-size:14px;border-bottom:1px solid #e9ecef;padding:12px 0;">
                                                        <span style="background-color:#28a745;color:white;padding:3px 8px;border-radius:4px;font-size:12px;font-weight:bold;">{origen}</span>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="color:#666;font-weight:600;font-size:14px;padding:12px 0;">
                                                        📅 Fecha:
                                                    </td>
                                                    <td style="color:#333;font-size:14px;padding:12px 0;">
                                                        {fecha_submission}
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Requerimiento del cliente -->
                        <tr>
                            <td style="padding:0 40px 30px 40px;">
                                <div style="background-color:#fff3cd;border-left:4px solid #ffc107;padding:20px;border-radius:0 8px 8px 0;">
                                    <h3 style="margin:0 0 10px 0;color:#856404;font-size:16px;font-weight:bold;font-family:Arial,sans-serif;">
                                        💼 Requerimiento del Cliente
                                    </h3>
                                    <p style="margin:0;color:#856404;font-size:14px;line-height:1.5;font-family:Arial,sans-serif;">
                                        {requerimiento}
                                    </p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Instrucciones de asignación -->
                        <tr>
                            <td style="padding:0 40px 30px 40px;">
                                <div style="background-color:#d1ecf1;border-left:4px solid #17a2b8;padding:20px;border-radius:0 8px 8px 0;text-align:center;">
                                    <h3 style="margin:0 0 10px 0;color:#0c5460;font-size:16px;font-weight:bold;font-family:Arial,sans-serif;">
                                        📌 Acción Requerida
                                    </h3>
                                    <p style="margin:0;color:#0c5460;font-size:14px;font-weight:500;font-family:Arial,sans-serif;">
                                        Por favor, asigna este lead al asesor correspondiente según el tipo de requerimiento y la disponibilidad del equipo.
                                    </p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Mensaje motivacional -->
                        <tr>
                            <td style="padding:0 40px 30px 40px;">
                                <div style="background-color:#d4edda;border-left:4px solid #28a745;padding:20px;border-radius:0 8px 8px 0;text-align:center;">
                                    <p style="margin:0;color:#155724;font-size:16px;font-weight:500;font-family:Arial,sans-serif;">
                                        🚀 ¡Nuevo cliente potencial! Asigna rápidamente para maximizar las oportunidades de conversión.
                                    </p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding:20px 40px 30px 40px;border-top:1px solid #eee;text-align:center;">
                                <div style="color:#888;font-size:12px;line-height:1.5;font-family:Arial,sans-serif;">
                                    <strong style="color:#666;">📧 Notificación Automática del Sistema</strong><br>
                                    Este correo se envía automáticamente cuando se recibe un nuevo lead desde WIX.<br>
                                    Sistema de Gestión de Leads - Grupo Kossodo<br><br>
                                    <strong>No responder a este mensaje.</strong><br>
                                    Para soporte técnico, contacta al equipo de sistemas.
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return html_template