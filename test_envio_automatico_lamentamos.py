#!/usr/bin/env python3
"""
🧪 PRUEBA DE ENVÍO AUTOMÁTICO DE EMAILS DE LAMENTAMOS
Probar que cuando llegue una calificación 1-4, se envíe automáticamente 
el email de lamentamos correspondiente al tipo de servicio.
"""

import requests
import json
import time

def test_calificacion_baja_ventas():
    """
    🔴 PRUEBA 1: Calificación baja (3) para Ventas (OC)
    Debe enviar automáticamente email de lamentamos Ventas
    """
    print("🔴 PRUEBA 1: CALIFICACIÓN BAJA VENTAS (3/10)")
    print("=" * 55)
    
    # Paso 1: Registrar cliente de Ventas
    url_registro = "http://192.168.18.26:3000/submit"
    datos_registro = {
        "asesor": "Carlos Ventas Test",
        "nombres": "Cliente Insatisfecho Ventas",
        "ruc": "20123456789",
        "correo": "gfxjef@gmail.com",  # Solo este email recibirá el mensaje
        "tipo": "Ventas (OC)",
        "grupo": "Test Lamentamos",
        "documento": "OC-LAMENTAMOS-001"
    }
    
    print(f"📝 Registrando cliente Ventas...")
    try:
        response_registro = requests.post(url_registro, json=datos_registro, timeout=10)
        if response_registro.status_code != 200:
            print(f"❌ Error en registro: {response_registro.status_code}")
            return
        
        data_registro = response_registro.json()
        print(f"✅ Cliente registrado: {data_registro['message']}")
        
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        return
    
    # Esperar un momento para asegurar que se registre
    time.sleep(2)
    
    # Paso 2: Simular calificación baja (3) - esto debe enviar email automático
    print(f"\n📊 Enviando calificación baja (3) que debe disparar email automático...")
    
    # Necesitamos obtener el unique_id del registro recién creado
    # Para simplificar, usaremos el último ID (esto es para pruebas)
    # En producción, el unique_id viene en el link del email de encuesta
    
    # Simular llamada al endpoint /encuesta con calificación baja
    url_calificacion = "http://192.168.18.26:3000/encuesta"
    
    # Para pruebas, usaremos un unique_id alto (simulando el último registro)
    unique_id_test = "9999"  # En una prueba real, esto vendría del registro anterior
    
    params_calificacion = {
        "unique_id": unique_id_test,
        "calificacion": "3",  # CALIFICACIÓN BAJA - debe disparar email automático
        "tipo": "Ventas (OC)"
    }
    
    print(f"🎯 URL: {url_calificacion}")
    print(f"📋 Parámetros: {params_calificacion}")
    print("🎯 Esperado: Email automático de lamentamos Ventas + redirección")
    print("-" * 55)
    
    try:
        response_cal = requests.get(url_calificacion, params=params_calificacion, timeout=10, allow_redirects=False)
        print(f"📨 Código HTTP: {response_cal.status_code}")
        
        if response_cal.status_code == 302:  # Redirección esperada
            location = response_cal.headers.get('Location', '')
            print(f"📍 Redirección a: {location}")
            
            if "encuesta_lamentamos_ventas.html" in location:
                print("✅ REDIRECCIÓN CORRECTA: Página de lamentamos Ventas")
            else:
                print("⚠️  Redirección inesperada")
                
            print("📧 VERIFICAR: gfxjef@gmail.com debe haber recibido email de lamentamos Ventas")
            
        else:
            print(f"⚠️  Código inesperado: {response_cal.status_code}")
            if response_cal.text:
                print(f"Respuesta: {response_cal.text[:200]}...")
                
    except Exception as e:
        print(f"❌ Error en calificación: {e}")

