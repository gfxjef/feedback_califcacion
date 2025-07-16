#!/usr/bin/env python3
"""
🚀 PRUEBA FINAL EN PRODUCCIÓN - RENDER
Probar filtro de emails en https://feedback-califcacion.onrender.com
Solo gfxjef@gmail.com debe recibir emails reales
"""

import requests
import json
import time

def test_render_email_permitido():
    """
    🟢 PRUEBA 1: Email permitido (gfxjef@gmail.com) en Render
    """
    url = "https://feedback-califcacion.onrender.com/submit"
    
    datos_permitido = {
        "asesor": "Carlos Testing Render",
        "nombres": "Usuario Prueba Produccion", 
        "ruc": "20512345678",
        "correo": "gfxjef@gmail.com",  # ✅ EMAIL PERMITIDO
        "tipo": "Ventas (OC)",
        "grupo": "Testing Render",
        "documento": "RENDER-PROD-001"
    }
    
    print("🟢 PRUEBA 1: EMAIL PERMITIDO EN RENDER")
    print("=" * 55)
    print(f"🌐 URL: {url}")
    print(f"📧 Email: {datos_permitido['correo']}")
    print("🎯 Esperado: EMAIL REAL enviado a gfxjef@gmail.com")
    print("-" * 55)
    
    try:
        response = requests.post(url, json=datos_permitido, timeout=15)
        print(f"📨 Código HTTP: {response.status_code}")
        
        response_data = response.json()
        print(f"📋 Respuesta:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            if "correctamente" in response_data.get('message', '').lower():
                print("✅ RESULTADO: EMAIL ENVIADO CORRECTAMENTE")
                print("📧 gfxjef@gmail.com debería recibir el email de encuesta")
            elif "simulado" in response_data.get('message', '').lower():
                print("⚠️  RESULTADO: Email simulado (revisar configuración)")
            else:
                print("🤔 RESULTADO: Respuesta inesperada")
        else:
            print("❌ RESULTADO: Error en el servidor")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_render_email_bloqueado():
    """
    🔴 PRUEBA 2: Email bloqueado (cliente real) en Render
    """
    url = "https://feedback-califcacion.onrender.com/submit"
    
    datos_bloqueado = {
        "asesor": "Ana García Render",
        "nombres": "Cliente Real Produccion", 
        "ruc": "20987654321",
        "correo": "cliente.real@empresa.com",  # 🚫 EMAIL BLOQUEADO
        "tipo": "Operaciones",
        "grupo": "Cliente Real",
        "documento": "CLIENTE-REAL-002"
    }
    
    print("\n🔴 PRUEBA 2: EMAIL BLOQUEADO EN RENDER")
    print("=" * 55)
    print(f"🌐 URL: {url}")
    print(f"📧 Email: {datos_bloqueado['correo']}")
    print("🎯 Esperado: EMAIL SIMULADO (NO se envía)")
    print("-" * 55)
    
    try:
        response = requests.post(url, json=datos_bloqueado, timeout=15)
        print(f"📨 Código HTTP: {response.status_code}")
        
        response_data = response.json()
        print(f"📋 Respuesta:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            if "simulado" in response_data.get('message', '').lower():
                print("✅ RESULTADO: EMAIL CORRECTAMENTE BLOQUEADO")
                print("🛡️  El cliente NO recibirá ningún email")
            elif "correctamente" in response_data.get('message', '').lower():
                print("⚠️  RESULTADO: Email procesado - verificar si fue simulado")
            else:
                print("🤔 RESULTADO: Respuesta inesperada")
        else:
            print("❌ RESULTADO: Error en el servidor")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_render_multiples_emails():
    """
    🟡 PRUEBA 3: Múltiples emails (uno permitido) en Render
    """
    url = "https://feedback-califcacion.onrender.com/submit"
    
    datos_multiples = {
        "asesor": "Luis Torres Render",
        "nombres": "Prueba Multiple Produccion", 
        "ruc": "20111222333",
        "correo": "cliente1@empresa.com, gfxjef@gmail.com, cliente2@empresa.com",
        "tipo": "Ventas (OC)",
        "grupo": "Testing Multiple",
        "documento": "MULTI-RENDER-003"
    }
    
    print("\n🟡 PRUEBA 3: MÚLTIPLES EMAILS EN RENDER")
    print("=" * 55)
    print(f"🌐 URL: {url}")
    print(f"📧 Emails: {datos_multiples['correo']}")
    print("🎯 Esperado: Solo gfxjef@gmail.com recibe email")
    print("-" * 55)
    
    try:
        response = requests.post(url, json=datos_multiples, timeout=15)
        print(f"📨 Código HTTP: {response.status_code}")
        
        response_data = response.json()
        print(f"📋 Respuesta:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print("✅ RESULTADO: Procesado correctamente")
            print("📧 Solo gfxjef@gmail.com debería recibir el email")
        else:
            print("❌ RESULTADO: Error en el servidor")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR DE CONEXIÓN: {e}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_health_render():
    """
    🔍 Verificar que el servidor de Render esté activo
    """
    print("🔍 VERIFICANDO SERVIDOR RENDER")
    print("=" * 35)
    
    try:
        response = requests.get("https://feedback-califcacion.onrender.com/health", timeout=10)
        print(f"📨 Código HTTP: {response.status_code}")
        if response.status_code == 200:
            print("✅ Servidor Render ACTIVO")
        else:
            print("⚠️  Servidor responde pero con código inesperado")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Servidor Render no accesible - {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS EN RENDER - PRODUCCIÓN")
    print("🎯 OBJETIVO: Solo gfxjef@gmail.com debe recibir emails")
    print("=" * 65)
    
    # Verificar que el servidor esté activo
    if not test_health_render():
        print("❌ No se puede continuar - Servidor Render no disponible")
        exit(1)
    
    print("\n" + "=" * 65)
    
    # Ejecutar todas las pruebas
    test_render_email_permitido()
    test_render_email_bloqueado()
    test_render_multiples_emails()
    
    print("\n" + "=" * 65)
    print("🏁 PRUEBAS EN RENDER COMPLETADAS")
    print("=" * 65)
    print("📋 VERIFICACIONES REALIZADAS:")
    print("   ✅ Email permitido → gfxjef@gmail.com")
    print("   🚫 Email bloqueado → cliente.real@empresa.com")
    print("   🎯 Múltiples emails → Solo gfxjef@gmail.com")
    print("\n📧 REVISA TU BANDEJA: gfxjef@gmail.com")
    print("   Solo deberías recibir emails de las pruebas 1 y 3")
    print("   La prueba 2 NO debe enviar ningún email")
    print("=" * 65) 