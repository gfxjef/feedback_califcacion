#!/usr/bin/env python3
"""
Test directo del filtro de emails importando la función directamente
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Verificar que las variables críticas estén configuradas
required_vars = ['MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_HOST', 'MYSQL_DATABASE', 'EMAIL_USER', 'EMAIL_PASSWORD']
missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    print(f"❌ ERROR: Variables de entorno faltantes: {', '.join(missing_vars)}")
    print("   Crea un archivo .env con estas variables")
    sys.exit(1)

# Agregar directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_filtro_directo():
    """
    Prueba directa de la función enviar_encuesta
    """
    try:
        from enviar_encuesta import enviar_encuesta
        
        print("🧪 TEST DIRECTO DEL FILTRO DE EMAILS")
        print("=" * 50)
        
        # Prueba 1: Email permitido
        print("\n🟢 PRUEBA 1: Email permitido (gfxjef@gmail.com)")
        resultado1, codigo1 = enviar_encuesta(
            nombre_cliente="Test Usuario",
            correo_cliente="gfxjef@gmail.com",
            asesor="Test Asesor", 
            numero_consulta="CONS-999001",
            tipo="Ventas (OC)",
            documento="TEST-001"
        )
        print(f"📨 Código: {codigo1}")
        print(f"📋 Resultado: {resultado1}")
        
        # Prueba 2: Email bloqueado
        print("\n🔴 PRUEBA 2: Email bloqueado (cliente@empresa.com)")
        resultado2, codigo2 = enviar_encuesta(
            nombre_cliente="Cliente Real",
            correo_cliente="cliente@empresa.com",
            asesor="Test Asesor",
            numero_consulta="CONS-999002", 
            tipo="Ventas (OC)",
            documento="TEST-002"
        )
        print(f"📨 Código: {codigo2}")
        print(f"📋 Resultado: {resultado2}")
        
        # Prueba 3: Múltiples emails
        print("\n🟡 PRUEBA 3: Múltiples emails")
        resultado3, codigo3 = enviar_encuesta(
            nombre_cliente="Multi Test",
            correo_cliente="cliente1@empresa.com, gfxjef@gmail.com, cliente2@empresa.com",
            asesor="Test Asesor",
            numero_consulta="CONS-999003",
            tipo="Operaciones", 
            documento="TEST-003"
        )
        print(f"📨 Código: {codigo3}")
        print(f"📋 Resultado: {resultado3}")
        
        # Análisis de resultados
        print("\n" + "=" * 50)
        print("📊 ANÁLISIS DE RESULTADOS:")
        
        if "simulado" in str(resultado2.get('message', '')).lower():
            print("✅ Email bloqueado funciona correctamente")
        else:
            print("❌ Email bloqueado NO funciona")
            
        if codigo1 == 200 and "correctamente" in str(resultado1.get('message', '')).lower():
            print("✅ Email permitido funciona correctamente")
        else:
            print("❌ Email permitido tiene problemas")
            
    except ImportError as e:
        print(f"❌ Error importando: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_filtro_directo() 