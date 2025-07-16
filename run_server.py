#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script launcher para ejecutar el servidor Flask
Ejecuta desde el directorio raíz para resolver importaciones correctamente
"""

import os
import sys

# Configurar variables de entorno básicas para testing (sin BD real)
os.environ.setdefault('MYSQL_USER', 'test_user')
os.environ.setdefault('MYSQL_PASSWORD', 'test_pass')
os.environ.setdefault('MYSQL_HOST', 'localhost')
os.environ.setdefault('MYSQL_DATABASE', 'test_db')

# Agregar el directorio del proyecto al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("🚀 INICIANDO SERVIDOR FLASK")
print("=" * 40)
print(f"Directorio del proyecto: {project_root}")
print("Variables de entorno configuradas (modo testing)")
print("Servidor: http://localhost:3000")
print("=" * 40)

try:
    # Importar y ejecutar la aplicación Flask
    from app.main import app
    
    print("✅ Importaciones exitosas")
    print("🔥 Iniciando servidor Flask...")
    print("   Presiona Ctrl+C para detener")
    print("=" * 40)
    
    # Ejecutar el servidor
    port = int(os.environ.get("PORT", 3000))
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=True,  # Habilitar modo debug para desarrollo
        use_reloader=False  # Evitar problemas con el reloader
    )
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Verifica que todos los archivos estén en su lugar")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n⏹️  Servidor detenido por el usuario")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    sys.exit(1) 