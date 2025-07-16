#!/usr/bin/env python3
"""
Script de prueba ESPECIAL para verificar el envío de emails a correos internos
Bypasea temporalmente la validación de dominios internos para testing.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys

# Agregar el directorio app al path para poder importar
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.templates_email import (
    get_email_template_ventas, 
    get_email_template_operaciones, 
    get_email_template_coordinador
)

def enviar_encuesta_test(nombre_cliente, correo_cliente, asesor, numero_consulta, tipo, documento=None):
    """
    Versión de test de enviar_encuesta que permite correos internos
    """
    # Validaciones básicas
    if not (nombre_cliente and correo_cliente and asesor and numero_consulta):
        return {'status': 'error', 'message': 'Faltan parámetros'}, 400

    # Procesar correos (SIN validación de dominios internos para test)
    email_list = [email.strip() for email in correo_cliente.split(',') if email.strip()]

    # Extraer el unique_id desde el número de consulta
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
        sender_email = os.environ.get('EMAIL_USER')
        sender_password = os.environ.get('EMAIL_PASSWORD')

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[TEST] Encuesta de Satisfacción - Consulta #{numero_consulta} - {tipo}"
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

        return {'status': 'ok', 'message': 'Encuesta de test enviada correctamente'}, 200

    except Exception as e:
        return {'status': 'error', 'message': f'Error al enviar el correo: {str(e)}'}, 500

def test_envio_ventas():
    """Test de envío para el tipo Ventas"""
    print("🔴 PROBANDO ENVÍO TIPO: VENTAS")
    print("-" * 50)
    
    response, status_code = enviar_encuesta_test(
        nombre_cliente="Juan Carlos Pérez",
        correo_cliente="jcamacho@kossodo.com",
        asesor="María González",
        numero_consulta="CONS-000001",
        tipo="Ventas",
        documento="VT-2024-001234"
    )
    
    print(f"Status: {status_code}")
    print(f"Response: {response}")
    print("=" * 50)
    return status_code == 200

def test_envio_operaciones():
    """Test de envío para el tipo Operaciones"""
    print("🔵 PROBANDO ENVÍO TIPO: OPERACIONES")
    print("-" * 50)
    
    response, status_code = enviar_encuesta_test(
        nombre_cliente="Ana Sofía Martínez",
        correo_cliente="jcamacho@kossodo.com",
        asesor="Carlos Rodriguez",
        numero_consulta="CONS-000002",
        tipo="Operaciones",
        documento="OP-2024-005678"
    )
    
    print(f"Status: {status_code}")
    print(f"Response: {response}")
    print("=" * 50)
    return status_code == 200

def test_envio_coordinador():
    """Test de envío para el tipo Coordinador"""
    print("⚫ PROBANDO ENVÍO TIPO: COORDINADOR")
    print("-" * 50)
    
    response, status_code = enviar_encuesta_test(
        nombre_cliente="Roberto Silva",
        correo_cliente="jcamacho@kossodo.com",
        asesor="Patricia López",
        numero_consulta="CONS-000003",
        tipo="Coordinador (Conformidad)",
        documento="CONF-2024-009876"
    )
    
    print(f"Status: {status_code}")
    print(f"Response: {response}")
    print("=" * 50)
    return status_code == 200

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 INICIANDO TESTS DE ENVÍO DE EMAIL (VERSIÓN INTERNA)")
    print("📧 Enviando a: jcamacho@kossodo.com")
    print("⚠️  BYPASEANDO validación de dominios internos para test")
    print("=" * 60)
    
    # Variables para seguimiento
    tests_exitosos = 0
    total_tests = 3
    
    # Ejecutar tests
    tests = [
        ("Ventas", test_envio_ventas),
        ("Operaciones", test_envio_operaciones),
        ("Coordinador", test_envio_coordinador)
    ]
    
    for nombre_test, funcion_test in tests:
        try:
            print(f"\n🧪 Ejecutando test: {nombre_test}")
            if funcion_test():
                print(f"✅ Test {nombre_test}: EXITOSO")
                tests_exitosos += 1
            else:
                print(f"❌ Test {nombre_test}: FALLÓ")
        except Exception as e:
            print(f"💥 Error en test {nombre_test}: {str(e)}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print(f"✅ Tests exitosos: {tests_exitosos}/{total_tests}")
    print(f"❌ Tests fallidos: {total_tests - tests_exitosos}/{total_tests}")
    
    if tests_exitosos == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON CORRECTAMENTE!")
        print("📧 Revisa tu correo jcamacho@kossodo.com para verificar los emails")
        print("🔍 Los emails tienen [TEST] en el asunto para identificarlos")
    else:
        print("⚠️ Algunos tests fallaron. Revisa la configuración.")
    
    print("\n📋 EMAILS DE PRUEBA ENVIADOS:")
    print("1. 🔴 [TEST] Ventas - Juan Carlos Pérez - Documento: VT-2024-001234")
    print("2. 🔵 [TEST] Operaciones - Ana Sofía Martínez - Documento: OP-2024-005678") 
    print("3. ⚫ [TEST] Coordinador - Roberto Silva - Documento: CONF-2024-009876")
    
    print("\n🔗 ENLACES DE PRUEBA GENERADOS:")
    print("- https://feedback-califcacion.onrender.com/encuesta?unique_id=000001&calificacion=5&tipo=Ventas")
    print("- https://feedback-califcacion.onrender.com/encuesta?unique_id=000002&calificacion=8&tipo=Operaciones")
    print("- https://feedback-califcacion.onrender.com/encuesta?unique_id=000003&calificacion=3&tipo=Coordinador (Conformidad)")
    
    print("\n📝 NOTA: Los enlaces de ejemplo usan calificaciones 5, 8 y 3 respectivamente")
    print("💡 Puedes cambiar el número de calificación en la URL (1-10) para probar diferentes valores")

if __name__ == "__main__":
    main() 