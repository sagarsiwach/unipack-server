"""
Sync Router - Bulk sync operations between NocoDB and Odoo
"""

from fastapi import APIRouter, HTTPException, status, Query
import logging

from ..models import SyncResult
from ..services.sync_service import get_sync_service

router = APIRouter(prefix="/sync", tags=["Sync"])
logger = logging.getLogger(__name__)


@router.post("/products", response_model=SyncResult)
async def sync_products(
    only_pending: bool = Query(False, description="Only sync pending products")
):
    """Sync all products from NocoDB to Odoo"""
    try:
        sync_service = get_sync_service()
        result = await sync_service.sync_products(only_pending=only_pending)
        return result
    except Exception as e:
        logger.error(f"Product sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/contacts", response_model=SyncResult)
async def sync_contacts(
    only_pending: bool = Query(False, description="Only sync pending contacts")
):
    """Sync all contacts from NocoDB to Odoo"""
    try:
        sync_service = get_sync_service()
        result = await sync_service.sync_contacts(only_pending=only_pending)
        return result
    except Exception as e:
        logger.error(f"Contact sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/all")
async def sync_all(only_pending: bool = Query(False)):
    """Sync both products and contacts"""
    try:
        sync_service = get_sync_service()
        products = await sync_service.sync_products(only_pending=only_pending)
        contacts = await sync_service.sync_contacts(only_pending=only_pending)
        return {
            "success": products.success and contacts.success,
            "products": {"created": products.created, "updated": products.updated, "errors": products.errors},
            "contacts": {"created": contacts.created, "updated": contacts.updated, "errors": contacts.errors}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
