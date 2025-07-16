#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script launcher para ejecutar el servidor Flask desde /app
Configura variables de entorno y maneja importaciones correctamente
"""

import os
import sys

# Configurar variables de entorno con credenciales reales de BD
os.environ.setdefault('MYSQL_USER', 'atusalud_atusalud')
os.environ.setdefault('MYSQL_PASSWORD', 'kmachin1')
os.environ.setdefault('MYSQL_HOST', 'atusaludlicoreria.com')
os.environ.setdefault('MYSQL_DATABASE', 'atusalud_kossomet')

# Configurar variables de entorno SMTP Gmail  
os.environ.setdefault('EMAIL_USER', 'jcamacho@kossodo.com')
os.environ.setdefault('EMAIL_PASSWORD', 'jxehvsnsgwirlleq')

# Agregar el directorio actual al path para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🚀 INICIANDO SERVIDOR FLASK DESDE /app")
print("=" * 45)
print(f"Directorio de ejecución: {current_dir}")
print("Variables de entorno configuradas con BD real")
print("BD: atusaludlicoreria.com/atusalud_kossomet")
print("Servidor: http://localhost:3000")
print("=" * 45)

try:
    # Importar directamente desde el mismo directorio
    import main
    
    print("✅ Módulo main.py importado exitosamente")
    print("🔥 Iniciando servidor Flask...")
    print("   Health check: http://localhost:3000/health")
    print("   Presiona Ctrl+C para detener")
    print("=" * 45)
    
    # Ejecutar el servidor usando la aplicación Flask del main.py
    if hasattr(main, 'app'):
        port = int(os.environ.get("PORT", 3000))
        main.app.run(
            host="0.0.0.0", 
            port=port, 
            debug=True,
            use_reloader=False
        )
    else:
        print("❌ No se encontró la aplicación Flask en main.py")
        sys.exit(1)
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Verifica que main.py esté en el directorio /app")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n⏹️  Servidor detenido por el usuario")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    print(f"Tipo de error: {type(e).__name__}")
    sys.exit(1) 