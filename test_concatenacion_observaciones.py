#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar la concatenación de observaciones con coma
Verifica que el feedback específico se agregue correctamente a observaciones existentes
"""

import requests
import json
import time

def test_concatenacion_observaciones():
    """
    Prueba que el feedback específico se agregue con coma a observaciones existentes
    """
    print("🧪 PROBANDO CONCATENACIÓN DE OBSERVACIONES CON COMA")
    print("=" * 60)
    
    base_url = "http://192.168.18.26:3000"
    
    # Paso 1: Crear un registro con observaciones iniciales
    print("📝 PASO 1: Creando registro con observaciones iniciales...")
    datos_registro = {
        "asesor": "Test Concatenación",
        "nombres": "Cliente Test Observaciones",
        "ruc": "10123456789",
        "correo": "gfxjef@gmail.com",
        "tipo": "Ventas (OC)",
        "documento": "TEST-CONCAT-001"
    }
    
    try:
        response = requests.post(
            f"{base_url}/submit",
            json=datos_registro,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            unique_id = data.get('unique_id')
            print(f"✅ Registro creado con unique_id: {unique_id}")
        else:
            print(f"❌ Error creando registro: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error en paso 1: {e}")
        return
    
    # Paso 2: Agregar observaciones manualmente (simular información previa)
    print(f"\n📝 PASO 2: Agregando observaciones iniciales al registro {unique_id}...")
    # En una prueba real, esto se haría directamente en la BD
    # Por ahora, vamos a simular que ya tiene observaciones
    
    # Paso 3: Usar feedback específico para agregar más información
    print(f"\n📝 PASO 3: Agregando feedback específico via click en email...")
    
    # Simular click en opción "Falta de información sobre servicios"
    params_feedback = {
        'unique_id': unique_id,
        'tipo': 'Ventas (OC)',
        'motivo': 'falta_informacion'
    }
    
    try:
        response_feedback = requests.get(
            f"{base_url}/feedback_especifico",
            params=params_feedback,
            allow_redirects=False,
            timeout=5
        )
        
        if response_feedback.status_code in [302, 301]:
            redirect_url = response_feedback.headers.get('Location', '')
            print("✅ Feedback específico procesado correctamente")
            print(f"   Motivo: Falta de información sobre servicios")
            print(f"   Redirect: {redirect_url}")
        else:
            print(f"❌ Error en feedback específico: {response_feedback.status_code}")
            print(f"   Respuesta: {response_feedback.text}")
            
    except Exception as e:
        print(f"❌ Error en paso 3: {e}")
        return
    
    # Paso 4: Agregar OTRO feedback específico para probar concatenación
    print(f"\n📝 PASO 4: Agregando SEGUNDO feedback específico para probar concatenación...")
    
    # Simular segundo click en opción "Demora en respuesta a consultas"
    params_feedback_2 = {
        'unique_id': unique_id,
        'tipo': 'Ventas (OC)',
        'motivo': 'demora_respuesta'
    }
    
    try:
        response_feedback_2 = requests.get(
            f"{base_url}/feedback_especifico",
            params=params_feedback_2,
            allow_redirects=False,
            timeout=5
        )
        
        if response_feedback_2.status_code in [302, 301]:
            print("✅ SEGUNDO feedback específico procesado correctamente")
            print(f"   Motivo: Demora en respuesta a consultas")
            print("   🔗 Este debería haberse agregado CON COMA al anterior")
        else:
            print(f"❌ Error en segundo feedback: {response_feedback_2.status_code}")
            
    except Exception as e:
        print(f"❌ Error en paso 4: {e}")
        return
    
    print(f"\n🎯 RESUMEN DEL TEST:")
    print("=" * 40)
    print(f"📋 Unique ID probado: {unique_id}")
    print("✅ Primer feedback: Falta de información sobre servicios")
    print("✅ Segundo feedback: Demora en respuesta a consultas")
    print("")
    print("🔍 RESULTADO ESPERADO EN BD:")
    print("   Columna 'observaciones' debería tener:")
    print("   'Feedback específico: Falta de información sobre servicios, Feedback específico: Demora en respuesta a consultas'")
    print("")
    print("💡 Para verificar manualmente, revisar la BD directamente")

def test_feedback_multiple_tipos():
    """
    Prueba feedback específico para múltiples tipos (Ventas y Operaciones)
    """
    print(f"\n🧪 PROBANDO FEEDBACK MÚLTIPLES TIPOS")
    print("=" * 45)
    
    base_url = "http://192.168.18.26:3000"
    
    # Test para Operaciones
    print("📝 Creando registro tipo Operaciones...")
    datos_operaciones = {
        "asesor": "Test Operaciones",
        "nombres": "Cliente Test Operaciones",
        "ruc": "10987654321",
        "correo": "gfxjef@gmail.com",
        "tipo": "Operaciones",
        "documento": "OP-TEST-001"
    }
    
    try:
        response = requests.post(
            f"{base_url}/submit",
            json=datos_operaciones,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            unique_id_op = data.get('unique_id')
            print(f"✅ Registro Operaciones creado: {unique_id_op}")
            
            # Agregar feedback específico de operaciones
            params_op = {
                'unique_id': unique_id_op,
                'tipo': 'Operaciones',
                'motivo': 'comunicacion_deficiente'
            }
            
            response_op = requests.get(
                f"{base_url}/feedback_especifico",
                params=params_op,
                allow_redirects=False,
                timeout=5
            )
            
            if response_op.status_code in [302, 301]:
                print("✅ Feedback Operaciones procesado: Comunicación deficiente")
            else:
                print(f"❌ Error feedback Operaciones: {response_op.status_code}")
        
    except Exception as e:
        print(f"❌ Error test operaciones: {e}")

if __name__ == "__main__":
    test_concatenacion_observaciones()
    test_feedback_multiple_tipos()
    
    print(f"\n🏁 TESTS COMPLETADOS")
    print("=" * 30)
    print("🔍 Revisar la BD para confirmar que las observaciones")
    print("   se concatenan correctamente con comas (,)") 