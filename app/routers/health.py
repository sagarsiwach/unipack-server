"""
Health Check Router
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from ..models import HealthResponse
from ..services.odoo_service import get_odoo_service, OdooService
from ..services.nocodb_service import get_nocodb_service, NocoDBService
from ..config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint that verifies connections to Odoo and NocoDB
    
    Returns:
        HealthResponse with status of all services
    """
    settings = get_settings()
    
    # Check Odoo connection
    odoo_service = get_odoo_service()
    odoo_healthy = odoo_service.check_connection()
    
    # Check NocoDB connection
    nocodb_service = get_nocodb_service()
    nocodb_healthy = await nocodb_service.check_connection()
    
    # Overall status
    all_healthy = odoo_healthy and nocodb_healthy
    status = "healthy" if all_healthy else "degraded"
    
    return HealthResponse(
        status=status,
        odoo=odoo_healthy,
        nocodb=nocodb_healthy,
        version=settings.app_version,
        timestamp=datetime.utcnow()
    )


@router.get("/")
async def root():
    """Root endpoint - API information"""
    settings = get_settings()
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "NocoDB to Odoo Sync API",
        "docs": "/docs",
        "health": "/health"
    }
