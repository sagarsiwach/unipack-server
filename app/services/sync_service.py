"""
Sync Service
Orchestrates synchronization between NocoDB and Odoo
"""

from typing import List, Dict, Any, Tuple
import logging
import asyncio

from .odoo_service import OdooService, get_odoo_service
from .nocodb_service import NocoDBService, get_nocodb_service
from ..models import SyncResult

logger = logging.getLogger(__name__)


class SyncService:
    """Service for synchronizing data between NocoDB and Odoo"""
    
    def __init__(
        self, 
        odoo: OdooService = None, 
        nocodb: NocoDBService = None
    ):
        self.odoo = odoo or get_odoo_service()
        self.nocodb = nocodb or get_nocodb_service()
    
    async def sync_products(self, only_pending: bool = False) -> SyncResult:
        """
        Sync products from NocoDB to Odoo
        
        Args:
            only_pending: If True, only sync products with pending status
        
        Returns:
            SyncResult with counts and errors
        """
        created = 0
        updated = 0
        errors: List[str] = []
        
        try:
            # Ensure Odoo is authenticated
            if not self.odoo.uid:
                if not self.odoo.authenticate():
                    return SyncResult(
                        success=False,
                        errors=["Failed to authenticate with Odoo"]
                    )
            
            # Get products from NocoDB
            if only_pending:
                products = await self.nocodb.get_pending_products()
            else:
                products = await self.nocodb.get_products()
            
            logger.info(f"Found {len(products)} products to sync")
            
            for product in products:
                try:
                    result = await self._sync_single_product(product)
                    if result == "created":
                        created += 1
                    elif result == "updated":
                        updated += 1
                except Exception as e:
                    error_msg = f"Error syncing product '{product.get('product_name', 'Unknown')}': {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    
                    # Mark as error in NocoDB
                    if product.get("Id"):
                        try:
                            await self.nocodb.mark_product_error(product["Id"], str(e))
                        except Exception:
                            pass
            
            return SyncResult(
                success=len(errors) == 0,
                created=created,
                updated=updated,
                errors=errors,
                message=f"Synced {created + updated} products ({created} created, {updated} updated)"
            )
            
        except Exception as e:
            logger.error(f"Product sync failed: {e}")
            return SyncResult(
                success=False,
                errors=[str(e)]
            )
    
    async def _sync_single_product(self, product: Dict[str, Any]) -> str:
        """
        Sync a single product to Odoo
        
        Returns:
            "created" or "updated" indicating the action taken
        """
        product_name = product.get("product_name", "")
        odoo_id = product.get("odoo_id")
        nocodb_id = product.get("Id")
        
        # Prepare product data for Odoo
        product_data = {
            "name": product_name,
            "sales_price": product.get("sales_price"),
            "cost": product.get("cost"),
            "internal_ref": product.get("internal_ref"),
            "category": product.get("category"),
            "description": product.get("description"),
        }
        
        if odoo_id:
            # Update existing product
            self.odoo.update_product(odoo_id, product_data)
            await self.nocodb.update_product_sync_status(nocodb_id, odoo_id, "synced")
            logger.info(f"Updated product: {product_name} (Odoo ID: {odoo_id})")
            return "updated"
        else:
            # Check if product exists by name
            existing_id = self.odoo.search_product_by_name(product_name)
            
            if existing_id:
                # Update existing and link
                self.odoo.update_product(existing_id, product_data)
                await self.nocodb.update_product_sync_status(nocodb_id, existing_id, "synced")
                logger.info(f"Linked and updated product: {product_name} (Odoo ID: {existing_id})")
                return "updated"
            else:
                # Create new product
                new_id = self.odoo.create_product(product_data)
                await self.nocodb.update_product_sync_status(nocodb_id, new_id, "synced")
                logger.info(f"Created product: {product_name} (Odoo ID: {new_id})")
                return "created"
    
    async def sync_contacts(self, only_pending: bool = False) -> SyncResult:
        """
        Sync contacts from NocoDB to Odoo
        
        Args:
            only_pending: If True, only sync contacts with pending status
        
        Returns:
            SyncResult with counts and errors
        """
        created = 0
        updated = 0
        errors: List[str] = []
        
        try:
            # Ensure Odoo is authenticated
            if not self.odoo.uid:
                if not self.odoo.authenticate():
                    return SyncResult(
                        success=False,
                        errors=["Failed to authenticate with Odoo"]
                    )
            
            # Get contacts from NocoDB
            if only_pending:
                contacts = await self.nocodb.get_pending_contacts()
            else:
                contacts = await self.nocodb.get_contacts()
            
            logger.info(f"Found {len(contacts)} contacts to sync")
            
            for contact in contacts:
                try:
                    result = await self._sync_single_contact(contact)
                    if result == "created":
                        created += 1
                    elif result == "updated":
                        updated += 1
                except Exception as e:
                    error_msg = f"Error syncing contact '{contact.get('name', 'Unknown')}': {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    
                    # Mark as error in NocoDB
                    if contact.get("Id"):
                        try:
                            await self.nocodb.mark_contact_error(contact["Id"], str(e))
                        except Exception:
                            pass
            
            return SyncResult(
                success=len(errors) == 0,
                created=created,
                updated=updated,
                errors=errors,
                message=f"Synced {created + updated} contacts ({created} created, {updated} updated)"
            )
            
        except Exception as e:
            logger.error(f"Contact sync failed: {e}")
            return SyncResult(
                success=False,
                errors=[str(e)]
            )
    
    async def _sync_single_contact(self, contact: Dict[str, Any]) -> str:
        """
        Sync a single contact to Odoo
        
        Returns:
            "created" or "updated" indicating the action taken
        """
        contact_name = contact.get("name", "")
        contact_email = contact.get("email")
        odoo_id = contact.get("odoo_id")
        nocodb_id = contact.get("Id")
        
        # Prepare contact data for Odoo
        contact_data = {
            "name": contact_name,
            "email": contact_email,
            "phone": contact.get("phone"),
            "mobile": contact.get("mobile"),
            "company_name": contact.get("company_name"),
            "street": contact.get("street"),
            "city": contact.get("city"),
            "state": contact.get("state"),
            "country": contact.get("country"),
            "is_customer": contact.get("is_customer", False),
            "is_vendor": contact.get("is_vendor", False),
            "tags": contact.get("tags"),
        }
        
        if odoo_id:
            # Update existing contact
            self.odoo.update_contact(odoo_id, contact_data)
            await self.nocodb.update_contact_sync_status(nocodb_id, odoo_id, "synced")
            logger.info(f"Updated contact: {contact_name} (Odoo ID: {odoo_id})")
            return "updated"
        else:
            # Check if contact exists by email or name
            existing_id = None
            if contact_email:
                existing_id = self.odoo.search_contact_by_email(contact_email)
            
            if not existing_id:
                existing_id = self.odoo.search_contact_by_name(contact_name)
            
            if existing_id:
                # Update existing and link
                self.odoo.update_contact(existing_id, contact_data)
                await self.nocodb.update_contact_sync_status(nocodb_id, existing_id, "synced")
                logger.info(f"Linked and updated contact: {contact_name} (Odoo ID: {existing_id})")
                return "updated"
            else:
                # Create new contact
                new_id = self.odoo.create_contact(contact_data)
                await self.nocodb.update_contact_sync_status(nocodb_id, new_id, "synced")
                logger.info(f"Created contact: {contact_name} (Odoo ID: {new_id})")
                return "created"


# Singleton instance
_sync_service: SyncService = None


def get_sync_service() -> SyncService:
    """Get or create Sync service instance"""
    global _sync_service
    if _sync_service is None:
        _sync_service = SyncService()
    return _sync_service
