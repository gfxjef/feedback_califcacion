

#!/usr/bin/env python3
"""
Script de prueba para verificar el envío de emails con la nueva implementación
Ejecutado desde el directorio /app
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar templates locales
from templates_email import (
    get_email_template_ventas, 
    get_email_template_operaciones, 
    get_email_template_coordinador
)

def enviar_encuesta_test(nombre_cliente, correo_cliente, asesor, numero_consulta, tipo, documento=None):
    """
    Versión de test que permite envío a correos internos para testing
    """
    print(f"📧 Preparando envío para: {nombre_cliente}")
    print(f"📨 Correo destino: {correo_cliente}")
    print(f"📋 Tipo: {tipo}")
    print(f"📄 Documento: {documento}")
    
    # Validaciones básicas
    if not (nombre_cliente and correo_cliente and asesor and numero_consulta):
        return {'status': 'error', 'message': 'Faltan parámetros'}, 400

    # Procesar correos (BYPASS validación para test)
    email_list = [email.strip() for email in correo_cliente.split(',') if email.strip()]

    # Extraer el unique_id desde el número de consulta
    unique_id = numero_consulta.replace("CONS-", "")

    # URL base donde se ubica el endpoint /encuesta
    base_url = "https://feedback-califcacion.onrender.com"

    # Generar el HTML según el tipo usando templates
    print(f"🎨 Generando template para tipo: {tipo}")
    
    if tipo == "Ventas" or tipo == "Ventas (OT)" or tipo == "Ventas (OC)":
        html_body = get_email_template_ventas(nombre_cliente, documento, base_url, unique_id, tipo)
        print("🔴 Template VENTAS generado")
    elif tipo == "Operaciones":
        html_body = get_email_template_operaciones(nombre_cliente, documento, base_url, unique_id, tipo)
        print("🔵 Template OPERACIONES generado")
    elif tipo == "Coordinador (Conformidad)" or tipo == "Entregado":
        html_body = get_email_template_coordinador(nombre_cliente, documento, base_url, unique_id, tipo)
        print("⚫ Template COORDINADOR generado")
    else:
        html_body = get_email_template_coordinador(nombre_cliente, documento, base_url, unique_id, tipo)
        print("⚫ Template por defecto (COORDINADOR) generado")

    try:
        # Configuración SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv('EMAIL_USER')
        sender_password = os.getenv('EMAIL_PASSWORD')
        
        print(f"📮 Configuración SMTP: {smtp_server}:{smtp_port}")
        print(f"👤 Usuario email: {sender_email}")
        print(f"🔑 Password configurado: {'✅' if sender_password else '❌'}")

        if not sender_email or not sender_password:
            return {'status': 'error', 'message': 'Variables de entorno EMAIL_USER o EMAIL_PASSWORD no configuradas'}, 500

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[TEST] Encuesta Satisfacción - {numero_consulta} - {tipo}"
        msg['From'] = "Kossodo S.A.C. <jcamacho@kossodo.com>"
        msg['To'] = ", ".join(email_list)

        part_html = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part_html)

        print("📤 Enviando correo...")
        # Enviar correo
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email_list, msg.as_string())
        server.quit()
        
        print("✅ Correo enviado exitosamente!")
        return {'status': 'ok', 'message': 'Email de test enviado correctamente'}, 200

    except Exception as e:
        print(f"❌ Error al enviar: {str(e)}")
        return {'status': 'error', 'message': f'Error al enviar el correo: {str(e)}'}, 500

def test_ventas():
    """Test para tipo Ventas"""
    print("\n" + "="*60)
    print("🔴 TEST 1: ENVÍO TIPO VENTAS")
    print("="*60)
    
    return enviar_encuesta_test(
        nombre_cliente="Juan Carlos Pérez",
        correo_cliente="jcamacho@kossodo.com",
        asesor="María González",
        numero_consulta="CONS-000001",
        tipo="Ventas",
        documento="VT-2024-001234"
    )

def test_operaciones():
    """Test para tipo Operaciones"""
    print("\n" + "="*60)
    print("🔵 TEST 2: ENVÍO TIPO OPERACIONES")
    print("="*60)
    
    return enviar_encuesta_test(
        nombre_cliente="Ana Sofía Martínez",
        correo_cliente="jcamacho@kossodo.com",
        asesor="Carlos Rodriguez",
        numero_consulta="CONS-000002",
        tipo="Operaciones",
        documento="OP-2024-005678"
    )

def test_coordinador():
    """Test para tipo Coordinador"""
    print("\n" + "="*60)
    print("⚫ TEST 3: ENVÍO TIPO COORDINADOR")
    print("="*60)
    
    return enviar_encuesta_test(
        nombre_cliente="Roberto Silva",
        correo_cliente="jcamacho@kossodo.com",
        asesor="Patricia López",
        numero_consulta="CONS-000003",
        tipo="Coordinador (Conformidad)",
        documento="CONF-2024-009876"
    )

def main():
    """Función principal"""
    print("🚀 INICIANDO TESTS DE EMAIL DESDE /app")
    print("📧 Destino: jcamacho@kossodo.com")
    print("🎯 Probando 3 tipos de templates diferentes")
    
    # Verificar variables de entorno
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    print(f"📋 EMAIL_USER: {email_user}")
    print(f"📋 EMAIL_PASSWORD: {'*' * len(email_password) if email_password else 'NO CONFIGURADO'}")
    
    if not email_user or not email_password:
        print("❌ ERROR: Variables EMAIL_USER y EMAIL_PASSWORD deben estar configuradas en .env")
        return
    
    tests = [
        ("Ventas", test_ventas),
        ("Operaciones", test_operaciones), 
        ("Coordinador", test_coordinador)
    ]
    
    exitosos = 0
    
    for nombre, test_func in tests:
        try:
            response, status = test_func()
            if status == 200:
                print(f"✅ Test {nombre}: EXITOSO")
                exitosos += 1
            else:
                print(f"❌ Test {nombre}: FALLÓ - {response}")
        except Exception as e:
            print(f"💥 Test {nombre}: ERROR - {str(e)}")
    
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print(f"✅ Tests exitosos: {exitosos}/3")
    print(f"❌ Tests fallidos: {3-exitosos}/3")
    
    if exitosos == 3:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        print("📧 Revisa tu correo jcamacho@kossodo.com")
        print("🔍 Busca emails con asunto '[TEST]'")
        
        print("\n🔗 ENLACES DE PRUEBA:")
        print("1. https://feedback-califcacion.onrender.com/encuesta?unique_id=000001&calificacion=5&tipo=Ventas")
        print("2. https://feedback-califcacion.onrender.com/encuesta?unique_id=000002&calificacion=8&tipo=Operaciones") 
        print("3. https://feedback-califcacion.onrender.com/encuesta?unique_id=000003&calificacion=3&tipo=Coordinador%20(Conformidad)")
    else:
        print("⚠️ Algunos tests fallaron")

if __name__ == "__main__":
    main() 