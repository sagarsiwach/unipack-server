"""
NocoDB API Service
Handles all communication with NocoDB
"""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


class NocoDBService:
    """Service for interacting with NocoDB via REST API"""
    
    # Table names in NocoDB
    PRODUCTS_TABLE = "Products"
    CONTACTS_TABLE = "Contacts"
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.nocodb_url
        self.api_token = self.settings.nocodb_api_token
        self.base_id = self.settings.nocodb_base_id
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get API headers with authentication"""
        return {
            "xc-token": self.api_token,
            "Content-Type": "application/json"
        }
    
    async def get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=30.0
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def check_connection(self) -> bool:
        """Check if NocoDB connection is working"""
        try:
            client = await self.get_client()
            # Try to get the base info
            response = await client.get(f"/api/v2/meta/bases")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"NocoDB connection check failed: {e}")
            return False
    
    def _get_table_url(self, table_name: str) -> str:
        """Get the API URL for a table"""
        return f"/api/v2/tables/{table_name}/records"
    
    # ============== Generic CRUD Operations ==============
    
    async def get_records(
        self, 
        table_name: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get records from a table with optional filters"""
        try:
            client = await self.get_client()
            
            params = {
                "limit": limit,
                "offset": offset
            }
            
            # Add filters if provided (NocoDB uses different filter syntax)
            if filters:
                # Convert to NocoDB filter format
                where_clauses = []
                for key, value in filters.items():
                    where_clauses.append(f"({key},eq,{value})")
                if where_clauses:
                    params["where"] = "~and".join(where_clauses)
            
            response = await client.get(
                self._get_table_url(table_name),
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("list", [])
        except Exception as e:
            logger.error(f"Error fetching records from {table_name}: {e}")
            raise
    
    async def get_all_records(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all records from a table (handles pagination)"""
        all_records = []
        offset = 0
        limit = 100
        
        while True:
            records = await self.get_records(table_name, limit=limit, offset=offset)
            if not records:
                break
            all_records.extend(records)
            if len(records) < limit:
                break
            offset += limit
        
        return all_records
    
    async def create_record(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in a table"""
        try:
            client = await self.get_client()
            response = await client.post(
                self._get_table_url(table_name),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating record in {table_name}: {e}")
            raise
    
    async def update_record(
        self, 
        table_name: str, 
        record_id: int, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing record"""
        try:
            client = await self.get_client()
            # NocoDB v2 uses PATCH with Id in the body
            data["Id"] = record_id
            response = await client.patch(
                self._get_table_url(table_name),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating record {record_id} in {table_name}: {e}")
            raise
    
    # ============== Product Operations ==============
    
    async def get_products(
        self, 
        sync_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all products, optionally filtered by sync status"""
        filters = {"sync_status": sync_status} if sync_status else None
        return await self.get_all_records(self.PRODUCTS_TABLE)
    
    async def get_pending_products(self) -> List[Dict[str, Any]]:
        """Get products pending sync"""
        all_products = await self.get_products()
        return [p for p in all_products if p.get("sync_status") in [None, "pending", ""]]
    
    async def update_product_sync_status(
        self, 
        record_id: int, 
        odoo_id: int, 
        status: str = "synced"
    ) -> Dict[str, Any]:
        """Update product sync status after Odoo sync"""
        return await self.update_record(
            self.PRODUCTS_TABLE,
            record_id,
            {
                "odoo_id": odoo_id,
                "sync_status": status,
                "last_synced": datetime.utcnow().isoformat()
            }
        )
    
    async def mark_product_error(
        self, 
        record_id: int, 
        error_message: str
    ) -> Dict[str, Any]:
        """Mark a product as having sync error"""
        return await self.update_record(
            self.PRODUCTS_TABLE,
            record_id,
            {
                "sync_status": "error",
                "last_synced": datetime.utcnow().isoformat()
            }
        )
    
    # ============== Contact Operations ==============
    
    async def get_contacts(
        self, 
        sync_status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all contacts, optionally filtered by sync status"""
        filters = {"sync_status": sync_status} if sync_status else None
        return await self.get_all_records(self.CONTACTS_TABLE)
    
    async def get_pending_contacts(self) -> List[Dict[str, Any]]:
        """Get contacts pending sync"""
        all_contacts = await self.get_contacts()
        return [c for c in all_contacts if c.get("sync_status") in [None, "pending", ""]]
    
    async def update_contact_sync_status(
        self, 
        record_id: int, 
        odoo_id: int, 
        status: str = "synced"
    ) -> Dict[str, Any]:
        """Update contact sync status after Odoo sync"""
        return await self.update_record(
            self.CONTACTS_TABLE,
            record_id,
            {
                "odoo_id": odoo_id,
                "sync_status": status,
                "last_synced": datetime.utcnow().isoformat()
            }
        )
    
    async def mark_contact_error(
        self, 
        record_id: int, 
        error_message: str
    ) -> Dict[str, Any]:
        """Mark a contact as having sync error"""
        return await self.update_record(
            self.CONTACTS_TABLE,
            record_id,
            {
                "sync_status": "error",
                "last_synced": datetime.utcnow().isoformat()
            }
        )


# Singleton instance
_nocodb_service: Optional[NocoDBService] = None


def get_nocodb_service() -> NocoDBService:
    """Get or create NocoDB service instance"""
    global _nocodb_service
    if _nocodb_service is None:
        _nocodb_service = NocoDBService()
    return _nocodb_service