def test_calificacion_baja_coordinador():
    """
    🟡 PRUEBA 2: Calificación baja (2) para Coordinador (Conformidad)  
    Debe enviar automáticamente email de lamentamos Operaciones
    """
    print("\n🟡 PRUEBA 2: CALIFICACIÓN BAJA COORDINADOR (2/10)")
    print("=" * 55)
    
    # Registrar cliente de Coordinador
    url_registro = "http://192.168.18.26:3000/submit"
    datos_registro = {
        "asesor": "Ana Coordinador Test",
        "nombres": "Cliente Insatisfecho Coordinador",
        "ruc": "20987654321", 
        "correo": "gfxjef@gmail.com",
        "tipo": "Coordinador (Conformidad)",
        "grupo": "Test Lamentamos",
        "documento": "CONF-LAMENTAMOS-002"
    }
    
    print(f"📝 Registrando cliente Coordinador...")
    try:
        response_registro = requests.post(url_registro, json=datos_registro, timeout=10)
        if response_registro.status_code == 200:
            print(f"✅ Cliente registrado correctamente")
        else:
            print(f"⚠️  Registro con código: {response_registro.status_code}")
    except Exception as e:
        print(f"❌ Error en registro: {e}")
        return
    
    time.sleep(2)
    
    # Calificación baja (2)
    print(f"\n📊 Enviando calificación baja (2) - debe enviar email lamentamos Operaciones...")
    
    url_calificacion = "http://192.168.18.26:3000/encuesta"
    params_calificacion = {
        "unique_id": "9998",  # ID de prueba
        "calificacion": "2",  # CALIFICACIÓN BAJA
        "tipo": "Coordinador (Conformidad)"
    }
    
    print(f"🎯 Esperado: Email automático de lamentamos Operaciones + redirección coordinación")
    print("-" * 55)
    
    try:
        response_cal = requests.get(url_calificacion, params=params_calificacion, timeout=10, allow_redirects=False)
        print(f"📨 Código HTTP: {response_cal.status_code}")
        
        if response_cal.status_code == 302:
            location = response_cal.headers.get('Location', '')
            print(f"📍 Redirección a: {location}")
            
            if "lamentamos_coordinacion.html" in location:
                print("✅ REDIRECCIÓN CORRECTA: Página de lamentamos coordinación")
            else:
                print("⚠️  Redirección inesperada")
                
            print("📧 VERIFICAR: gfxjef@gmail.com debe haber recibido email de lamentamos Operaciones")
            
    except Exception as e:
        print(f"❌ Error en calificación: {e}")

def test_calificacion_alta():
    """
    🟢 PRUEBA 3: Calificación alta (8) - NO debe enviar email de lamentamos
    """
    print("\n🟢 PRUEBA 3: CALIFICACIÓN ALTA (8/10) - SIN EMAIL")
    print("=" * 55)
    
    url_calificacion = "http://192.168.18.26:3000/encuesta"
    params_calificacion = {
        "unique_id": "9997",
        "calificacion": "8",  # CALIFICACIÓN ALTA - NO debe enviar lamentamos
        "tipo": "Ventas (OC)"
    }
    
    print(f"🎯 Esperado: Solo redirección a página de gracias (SIN email lamentamos)")
    print("-" * 55)
    
    try:
        response_cal = requests.get(url_calificacion, params=params_calificacion, timeout=10, allow_redirects=False)
        print(f"📨 Código HTTP: {response_cal.status_code}")
        
        if response_cal.status_code == 302:
            location = response_cal.headers.get('Location', '')
            print(f"📍 Redirección a: {location}")
            
            if "encuesta-gracias.html" in location:
                print("✅ REDIRECCIÓN CORRECTA: Página de gracias")
                print("✅ NO debe enviarse email de lamentamos")
            else:
                print("⚠️  Redirección inesperada")
                
    except Exception as e:
        print(f"❌ Error en calificación: {e}")

if __name__ == "__main__":
    print("🧪 PROBANDO ENVÍO AUTOMÁTICO DE EMAILS DE LAMENTAMOS")
    print("🎯 OBJETIVO: Verificar que calificaciones 1-4 disparen emails automáticos")
    print("📧 IMPORTANTE: Solo gfxjef@gmail.com recibirá emails (modo testing)")
    print("=" * 65)
    
    # Ejecutar todas las pruebas
    test_calificacion_baja_ventas()
    test_calificacion_baja_coordinador() 
    test_calificacion_alta()
    
    print("\n" + "=" * 65)
    print("🏁 PRUEBAS COMPLETADAS")
    print("=" * 65)
    print("📧 VERIFICAR EN gfxjef@gmail.com:")
    print("   ✅ Email de lamentamos Ventas (Prueba 1)")
    print("   ✅ Email de lamentamos Operaciones (Prueba 2)")
    print("   🚫 NO debe haber email de la Prueba 3")
    print("")
    print("📋 FUNCIONALIDAD IMPLEMENTADA:")
    print("   ⚡ Envío automático al recibir calificación 1-4")
    print("   🎯 Template correcto según tipo de servicio")
    print("   🛡️  Filtro de testing activo (solo gfxjef@gmail.com)")
    print("   🔄 Redirección mantiene funcionamiento original")
    print("=" * 65) 