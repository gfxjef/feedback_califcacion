#!/usr/bin/env python3
"""
Script de prueba para verificar el envío de emails con la nueva implementación
de calificación 1-10 y templates diferenciados por tipo.
"""

import sys
import os

# Agregar el directorio app al path para poder importar
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.enviar_encuesta import enviar_encuesta

def test_envio_ventas():
    """Test de envío para el tipo Ventas"""
    print("🔴 PROBANDO ENVÍO TIPO: VENTAS")
    print("-" * 50)
    
    response, status_code = enviar_encuesta(
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
    
    response, status_code = enviar_encuesta(
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
    
    response, status_code = enviar_encuesta(
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

def test_envio_sin_documento():
    """Test de envío sin número de documento"""
    print("📝 PROBANDO ENVÍO SIN DOCUMENTO")
    print("-" * 50)
    
    response, status_code = enviar_encuesta(
        nombre_cliente="Elena Fernández",
        correo_cliente="jcamacho@kossodo.com",
        asesor="Diego Mendoza",
        numero_consulta="CONS-000004",
        tipo="Ventas",
        documento=None  # Sin documento
    )
    
    print(f"Status: {status_code}")
    print(f"Response: {response}")
    print("=" * 50)
    return status_code == 200

def main():
    """Función principal que ejecuta todas las pruebas"""
    print("🚀 INICIANDO TESTS DE ENVÍO DE EMAIL")
    print("📧 Enviando a: jcamacho@kossodo.com")
    print("=" * 60)
    
    # Variables para seguimiento
    tests_exitosos = 0
    total_tests = 4
    
    # Ejecutar tests
    tests = [
        ("Ventas", test_envio_ventas),
        ("Operaciones", test_envio_operaciones),
        ("Coordinador", test_envio_coordinador),
        ("Sin Documento", test_envio_sin_documento)
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
    else:
        print("⚠️ Algunos tests fallaron. Revisa la configuración.")
    
    print("\n📋 DETALLES DE LOS EMAILS ENVIADOS:")
    print("1. 🔴 Ventas - Juan Carlos Pérez - Documento: VT-2024-001234")
    print("2. 🔵 Operaciones - Ana Sofía Martínez - Documento: OP-2024-005678") 
    print("3. ⚫ Coordinador - Roberto Silva - Documento: CONF-2024-009876")
    print("4. 📝 Ventas Sin Doc - Elena Fernández - Sin documento")
    
    print("\n🔗 ENLACES DE PRUEBA GENERADOS:")
    print("- CONS-000001: https://feedback-califcacion.onrender.com/encuesta?unique_id=000001&calificacion=X&tipo=Ventas")
    print("- CONS-000002: https://feedback-califcacion.onrender.com/encuesta?unique_id=000002&calificacion=X&tipo=Operaciones")
    print("- CONS-000003: https://feedback-califcacion.onrender.com/encuesta?unique_id=000003&calificacion=X&tipo=Coordinador (Conformidad)")
    print("- CONS-000004: https://feedback-califcacion.onrender.com/encuesta?unique_id=000004&calificacion=X&tipo=Ventas")

if __name__ == "__main__":
    main() 