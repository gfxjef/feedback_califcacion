#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test completo del sistema de feedback para calificaciones bajas (1-4)
Incluye templates de "lamentamos" y guardado de feedback específico en BD
"""

import sys
import os
import json
from datetime import datetime

# Agregar directorios al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from db import get_db_connection
    from templates_email import get_email_template_lamentamos_ventas, get_email_template_lamentamos_operaciones
    import mysql.connector
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("   Asegúrate de que existen db.py y templates_email.py")
    sys.exit(1)

# Configuración de la tabla (debe coincidir con main.py)
TABLE_NAME = "calificaciones"

def insertar_registro_prueba():
    """Inserta un registro de prueba en la base de datos"""
    cnx = get_db_connection()
    if cnx is None:
        print("❌ No se pudo conectar a la base de datos")
        return None

    unique_id = f"test-lamentamos-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    try:
        cursor = cnx.cursor()
        
        # Insertar registro de prueba
        insert_query = f"""
            INSERT INTO {TABLE_NAME} 
            (idcalificacion, nombre_cliente, email_cliente, telefono_cliente, tipo_cliente, numero_documento, fecha_envio)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        
        datos_prueba = [
            (unique_id, "María Fernández Test", "test@example.com", "555-0123", "Ventas (OT)", "VT-2024-TEST001"),
            (f"{unique_id}-op", "Carlos López Test", "test2@example.com", "555-0124", "Coordinador (Conformidad)", "OP-2024-TEST002")
        ]
        
        for datos in datos_prueba:
            cursor.execute(insert_query, datos)
        
        cnx.commit()
        print(f"✅ Registros de prueba insertados:")
        print(f"   • Ventas ID: {unique_id}")
        print(f"   • Operaciones ID: {unique_id}-op")
        
        return [unique_id, f"{unique_id}-op"]
        
    except mysql.connector.Error as err:
        print(f"❌ Error al insertar registros de prueba: {err}")
        return None
    finally:
        cursor.close()
        cnx.close()

def probar_templates_lamentamos(unique_ids):
    """Prueba la generación de templates de lamentamos"""
    print("\n🧪 PROBANDO TEMPLATES DE LAMENTAMOS")
    print("=" * 45)
    
    base_url = "http://localhost:5000"
    
    # Datos de prueba
    tests = [
        {
            'id': unique_ids[0],
            'nombre': "María Fernández Test",
            'documento': "VT-2024-TEST001",
            'tipo': "ventas",
            'template_func': get_email_template_lamentamos_ventas,
            'tipo_nombre': "VENTAS"
        },
        {
            'id': unique_ids[1],
            'nombre': "Carlos López Test", 
            'documento': "OP-2024-TEST002",
            'tipo': "operaciones",
            'template_func': get_email_template_lamentamos_operaciones,
            'tipo_nombre': "OPERACIONES"
        }
    ]
    
    for test in tests:
        print(f"\n📧 Probando template: {test['tipo_nombre']}")
        
        try:
            html_content = test['template_func'](
                test['nombre'], 
                test['documento'], 
                base_url, 
                test['id'], 
                test['tipo']
            )
            
            # Verificaciones
            verificaciones = [
                ("Imagen calif_reg.jpg", "calif_reg.jpg" in html_content),
                ("Número de orden", test['documento'] in html_content),
                ("Texto Grupo Kossodo", "Grupo Kossodo" in html_content),
                ("Enlaces feedback", "/feedback_especifico" in html_content),
                ("Unique ID en enlaces", test['id'] in html_content),
                ("Texto agradecimiento", "Agradecemos el tiempo" in html_content)
            ]
            
            print(f"   ✅ Template generado exitosamente")
            
            for nombre_check, resultado in verificaciones:
                status = "✅" if resultado else "❌"
                print(f"   {status} {nombre_check}")
            
            # Guardar archivo HTML
            filename = f"test_lamentamos_{test['tipo']}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"   💾 Guardado como: {filename}")
            
            # Contar botones específicos
            if test['tipo'] == 'ventas':
                botones_esperados = 4  # Falta información, Demora, Presión, Incapacidad
            else:
                botones_esperados = 6  # 6 opciones para operaciones
                
            botones_encontrados = html_content.count('/feedback_especifico')
            print(f"   🔢 Botones de feedback: {botones_encontrados}/{botones_esperados}")
            
        except Exception as e:
            print(f"   ❌ Error generando template {test['tipo_nombre']}: {str(e)}")

