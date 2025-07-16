#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script launcher para ejecutar el servidor Flask desde /app
Configura variables de entorno y maneja importaciones correctamente
"""

import os
import sys

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv()

# Verificar que las variables de entorno requeridas estén configuradas
required_vars = [
    'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_HOST', 'MYSQL_DATABASE',
    'EMAIL_USER', 'EMAIL_PASSWORD'
]

missing_vars = [var for var in required_vars if not os.environ.get(var)]
if missing_vars:
    print(f"❌ ERROR: Faltan las siguientes variables de entorno: {', '.join(missing_vars)}")
    print("   Crea un archivo .env con estas variables o configúralas en el sistema")
    sys.exit(1)

# Agregar el directorio actual al path para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🚀 INICIANDO SERVIDOR FLASK DESDE /app")
print("=" * 45)
print(f"Directorio de ejecución: {current_dir}")
print("✅ Variables de entorno cargadas desde .env")
print(f"🗄️  BD: {os.environ.get('MYSQL_HOST')}/{os.environ.get('MYSQL_DATABASE')}")
print(f"📧 Email: {os.environ.get('EMAIL_USER')}")
print("🌐 Servidor: http://localhost:3000")
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