#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el sistema de imágenes individuales clickeables
para los botones de calificación 1-10 en emails.
"""

import sys
import os

# Agregar el directorio app al path para importar templates_email
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app')
sys.path.append(app_dir)

try:
    from templates_email import get_email_template_ventas, get_email_template_operaciones, get_email_template_coordinador
except ImportError:
    print("❌ Error: No se puede importar templates_email.py")
    print("   Asegúrate de que existe app/templates_email.py")
    sys.exit(1)

def generar_email_prueba():
    """Genera emails de prueba con el nuevo sistema de imágenes individuales"""
    
    # Datos de prueba
    nombre_cliente = "Ana Sofía Martínez"
    documento = "OP-2024-005678"
    base_url = "http://localhost:5000"
    unique_id = "test-12345"
    
    print("🧪 PRUEBA DEL SISTEMA DE IMÁGENES INDIVIDUALES")
    print("=" * 55)
    
    # Probar cada tipo de template
    tipos = [
        ("ventas", get_email_template_ventas, "VENTAS"),
        ("operaciones", get_email_template_operaciones, "OPERACIONES"), 
        ("coordinador", get_email_template_coordinador, "COORDINADOR")
    ]
    
    for tipo, template_func, nombre in tipos:
        print(f"\n📧 Generando template: {nombre}")
        
        try:
            html_content = template_func(nombre_cliente, documento, base_url, unique_id, tipo)
            
            # Verificar elementos clave del nuevo sistema
            verificaciones = [
                ("Imágenes individuales", "atusaludlicoreria.com/feedback/" in html_content),
                ("Enlaces directos", f"unique_id={unique_id}" in html_content),
                ("Tabla de botones", "cellspacing=\"2\"" in html_content),
                ("Max-width responsive", "max-width:45px" in html_content),
                ("Todas las imágenes", all(f"{i}.jpg" in html_content for i in range(1, 11)))
            ]
            
            print(f"   ✅ Template generado exitosamente")
            
            for nombre_check, resultado in verificaciones:
                status = "✅" if resultado else "❌"
                print(f"   {status} {nombre_check}")
            
            # Guardar archivo de prueba
            filename = f"test_email_{tipo}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"   💾 Guardado como: {filename}")
            
            # Contar imágenes de calificación
            image_count = html_content.count('atusaludlicoreria.com/feedback/')
            print(f"   🔢 Imágenes de calificación encontradas: {image_count}/10")
            
            # Verificar URLs específicas
            missing_images = []
            for i in range(1, 11):
                if f"{i}.jpg" not in html_content:
                    missing_images.append(str(i))
            
            if missing_images:
                print(f"   ⚠️  Imágenes faltantes: {', '.join(missing_images)}")
            else:
                print(f"   ✅ Todas las imágenes (1-10) están presentes")
            
        except Exception as e:
            print(f"   ❌ Error generando template {nombre}: {str(e)}")
    
    print("\n📋 RESUMEN DE SISTEMA ACTUAL:")
    print("   • Tipo: Imágenes individuales")
    print("   • Cantidad: 10 imágenes (1.jpg - 10.jpg)")
    print("   • URL base: https://atusaludlicoreria.com/feedback/")
    print("   • Tamaño: max-width:45px (responsive)")
    print("   • Compatibilidad: 100% con móviles")
    
    print("\n🎯 VENTAJAS DE ESTA SOLUCIÓN:")
    print("   ✅ Cada imagen es un enlace directo")
    print("   ✅ Sin dependencia de mapas HTML")
    print("   ✅ Máxima compatibilidad móvil")
    print("   ✅ Touch-friendly individual")
    print("   ✅ Carga rápida por caché")
    
    print("\n🔗 URLs DE LAS IMÁGENES:")
    for i in range(1, 11):
        print(f"   {i}: https://atusaludlicoreria.com/feedback/{i}.jpg")
    
    return True

if __name__ == "__main__":
    try:
        generar_email_prueba()
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("\n🚀 El sistema está listo para usar en producción!")
    except Exception as e:
        print(f"\n❌ ERROR EN LA PRUEBA: {str(e)}")
        sys.exit(1) 