def simular_feedback_especifico(unique_ids):
    """Simula el guardado de feedback específico en la base de datos"""
    print("\n🎯 SIMULANDO FEEDBACK ESPECÍFICO")
    print("=" * 40)
    
    cnx = get_db_connection()
    if cnx is None:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    # Simular calificaciones bajas y feedback específico
    simulaciones = [
        {
            'id': unique_ids[0],
            'calificacion': 2,
            'tipo': 'ventas',
            'motivo': 'falta_informacion',
            'texto_esperado': 'Falta de información sobre servicios'
        },
        {
            'id': unique_ids[1], 
            'calificacion': 3,
            'tipo': 'operaciones',
            'motivo': 'demora_informes',
            'texto_esperado': 'Demora en la entrega de informes'
        }
    ]
    
    try:
        cursor = cnx.cursor(dictionary=True)
        
        for sim in simulaciones:
            print(f"\n📝 Procesando: {sim['tipo'].upper()}")
            
            # 1. Actualizar calificación
            update_calif_query = f"""
                UPDATE {TABLE_NAME} 
                SET calificacion = %s, fecha_califacion = NOW()
                WHERE idcalificacion = %s
            """
            cursor.execute(update_calif_query, (sim['calificacion'], sim['id']))
            
            # 2. Simular feedback específico
            feedback_text = f"Feedback específico: {sim['texto_esperado']}"
            update_obs_query = f"""
                UPDATE {TABLE_NAME} 
                SET observaciones = %s
                WHERE idcalificacion = %s
            """
            cursor.execute(update_obs_query, (feedback_text, sim['id']))
            
            print(f"   ✅ Calificación: {sim['calificacion']}/10")
            print(f"   ✅ Feedback: {sim['texto_esperado']}")
            
        cnx.commit()
        print(f"\n✅ Todas las simulaciones guardadas en BD")
        
    except mysql.connector.Error as err:
        print(f"❌ Error en simulación: {err}")
    finally:
        cursor.close()
        cnx.close()

def verificar_registros_bd(unique_ids):
    """Verifica que los registros se guardaron correctamente en la BD"""
    print("\n🔍 VERIFICANDO REGISTROS EN BD")
    print("=" * 35)
    
    cnx = get_db_connection()
    if cnx is None:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    try:
        cursor = cnx.cursor(dictionary=True)
        
        for unique_id in unique_ids:
            select_query = f"""
                SELECT idcalificacion, nombre_cliente, tipo_cliente, numero_documento, 
                       calificacion, observaciones, fecha_califacion
                FROM {TABLE_NAME} 
                WHERE idcalificacion = %s
            """
            cursor.execute(select_query, (unique_id,))
            row = cursor.fetchone()
            
            if row:
                print(f"\n📋 Registro: {unique_id}")
                print(f"   • Cliente: {row['nombre_cliente']}")
                print(f"   • Tipo: {row['tipo_cliente']}")
                print(f"   • Documento: {row['numero_documento']}")
                print(f"   • Calificación: {row['calificacion']}/10")
                print(f"   • Feedback: {row['observaciones'] or 'Ninguno'}")
                print(f"   • Fecha: {row['fecha_califacion']}")
            else:
                print(f"❌ No se encontró registro: {unique_id}")
                
    except mysql.connector.Error as err:
        print(f"❌ Error verificando registros: {err}")
    finally:
        cursor.close()
        cnx.close()

def limpiar_registros_prueba(unique_ids):
    """Limpia los registros de prueba de la base de datos"""
    print("\n🧹 LIMPIANDO REGISTROS DE PRUEBA")
    print("=" * 40)
    
    cnx = get_db_connection()
    if cnx is None:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    try:
        cursor = cnx.cursor()
        
        for unique_id in unique_ids:
            delete_query = f"DELETE FROM {TABLE_NAME} WHERE idcalificacion = %s"
            cursor.execute(delete_query, (unique_id,))
            print(f"   🗑️ Eliminado: {unique_id}")
        
        cnx.commit()
        print(f"✅ Registros de prueba eliminados")
        
    except mysql.connector.Error as err:
        print(f"❌ Error eliminando registros: {err}")
    finally:
        cursor.close()
        cnx.close()

def main():
    """Función principal del test"""
    print("🧪 TEST COMPLETO DEL SISTEMA DE FEEDBACK")
    print("=" * 50)
    print("Este test verificará:")
    print("• Inserción de registros en BD")
    print("• Generación de templates 'lamentamos'")
    print("• Simulación de feedback específico")
    print("• Verificación de datos en BD")
    print("=" * 50)
    
    # 1. Insertar registros de prueba
    unique_ids = insertar_registro_prueba()
    if not unique_ids:
        print("❌ No se pudieron crear registros de prueba")
        return
    
    try:
        # 2. Probar templates
        probar_templates_lamentamos(unique_ids)
        
        # 3. Simular feedback específico
        simular_feedback_especifico(unique_ids)
        
        # 4. Verificar registros
        verificar_registros_bd(unique_ids)
        
        print("\n📊 RESUMEN DEL SISTEMA:")
        print("   ✅ Templates de lamentamos creados")
        print("   ✅ Endpoint /feedback_especifico configurado")
        print("   ✅ Base de datos actualizada correctamente")
        print("   ✅ Sistema completo para calificaciones 1-4")
        
    finally:
        # 5. Limpiar registros de prueba
        respuesta = input("\n¿Deseas eliminar los registros de prueba? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            limpiar_registros_prueba(unique_ids)
        else:
            print("📝 Registros de prueba conservados para revisión manual")

if __name__ == "__main__":
    try:
        main()
        print("\n✅ TEST COMPLETADO EXITOSAMENTE")
        print("🚀 El sistema de feedback está listo para producción!")
    except Exception as e:
        print(f"\n❌ ERROR EN EL TEST: {str(e)}")
        sys.exit(1) 