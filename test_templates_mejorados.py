#!/usr/bin/env python3
"""
Script para generar archivos HTML locales de los templates mejorados
para revisar visualmente los cambios antes de enviar emails
"""

from templates_email import (
    get_email_template_ventas, 
    get_email_template_operaciones, 
    get_email_template_coordinador
)

def generar_html_locales():
    """Genera archivos HTML locales para revisar el diseño"""
    
    # Datos de prueba
    nombre_cliente = "Juan Carlos Pérez"
    documento = "VT-2024-001234"
    base_url = "https://feedback-califcacion.onrender.com"
    unique_id = "000001"
    
    # Template de Ventas
    html_ventas = get_email_template_ventas(
        nombre_cliente=nombre_cliente,
        documento=documento,
        base_url=base_url,
        unique_id=unique_id,
        tipo="Ventas"
    )
    
    with open("preview_ventas.html", "w", encoding="utf-8") as f:
        f.write(html_ventas)
    print("✅ Generado: preview_ventas.html")
    
    # Template de Operaciones
    html_operaciones = get_email_template_operaciones(
        nombre_cliente="Ana Sofía Martínez",
        documento="OP-2024-005678",
        base_url=base_url,
        unique_id="000002",
        tipo="Operaciones"
    )
    
    with open("preview_operaciones.html", "w", encoding="utf-8") as f:
        f.write(html_operaciones)
    print("✅ Generado: preview_operaciones.html")
    
    # Template de Coordinador
    html_coordinador = get_email_template_coordinador(
        nombre_cliente="Roberto Silva",
        documento="CONF-2024-009876",
        base_url=base_url,
        unique_id="000003",
        tipo="Coordinador (Conformidad)"
    )
    
    with open("preview_coordinador.html", "w", encoding="utf-8") as f:
        f.write(html_coordinador)
    print("✅ Generado: preview_coordinador.html")
    
    # Template sin documento para comparar
    html_sin_doc = get_email_template_ventas(
        nombre_cliente="Elena Fernández",
        documento=None,
        base_url=base_url,
        unique_id="000004",
        tipo="Ventas"
    )
    
    with open("preview_sin_documento.html", "w", encoding="utf-8") as f:
        f.write(html_sin_doc)
    print("✅ Generado: preview_sin_documento.html")
    
    print("\n" + "="*60)
    print("📋 ARCHIVOS HTML GENERADOS")
    print("="*60)
    print("🔴 preview_ventas.html - Template de Ventas")
    print("🔵 preview_operaciones.html - Template de Operaciones") 
    print("⚫ preview_coordinador.html - Template de Coordinador")
    print("📝 preview_sin_documento.html - Sin número de orden")
    
    print("\n🎨 MEJORAS APLICADAS:")
    print("✅ Números centrados vertical y horizontalmente")
    print("✅ Espaciado reducido entre cuadros")
    print("✅ Texto más grande (20px vs 16px)")
    print("✅ Color verde #6cb79a uniforme en bordes y letras")
    print("✅ Sin padding-top en sección de calificación")
    print("✅ 'Número de orden' más grande (19px) sin '#'")
    
    print("\n💡 INSTRUCCIONES:")
    print("1. Abre los archivos .html en tu navegador")
    print("2. Revisa el diseño y funcionamiento")
    print("3. Si todo se ve bien, ejecuta el test de envío")

if __name__ == "__main__":
    print("🚀 GENERANDO PREVIEWS DE TEMPLATES MEJORADOS")
    generar_html_locales() 