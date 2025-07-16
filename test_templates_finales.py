#!/usr/bin/env python3
"""
Script para generar archivos HTML de preview con los templates finales
que incluyen imagen de opinión importante, textos específicos y texto final común
"""

from templates_email import (
    get_email_template_ventas, 
    get_email_template_operaciones, 
    get_email_template_coordinador
)

def generar_previews_finales():
    """Genera archivos HTML de preview con todos los cambios aplicados"""
    
    print("🚀 GENERANDO PREVIEWS FINALES DE TEMPLATES")
    print("="*60)
    
    # Datos de prueba
    base_url = "https://feedback-califcacion.onrender.com"
    
    # Template de Ventas con documento
    print("🔴 Generando template VENTAS...")
    html_ventas = get_email_template_ventas(
        nombre_cliente="Juan Carlos Pérez",
        documento="VT-2024-001234",
        base_url=base_url,
        unique_id="000001",
        tipo="Ventas"
    )
    
    with open("final_ventas.html", "w", encoding="utf-8") as f:
        f.write(html_ventas)
    print("✅ Archivo: final_ventas.html")
    
    # Template de Operaciones con documento
    print("\n🔵 Generando template OPERACIONES...")
    html_operaciones = get_email_template_operaciones(
        nombre_cliente="Ana Sofía Martínez",
        documento="OP-2024-005678",
        base_url=base_url,
        unique_id="000002",
        tipo="Operaciones"
    )
    
    with open("final_operaciones.html", "w", encoding="utf-8") as f:
        f.write(html_operaciones)
    print("✅ Archivo: final_operaciones.html")
    
    # Template de Coordinador con documento
    print("\n⚫ Generando template COORDINADOR...")
    html_coordinador = get_email_template_coordinador(
        nombre_cliente="Roberto Silva",
        documento="CONF-2024-009876",
        base_url=base_url,
        unique_id="000003",
        tipo="Coordinador (Conformidad)"
    )
    
    with open("final_coordinador.html", "w", encoding="utf-8") as f:
        f.write(html_coordinador)
    print("✅ Archivo: final_coordinador.html")
    
    # Template sin documento para comparar
    print("\n📝 Generando template SIN DOCUMENTO...")
    html_sin_doc = get_email_template_ventas(
        nombre_cliente="Elena Fernández",
        documento=None,
        base_url=base_url,
        unique_id="000004",
        tipo="Ventas"
    )
    
    with open("final_sin_documento.html", "w", encoding="utf-8") as f:
        f.write(html_sin_doc)
    print("✅ Archivo: final_sin_documento.html")
    
    print("\n" + "="*60)
    print("📋 ARCHIVOS HTML FINALES GENERADOS")
    print("="*60)
    print("🔴 final_ventas.html - Template de Ventas completo")
    print("🔵 final_operaciones.html - Template de Operaciones completo") 
    print("⚫ final_coordinador.html - Template de Coordinador completo")
    print("📝 final_sin_documento.html - Sin número de orden")
    
    print("\n🎨 MEJORAS INCLUIDAS:")
    print("="*60)
    print("✅ Imagen de opinión importante: http://atusaludlicoreria.com/feedback/opinion_importante.jpg")
    print("✅ Textos específicos por tipo de servicio")
    print("✅ Texto final común en todos los templates")
    print("✅ Color #212639 y tamaño 19px en textos nuevos")
    print("✅ Números centrados y espaciado optimizado")
    print("✅ Color verde #6cb79a uniforme en botones")
    
    print("\n📧 CONTENIDO DE CADA TEMPLATE:")
    print("="*60)
    print("🔴 VENTAS:")
    print("   'Su orden de trabajo ha sido creada y se encuentra en proceso de")
    print("   atención. Valoramos su opinion y lo invitamos a seleccionar...'")
    
    print("\n🔵 OPERACIONES:")
    print("   'Su orden de Servicio ah sido culminada. Valoramos su opinion")
    print("   y 10 invitamos a seleccionar una de las opciones...'")
    
    print("\n⚫ COORDINADOR:")
    print("   'Valoramos su opinion y lo invitamos a seleccionar una de")
    print("   las opciones para indicarnos cómo percibio nuestro servicio.'")
    
    print("\n📝 TEXTO FINAL COMÚN:")
    print("   'En el Grupo Kossodo valoramos la comunicación interna")
    print("   y extema. Por ello su retroalimentación es esencial para")
    print("   seguir mejorando nuestros procesos.")
    print("   ")
    print("   Conozca más sobre nuestro catálogo de productos y sercicios:'")
    
    print("\n💡 INSTRUCCIONES:")
    print("="*60)
    print("1. 🌐 Abre los archivos .html en tu navegador")
    print("2. 📱 Prueba en desktop y móvil") 
    print("3. 🔗 Verifica que los enlaces funcionen correctamente")
    print("4. 🖼️ Confirma que la imagen de opinión se carga bien")
    print("5. ✅ Si todo se ve correcto, procede con el test de envío real")
    
    print("\n🔗 ENLACES DE PRUEBA INCLUIDOS:")
    print("- Calificación 1-10: unique_id=000001-000004&calificacion=1-10")
    print("- Los enlaces redirigen según el tipo especificado")

if __name__ == "__main__":
    generar_previews_finales() 