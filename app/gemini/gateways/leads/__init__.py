"""
Gateway Leads module
"""

try:
    from app.gemini.gateways.leads.gateway import GatewayLeads
except ImportError:
    from gemini.gateways.leads.gateway import GatewayLeads

__all__ = ['GatewayLeads']
