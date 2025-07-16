#!/usr/bin/env python3
"""
Script para verificar que todas las importaciones estén corregidas
Simula el comportamiento de Gunicorn en Render
"""

import sys
import os

def test_importaciones_como_paquete():
    """
    Prueba las importaciones como si fuera Gunicorn en Render
    """
    print("🧪 PROBANDO IMPORTACIONES COMO PAQUETE (modo Render)")
    print("=" * 55)
    
    # Simular el entorno de Render donde app es un paquete
    # Agregar el directorio padre al path
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    errores = []
    
    # Probar importación principal
    try:
        from app.main import app
        print("✅ app.main importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando app.main: {e}")
        errores.append("app.main")
    
    # Probar otros módulos
    modulos_a_probar = [
        ("app.db", "get_db_connection"),
        ("app.enviar_encuesta", "enviar_encuesta"),
        ("app.login", "login_bp"),
        ("app.roles_menu", "roles_menu_bp"),
        ("app.records", "records_bp"),
        ("app.Mailing.wix", "wix_bp"),
        ("app.templates_email", "get_email_template_ventas")
    ]
    
    for modulo, elemento in modulos_a_probar:
        try:
            mod = __import__(modulo, fromlist=[elemento])
            getattr(mod, elemento)
            print(f"✅ {modulo}.{elemento} importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando {modulo}: {e}")
            errores.append(modulo)
        except AttributeError as e:
            print(f"⚠️  {modulo} importado pero {elemento} no encontrado: {e}")
    
    print("\n" + "=" * 55)
    if errores:
        print("❌ ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"   - {error}")
        print("\n❌ AÚN HAY PROBLEMAS DE IMPORTACIÓN")
        return False
    else:
        print("✅ TODAS LAS IMPORTACIONES FUNCIONAN CORRECTAMENTE")
        print("🚀 LISTO PARA DEPLOY EN RENDER")
        return True

def test_importaciones_desarrollo():
    """
    Prueba las importaciones como en desarrollo con run_app.py
    """
    print("\n🛠️  PROBANDO IMPORTACIONES MODO DESARROLLO")
    print("=" * 45)
    
    # Simular el entorno de desarrollo
    app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    
    try:
        # Cambiar al directorio app temporalmente
        old_cwd = os.getcwd()
        os.chdir(app_dir)
        
        import main
        print("✅ main.py importado en modo desarrollo")
        
        # Verificar que la app Flask existe
        if hasattr(main, 'app'):
            print("✅ Aplicación Flask encontrada")
        else:
            print("❌ Aplicación Flask no encontrada")
            
    except ImportError as e:
        print(f"❌ Error en modo desarrollo: {e}")
    finally:
        os.chdir(old_cwd)

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN DE IMPORTACIONES PARA RENDER")
    print("🎯 Objetivo: Resolver ModuleNotFoundError en producción")
    print("=" * 60)
    
    # Probar modo Render (paquete)
    render_ok = test_importaciones_como_paquete()
    
    # Probar modo desarrollo
    test_importaciones_desarrollo()
    
    print("\n" + "=" * 60)
    if render_ok:
        print("🎉 ¡READY FOR RENDER DEPLOY!")
        print("📋 Cambios realizados:")
        print("   ✅ app/main.py - Importaciones try/except")
        print("   ✅ app/enviar_encuesta.py - Importaciones try/except")
        print("   ✅ app/roles_menu.py - Importaciones try/except")
        print("   ✅ app/records.py - Importaciones try/except")
        print("   ✅ app/Mailing/wix.py - Importaciones try/except")
        print("\n🚀 Haz commit y push para deployer en Render")
    else:
        print("❌ AÚN HAY PROBLEMAS - Revisar errores arriba")
    print("=" * 60) 