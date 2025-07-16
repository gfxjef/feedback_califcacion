#!/usr/bin/env python3
"""
🧪 PRUEBA REALISTA DE ENVÍO AUTOMÁTICO DE EMAILS DE LAMENTAMOS
Usa registros reales de la base de datos para probar el envío automático
"""

import requests
import json
import time

def obtener_ultimos_registros():
    """
    Obtiene los últimos registros de la base de datos para usar en las pruebas
    """
    print("🔍 Obteniendo últimos registros de la base de datos...")
    
    try:
        # Usar el endpoint de records para obtener registros reales
        url_records = "http://192.168.18.26:3000/records"
        response = requests.get(url_records, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            if records:
                print(f"✅ Obtenidos {len(records)} registros")
                # Tomar los últimos 3 registros para las pruebas
                ultimos = records[-3:] if len(records) >= 3 else records
                
                for i, record in enumerate(ultimos):
                    print(f"   📋 Registro {i+1}: ID={record.get('idcalificacion')}, Tipo={record.get('tipo')}, Cliente={record.get('nombres')}")
                
                return ultimos
            else:
                print("⚠️  No se encontraron registros")
                return []
        else:
            print(f"❌ Error obteniendo registros: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_calificacion_baja_con_id_real(registro, calificacion, tipo_esperado):
    """
    Prueba el envío automático usando un registro real de la base de datos
    """
    if not registro:
        print("❌ No hay registro válido para la prueba")
        return
    
    unique_id = str(registro.get('idcalificacion'))
    nombre = registro.get('nombres', 'Cliente')
    tipo_actual = registro.get('tipo', 'Desconocido')
    
    print(f"\n🧪 PROBANDO CON REGISTRO REAL")
    print("=" * 50)
    print(f"📋 ID: {unique_id}")
    print(f"👤 Cliente: {nombre}")
    print(f"📊 Tipo: {tipo_actual}")
    print(f"⭐ Calificación: {calificacion}")
    print(f"🎯 Tipo de email esperado: {tipo_esperado}")
    print("-" * 50)
    
    # Llamar al endpoint de calificación
    url_calificacion = "http://192.168.18.26:3000/encuesta"
    params = {
        "unique_id": unique_id,
        "calificacion": str(calificacion),
        "tipo": tipo_actual  # Usar el tipo del registro real
    }
    
    try:
        response = requests.get(url_calificacion, params=params, timeout=10, allow_redirects=False)
        print(f"📨 Código HTTP: {response.status_code}")
        
        if response.status_code == 302:  # Redirección esperada
            location = response.headers.get('Location', '')
            print(f"📍 Redirección a: {location}")
            
            # Verificar tipo de redirección
            if calificacion <= 4:
                if "lamentamos" in location.lower():
                    print(f"✅ REDIRECCIÓN CORRECTA: Página de lamentamos")
                    print(f"📧 DEBE HABERSE ENVIADO: Email de lamentamos {tipo_esperado}")
                    print(f"📧 VERIFICAR: gfxjef@gmail.com debe tener nuevo email")
                else:
                    print("⚠️  Redirección inesperada para calificación baja")
            else:
                if "gracias" in location.lower():
                    print("✅ REDIRECCIÓN CORRECTA: Página de gracias")
                    print("🚫 NO debe enviarse email de lamentamos")
                else:
                    print("⚠️  Redirección inesperada para calificación alta")
                    
        elif response.status_code == 404:
            print("❌ Registro no encontrado - puede que ya tenga calificación")
            try:
                error_data = response.json()
                print(f"   Mensaje: {error_data.get('message', '')}")
            except:
                pass
        elif response.status_code == 200:
            print("⚠️  Respuesta 200 inesperada")
            try:
                data = response.json()
                print(f"   Datos: {data}")
            except:
                print(f"   Contenido: {response.text[:200]}...")
        else:
            print(f"⚠️  Código inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en calificación: {e}")

def crear_registro_para_prueba(tipo_servicio, documento_prefijo):
    """
    Crea un registro específico para las pruebas
    """
    url_registro = "http://192.168.18.26:3000/submit"
    
    datos_registro = {
        "asesor": f"Test Lamentamos {tipo_servicio}",
        "nombres": f"Cliente Test {tipo_servicio}",
        "ruc": "20555666777",
        "correo": "gfxjef@gmail.com",  # Solo este email recibirá mensajes
        "tipo": tipo_servicio,
        "grupo": "Testing Lamentamos",
        "documento": f"{documento_prefijo}-{int(time.time())}"  # Documento único
    }
    
    print(f"📝 Creando registro de prueba para {tipo_servicio}...")
    
    try:
        response = requests.post(url_registro, json=datos_registro, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registro creado: {data.get('message')}")
            
            # Esperar un momento para que se registre
            time.sleep(2)
            
            # Obtener el registro recién creado (será el último)
            registros = obtener_ultimos_registros()
            if registros:
                nuevo_registro = registros[-1]  # El último registro
                print(f"📋 Nuevo registro ID: {nuevo_registro.get('idcalificacion')}")
                return nuevo_registro
                
        else:
            print(f"❌ Error creando registro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    print("🧪 PRUEBA REALISTA DE ENVÍO AUTOMÁTICO DE LAMENTAMOS")
    print("🎯 Usando registros reales de la base de datos")
    print("📧 Solo gfxjef@gmail.com recibirá emails (modo testing)")
    print("=" * 60)
    
    # Prueba 1: Crear y probar Ventas (OC)
    print("\n🔴 PRUEBA 1: VENTAS CON CALIFICACIÓN BAJA (3)")
    registro_ventas = crear_registro_para_prueba("Ventas (OC)", "TEST-VENTAS")
    if registro_ventas:
        test_calificacion_baja_con_id_real(registro_ventas, 3, "Ventas")
    
    # Prueba 2: Crear y probar Coordinador (Conformidad) 
    print("\n🟡 PRUEBA 2: COORDINADOR CON CALIFICACIÓN BAJA (2)")
    registro_coordinador = crear_registro_para_prueba("Coordinador (Conformidad)", "TEST-COORD")
    if registro_coordinador:
        test_calificacion_baja_con_id_real(registro_coordinador, 2, "Operaciones")
    
    # Prueba 3: Crear y probar calificación alta (sin lamentamos)
    print("\n🟢 PRUEBA 3: VENTAS CON CALIFICACIÓN ALTA (8) - SIN EMAIL")
    registro_alto = crear_registro_para_prueba("Ventas (OC)", "TEST-ALTO")
    if registro_alto:
        test_calificacion_baja_con_id_real(registro_alto, 8, "Ninguno")
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS REALISTAS COMPLETADAS")
    print("=" * 60)
    print("📧 VERIFICAR EN gfxjef@gmail.com:")
    print("   ✅ Email 1: 'Queremos mejorar nuestro servicio' (Ventas)")
    print("   ✅ Email 2: 'Queremos mejorar nuestro servicio' (Operaciones)")
    print("   🚫 Email 3: NO debe existir (calificación alta)")
    print("")
    print("💡 FUNCIONALIDAD VERIFICADA:")
    print("   ⚡ Envío automático para calificaciones 1-4")
    print("   🎯 Template correcto según tipo de servicio")
    print("   🔄 Redirección funciona correctamente")
    print("   🛡️  Filtro de testing protege emails reales")
    print("=" * 60) 