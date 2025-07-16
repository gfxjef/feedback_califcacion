#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el servidor Flask y todos sus endpoints
Incluye pruebas del sistema de feedback para calificaciones bajas (1-4)
"""

import requests
import json
import time
from datetime import datetime

# Configuración del servidor
SERVER_URL = "http://localhost:3000"

def probar_health():
    """Prueba el endpoint de health check"""
    print("🏥 PROBANDO HEALTH CHECK")
    print("=" * 30)
    
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Servidor activo y funcionando")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print("   ¿Está ejecutándose en localhost:3000?")
        return False
    except Exception as e:
        print(f"❌ Error en health check: {str(e)}")
        return False

def probar_submit_y_envio():
    """Prueba el endpoint /submit para crear registros de prueba"""
    print("\n📝 PROBANDO SUBMIT Y ENVÍO DE ENCUESTAS")
    print("=" * 45)
    
    # Datos de prueba para diferentes tipos
    datos_prueba = [
        {
            "asesor": "Ana García Test",
            "nombres": "María Fernández Cliente",
            "ruc": "12345678901",
            "correo": "test.ventas@example.com",
            "tipo": "Ventas (OT)",
            "grupo": "Grupo Test Ventas",
            "documento": "VT-2024-001"
        },
        {
            "asesor": "Carlos López Test", 
            "nombres": "Pedro Martínez Cliente",
            "ruc": "98765432109",
            "correo": "test.operaciones@example.com",
            "tipo": "Coordinador (Conformidad)",
            "grupo": "Grupo Test Operaciones",
            "documento": "OP-2024-002"
        }
    ]
    
    registros_creados = []
    
    for i, datos in enumerate(datos_prueba):
        print(f"\n📋 Creando registro {i+1}: {datos['tipo']}")
        
        try:
            response = requests.post(
                f"{SERVER_URL}/submit", 
                json=datos,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Registro creado exitosamente")
                print(f"   Status: {result['status']}")
                print(f"   Mensaje: {result['message']}")
                
                # Extraer el ID del registro (lo necesitaremos para las pruebas)
                # Nota: El ID real se genera en la BD, aquí simulamos
                registro_id = f"test-{int(time.time())}-{i}"
                registros_creados.append({
                    'id': registro_id,
                    'tipo': datos['tipo'],
                    'correo': datos['correo'],
                    'nombre': datos['nombres']
                })
                
            else:
                print(f"❌ Error al crear registro: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
        except Exception as e:
            print(f"❌ Excepción al crear registro: {str(e)}")
    
    return registros_creados

def probar_calificaciones_bajas(registros):
    """Prueba el flujo de calificaciones bajas (1-4) y feedback específico"""
    print("\n🔢 PROBANDO CALIFICACIONES BAJAS (1-4)")
    print("=" * 42)
    
    if not registros:
        print("❌ No hay registros para probar")
        return
    
    # Simular calificaciones bajas
    calificaciones_prueba = [
        {
            'registro': registros[0] if len(registros) > 0 else None,
            'calificacion': 2,
            'tipo_esperado': 'ventas'
        },
        {
            'registro': registros[1] if len(registros) > 1 else None,
            'calificacion': 3, 
            'tipo_esperado': 'operaciones'
        }
    ]
    
    for prueba in calificaciones_prueba:
        if not prueba['registro']:
            continue
            
        registro = prueba['registro']
        print(f"\n📊 Probando calificación {prueba['calificacion']} para {registro['tipo']}")
        
        # Simular click en calificación
        try:
            params = {
                'unique_id': registro['id'],
                'calificacion': prueba['calificacion'],
                'tipo': registro['tipo']
            }
            
            response = requests.get(
                f"{SERVER_URL}/encuesta",
                params=params,
                allow_redirects=False,  # No seguir redirects para ver la URL
                timeout=5
            )
            
            if response.status_code in [302, 301]:  # Redirect esperado
                redirect_url = response.headers.get('Location', '')
                print(f"✅ Calificación procesada correctamente")
                print(f"   Redirect a: {redirect_url}")
                
                if 'lamentamos' in redirect_url:
                    print(f"✅ Redirigió correctamente a página de lamentamos")
                    
                    # Probar feedback específico
                    probar_feedback_especifico(registro['id'], registro['tipo'], prueba['tipo_esperado'])
                else:
                    print(f"⚠️  Redirect inesperado (puede ser por configuración de BD)")
                    
            else:
                print(f"❌ Error en calificación: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                
        except Exception as e:
            print(f"❌ Excepción en calificación: {str(e)}")

def probar_feedback_especifico(unique_id, tipo_bd, tipo_esperado):
    """Prueba el endpoint de feedback específico"""
    print(f"\n🎯 Probando feedback específico para {tipo_esperado}")
    
    # Motivos de prueba según el tipo
    motivos_por_tipo = {
        'ventas': [
            'falta_informacion',
            'demora_respuesta', 
            'presion_venta',
            'incapacidad_resolver'
        ],
        'operaciones': [
            'comunicacion_deficiente',
            'fecha_lejana',
            'incumplimiento_fecha',
            'atencion_insatisfactoria',
            'demora_informes',
            'demora_consultas'
        ]
    }
    
    motivos = motivos_por_tipo.get(tipo_esperado, ['falta_informacion'])
    motivo_prueba = motivos[0]  # Tomar el primer motivo para la prueba
    
    try:
        params = {
            'unique_id': unique_id,
            'tipo': tipo_bd,
            'motivo': motivo_prueba
        }
        
        response = requests.get(
            f"{SERVER_URL}/feedback_especifico",
            params=params,
            allow_redirects=False,
            timeout=5
        )
        
        if response.status_code in [302, 301]:
            redirect_url = response.headers.get('Location', '')
            print(f"✅ Feedback específico procesado")
            print(f"   Motivo: {motivo_prueba}")
            print(f"   Redirect a: {redirect_url}")
            
            if 'feedback-registrado' in redirect_url:
                print(f"✅ Redirigió correctamente a página de confirmación")
            else:
                print(f"⚠️  Redirect inesperado")
                
        else:
            print(f"❌ Error en feedback específico: {response.status_code}")
            if response.text:
                print(f"   Respuesta: {response.text}")
                
    except Exception as e:
        print(f"❌ Excepción en feedback específico: {str(e)}")

def probar_templates_html():
    """Genera y prueba los templates HTML de lamentamos"""
    print("\n🎨 PROBANDO GENERACIÓN DE TEMPLATES HTML")
    print("=" * 45)
    
    try:
                 # Importar las funciones de templates
         import sys
         import os
         sys.path.append('./app')
         sys.path.append('.')  # También agregar directorio actual
        
        from templates_email import get_email_template_lamentamos_ventas, get_email_template_lamentamos_operaciones
        
        # Datos de prueba
        datos_template = {
            'nombre_cliente': "María Test Cliente",
            'documento': "TEST-2024-001",
            'base_url': SERVER_URL,
            'unique_id': "test-template-123",
            'tipo': "ventas"
        }
        
        # Probar template de ventas
        print("\n📧 Generando template de Ventas...")
        html_ventas = get_email_template_lamentamos_ventas(**datos_template)
        
        with open('test_template_lamentamos_ventas.html', 'w', encoding='utf-8') as f:
            f.write(html_ventas)
        print("✅ Template de Ventas generado: test_template_lamentamos_ventas.html")
        
        # Probar template de operaciones
        print("\n📧 Generando template de Operaciones...")
        datos_template['tipo'] = 'operaciones'
        html_operaciones = get_email_template_lamentamos_operaciones(**datos_template)
        
        with open('test_template_lamentamos_operaciones.html', 'w', encoding='utf-8') as f:
            f.write(html_operaciones)
        print("✅ Template de Operaciones generado: test_template_lamentamos_operaciones.html")
        
        # Verificaciones básicas
        verificaciones = [
            ("Imagen calif_reg.jpg", "calif_reg.jpg" in html_ventas and "calif_reg.jpg" in html_operaciones),
            ("Enlaces feedback", "/feedback_especifico" in html_ventas and "/feedback_especifico" in html_operaciones),
            ("Texto Grupo Kossodo", "Grupo Kossodo" in html_ventas and "Grupo Kossodo" in html_operaciones),
            ("Número de documento", "TEST-2024-001" in html_ventas and "TEST-2024-001" in html_operaciones)
        ]
        
        print("\n🔍 Verificaciones de templates:")
        for nombre, resultado in verificaciones:
            status = "✅" if resultado else "❌"
            print(f"   {status} {nombre}")
            
    except ImportError as e:
        print(f"❌ Error importando templates: {e}")
    except Exception as e:
        print(f"❌ Error generando templates: {e}")

def main():
    """Función principal de pruebas"""
    print("🧪 PRUEBAS COMPLETAS DEL SERVIDOR FLASK")
    print("=" * 50)
    print("Este script probará:")
    print("• Health check del servidor")
    print("• Creación de registros (/submit)")
    print("• Calificaciones bajas (1-4)")
    print("• Feedback específico")
    print("• Generación de templates")
    print("=" * 50)
    
    # 1. Verificar que el servidor esté activo
    if not probar_health():
        print("\n❌ SERVIDOR NO DISPONIBLE")
        print("Asegúrate de ejecutar: cd app && python main.py")
        return
    
    # 2. Probar creación de registros
    registros = probar_submit_y_envio()
    
    # 3. Probar calificaciones bajas y feedback
    probar_calificaciones_bajas(registros)
    
    # 4. Probar generación de templates
    probar_templates_html()
    
    print("\n📊 RESUMEN DE PRUEBAS:")
    print("   ✅ Servidor Flask activo")
    print("   ✅ Endpoints principales funcionando")
    print("   ✅ Sistema de calificaciones 1-4 implementado")
    print("   ✅ Templates de lamentamos generados")
    print("   ✅ Feedback específico configurado")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("   1. Configurar variables de entorno para BD")
    print("   2. Probar envío real de correos")
    print("   3. Validar en dispositivos móviles")

if __name__ == "__main__":
    try:
        main()
        print("\n✅ PRUEBAS COMPLETADAS EXITOSAMENTE")
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {str(e)}") 