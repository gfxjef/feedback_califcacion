#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos
"""

import os
import sys

# Configurar las mismas variables de entorno que usa run_app.py
os.environ.setdefault('MYSQL_USER', 'atusalud_atusalud')
os.environ.setdefault('MYSQL_PASSWORD', 'kmachin1')
os.environ.setdefault('MYSQL_HOST', 'atusaludlicoreria.com')
os.environ.setdefault('MYSQL_DATABASE', 'atusalud_kossomet')

# Agregar directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_db_connection():
    """
    Prueba la conexión a la base de datos usando el módulo db.py
    """
    print("🔍 PROBANDO CONEXIÓN A BASE DE DATOS")
    print("=" * 40)
    print(f"Host: {os.environ.get('MYSQL_HOST')}")
    print(f"Database: {os.environ.get('MYSQL_DATABASE')}")
    print(f"User: {os.environ.get('MYSQL_USER')}")
    print("=" * 40)
    
    try:
        # Importar el módulo de db desde app
        from db import get_db_connection
        
        print("📦 Módulo db.py importado correctamente")
        
        # Intentar conexión
        print("🔌 Intentando conectar...")
        cnx = get_db_connection()
        
        if cnx is not None:
            print("✅ CONEXIÓN EXITOSA!")
            
            # Probar una consulta simple
            cursor = cnx.cursor()
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()
            print(f"📊 Versión MySQL: {version[0]}")
            
            # Verificar si existe la tabla
            cursor.execute("SHOW TABLES LIKE 'envio_de_encuestas';")
            table_exists = cursor.fetchone()
            if table_exists:
                print("📋 Tabla 'envio_de_encuestas' existe")
                
                # Contar registros
                cursor.execute("SELECT COUNT(*) FROM envio_de_encuestas;")
                count = cursor.fetchone()
                print(f"📊 Registros en tabla: {count[0]}")
            else:
                print("⚠️  Tabla 'envio_de_encuestas' no existe (se creará automáticamente)")
            
            cursor.close()
            cnx.close()
            return True
        else:
            print("❌ FALLO EN CONEXIÓN")
            return False
            
    except ImportError as e:
        print(f"❌ Error importando módulo db: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    test_db_connection() 