"""
Tools for Gateway Leads
"""

try:
    from app.gemini.gateways.leads.tools.buscar_en_siek import buscar_en_siek
    from app.gemini.gateways.leads.tools.analizar_requerimiento import analizar_requerimiento
    from app.gemini.gateways.leads.tools.buscar_info_empresa import buscar_info_empresa
except ImportError:
    from gemini.gateways.leads.tools.buscar_en_siek import buscar_en_siek
    from gemini.gateways.leads.tools.analizar_requerimiento import analizar_requerimiento
    from gemini.gateways.leads.tools.buscar_info_empresa import buscar_info_empresa

__all__ = [
    'buscar_en_siek',
    'analizar_requerimiento',
    'buscar_info_empresa'
]
