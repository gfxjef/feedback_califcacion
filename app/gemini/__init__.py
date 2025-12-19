"""
Gemini Orchestration Module
Sistema de orquestacion que utiliza Google Gemini Function Calling
para analizar leads automaticamente.
"""

try:
    from app.gemini.service import analizar_lead_automatico
    from app.gemini.config import GEMINI_CONFIG, SIEK_CONFIG
except ImportError:
    from gemini.service import analizar_lead_automatico
    from gemini.config import GEMINI_CONFIG, SIEK_CONFIG

__all__ = [
    'analizar_lead_automatico',
    'GEMINI_CONFIG',
    'SIEK_CONFIG'
]
