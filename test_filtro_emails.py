#!/usr/bin/env python3
"""
Script de prueba para verificar el filtro de emails de testing
Probar que solo se envíen emails a gfxjef@gmail.com
"""

import requests
import json
import time

def test_email_permitido():
    """
    Prueba con el email permitido (gfxjef@gmail.com)
    Debe enviar el email realmente
    """
    url = "http://192.168.18.26:3000/submit"
    
    datos_email_permitido = {
        "asesor": "Carlos Mendoza",
        "nombres": "Usuario Testing Permitido", 
        "ruc": "20512345678",
        "correo": "gfxjef@gmail.com",  # EMAIL PERMITIDO
        "tipo": "Ventas (OC)",
        "grupo": "Testing",
        "documento": "TEST-PERMITIDO-001"
    }
    
    print("🟢 PRUEBA 1: EMAIL PERMITIDO (gfxjef@gmail.com)")
    print("=" * 50)
    print(f"📧 Email: {datos_email_permitido['correo']}")
    print("🎯 Resultado esperado: EMAIL SÍ SE ENVÍA")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=datos_email_permitido, timeout=10)
        print(f"📨 Código de respuesta: {response.status_code}")
        
        response_data = response.json()
        print(f"📋 Respuesta: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and "correctamente" in response_data.get('message', '').lower():
            print("✅ RESULTADO: EMAIL ENVIADO CORRECTAMENTE")
        else:
            print("❌ RESULTADO: ERROR EN ENVÍO")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_email_bloqueado():
    """
    Prueba con email NO permitido (cliente real)
    Debe simular envío sin enviar realmente
    """
    url = "http://192.168.18.26:3000/submit"
    
    datos_email_bloqueado = {
        "asesor": "Ana García",
        "nombres": "Cliente Real Ejemplo", 
        "ruc": "20987654321",
        "correo": "cliente.real@empresa.com",  # EMAIL BLOQUEADO
        "tipo": "Ventas (OC)",
        "grupo": "Corporativo",
        "documento": "OC-REAL-002"
    }
    
    print("\n🔴 PRUEBA 2: EMAIL BLOQUEADO (cliente.real@empresa.com)")
    print("=" * 50)
    print(f"📧 Email: {datos_email_bloqueado['correo']}")
    print("🎯 Resultado esperado: EMAIL SIMULADO (NO se envía)")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=datos_email_bloqueado, timeout=10)
        print(f"📨 Código de respuesta: {response.status_code}")
        
        response_data = response.json()
        print(f"📋 Respuesta: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and "simulado" in response_data.get('message', '').lower():
            print("✅ RESULTADO: EMAIL CORRECTAMENTE BLOQUEADO (simulado)")
        elif response.status_code == 200:
            print("⚠️  RESULTADO: Email procesado pero verificar mensaje")
        else:
            print("❌ RESULTADO: ERROR INESPERADO")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_email_multiple_con_permitido():
    """
    Prueba con múltiples emails donde uno es permitido
    """
    url = "http://192.168.18.26:3000/submit"
    
    datos_multiple = {
        "asesor": "Luis Torres",
        "nombres": "Prueba Multiple Emails", 
        "ruc": "20111222333",
        "correo": "cliente1@empresa.com, gfxjef@gmail.com, cliente2@empresa.com",  # MÚLTIPLES
        "tipo": "Operaciones",
        "grupo": "Testing",
        "documento": "MULTI-TEST-003"
    }
    
    print("\n🟡 PRUEBA 3: MÚLTIPLES EMAILS (incluye gfxjef@gmail.com)")
    print("=" * 50)
    print(f"📧 Emails: {datos_multiple['correo']}")
    print("🎯 Resultado esperado: Solo enviar a gfxjef@gmail.com")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=datos_multiple, timeout=10)
        print(f"📨 Código de respuesta: {response.status_code}")
        
        response_data = response.json()
        print(f"📋 Respuesta: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ RESULTADO: Procesado correctamente")
        else:
            print("❌ RESULTADO: ERROR")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DE FILTRO DE EMAILS")
    print("🎯 Solo gfxjef@gmail.com debe recibir emails reales")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    test_email_permitido()
    test_email_bloqueado() 
    test_email_multiple_con_permitido()
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS COMPLETADAS")
    print("📋 Verificar que:")
    print("   ✅ Solo gfxjef@gmail.com recibe emails reales")
    print("   ✅ Otros emails se simulan sin enviar")
    print("   ✅ Base de datos registra todos los casos") 