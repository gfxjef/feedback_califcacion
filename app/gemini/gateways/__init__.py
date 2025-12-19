"""
Gateways module
"""

try:
    from app.gemini.gateways.leads import GatewayLeads
except ImportError:
    from gemini.gateways.leads import GatewayLeads

__all__ = ['GatewayLeads']
