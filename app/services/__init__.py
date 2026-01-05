# Services package
from .odoo_service import OdooService, get_odoo_service
from .ai_service import AIService, get_ai_service

__all__ = ["OdooService", "get_odoo_service", "AIService", "get_ai_service"]
