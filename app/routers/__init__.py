# Routers package
from .health import router as health_router
from .products import router as products_router
from .contacts import router as contacts_router
from .sync import router as sync_router

__all__ = ["health_router", "products_router", "contacts_router", "sync_router"]
