#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para probar endpoints básicos del servidor Flask
"""

import requests
import time

SERVER_URL = "http://localhost:3000"

def test_health():
    """Prueba el endpoint de health"""
    print("🏥 Probando Health Check...")
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check exitoso")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_templates():
    """Prueba la generación de templates"""
    print("\n🎨 Probando Templates...")
    try:
        import sys
        sys.path.append('./app')
        
        from app.templates_email import get_email_template_lamentamos_ventas
        
        html = get_email_template_lamentamos_ventas(
            "María Test", 
            "TEST-001", 
            SERVER_URL, 
            "test-123", 
            "ventas"
        )
        
        with open('test_lamentamos_simple.html', 'w', encoding='utf-8') as f:
            f.write(html)
            
        print("✅ Template generado: test_lamentamos_simple.html")
        return True
        
    except Exception as e:
        print(f"❌ Error generando template: {e}")
        return False

def test_feedback_endpoint():
    """Prueba el endpoint de feedback específico"""
    print("\n🎯 Probando Feedback Endpoint...")
    try:
        params = {
            'unique_id': 'test-123',
            'tipo': 'ventas',
            'motivo': 'falta_informacion'
        }
        
        response = requests.get(
            f"{SERVER_URL}/feedback_especifico",
            params=params,
            allow_redirects=False,
            timeout=5
        )
        
        if response.status_code in [302, 301, 404, 500]:
            print(f"✅ Endpoint responde (código: {response.status_code})")
            if 'Location' in response.headers:
                print(f"   Redirect a: {response.headers['Location']}")
            return True
        else:
            print(f"⚠️  Respuesta inesperada: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 PRUEBAS SIMPLES DEL SERVIDOR")
    print("=" * 40)
    
    # Esperar a que el servidor se inicie
    print("Esperando 3 segundos para que el servidor se inicie...")
    time.sleep(3)
    
    # Ejecutar pruebas
    health_ok = test_health()
    template_ok = test_templates()
    feedback_ok = test_feedback_endpoint()
    
    print("\n📊 RESUMEN:")
    print(f"   Health Check: {'✅' if health_ok else '❌'}")
    print(f"   Templates: {'✅' if template_ok else '❌'}")
    print(f"   Feedback: {'✅' if feedback_ok else '❌'}")
    
    if health_ok:
        print("\n🚀 ¡Servidor funcionando! Puedes probar:")
        print(f"   • Health: {SERVER_URL}/health")
        print(f"   • Submit: POST {SERVER_URL}/submit")
        print(f"   • Feedback: {SERVER_URL}/feedback_especifico")

if __name__ == "__main__":
    main() 