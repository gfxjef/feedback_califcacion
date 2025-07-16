#!/usr/bin/env python3
"""
Script de prueba para endpoint /submit con tipo 'Ventas (OC)'
Prueba el registro completo desde el envío hasta la confirmación del email
"""

import requests
import json
import time

def test_registro_ventas_oc():
    """
    Prueba el endpoint /submit con datos de ejemplo para Ventas (OC)
    """
    
    # URL del endpoint
    url = "http://192.168.18.26:3000/submit"
    
    # Datos de prueba para Ventas (OC)
    datos_prueba = {
        "asesor": "Carlos Mendoza",
        "nombres": "Maria Elena Rodriguez Gutierrez", 
        "ruc": "10480528501",
        "correo": "gfxjef@gmail.com",   
        "tipo": "Ventas (OC)",
        "grupo": "Corporativo",
        "documento": "OC-2024-001234"
    }
    
    print("🧪 INICIANDO PRUEBA DE REGISTRO - VENTAS (OC)")
    print("=" * 50)
    print(f"🎯 URL: {url}")
    print(f"📊 Datos de prueba:")
    for key, value in datos_prueba.items():
        print(f"   {key}: {value}")
    print("=" * 50)
    
    try:
        # Realizar la petición POST
        print("📤 Enviando petición...")
        response = requests.post(
            url, 
            json=datos_prueba,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📨 Código de respuesta: {response.status_code}")
        print(f"📋 Respuesta del servidor:")
        
        # Parsear respuesta JSON
        try:
            response_data = response.json()
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("❌ Error: Respuesta no es JSON válido")
            print(f"Contenido raw: {response.text}")
        
        # Evaluar resultado
        if response.status_code == 200:
            print("\n✅ REGISTRO EXITOSO!")
            print("📧 Se debería haber enviado un email de encuesta")
            print("🗄️ Datos guardados en base de datos")
        else:
            print(f"\n❌ ERROR EN REGISTRO (Código: {response.status_code})")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor")
        print("   Verificar que el servidor esté corriendo en http://192.168.18.26:3000")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Timeout en la conexión")
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🏁 FIN DE PRUEBA")

def test_campos_requeridos():
    """
    Prueba validaciones de campos requeridos
    """
    url = "http://192.168.18.26:3000/submit"
    
    print("\n🔍 PRUEBA DE VALIDACIONES")
    print("=" * 30)
    
    # Caso 1: Sin campos requeridos
    datos_invalidos = {}
    print("📝 Probando: Sin campos...")
    try:
        response = requests.post(url, json=datos_invalidos, timeout=5)
        print(f"   Respuesta: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Caso 2: RUC inválido
    datos_ruc_invalido = {
        "asesor": "Test",
        "nombres": "Test", 
        "ruc": "123",  # RUC inválido
        "correo": "test@test.com",
        "tipo": "Ventas (OC)"
    }
    print("📝 Probando: RUC inválido...")
    try:
        response = requests.post(url, json=datos_ruc_invalido, timeout=5)
        print(f"   Respuesta: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    # Ejecutar prueba principal
    test_registro_ventas_oc()
    
    # Ejecutar pruebas de validación
    test_campos_requeridos() 