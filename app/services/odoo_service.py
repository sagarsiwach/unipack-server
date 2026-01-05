"""
Odoo XML-RPC Service
Handles all communication with Odoo ERP
"""

import xmlrpc.client
import ssl
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


class OdooService:
    """Service for interacting with Odoo via XML-RPC"""
    
    def __init__(self):
        self.settings = get_settings()
        self.url = self.settings.odoo_url
        self.db = self.settings.odoo_db
        self.username = self.settings.odoo_user
        self.password = self.settings.odoo_password
        self._uid: Optional[int] = None
        self._common: Optional[xmlrpc.client.ServerProxy] = None
        self._models: Optional[xmlrpc.client.ServerProxy] = None
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context for HTTPS connections"""
        context = ssl.create_default_context()
        return context
    
    @property
    def common(self) -> xmlrpc.client.ServerProxy:
        """Get common endpoint proxy (lazy initialization)"""
        if self._common is None:
            context = self._create_ssl_context()
            self._common = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/common',
                context=context
            )
        return self._common
    
    @property
    def models(self) -> xmlrpc.client.ServerProxy:
        """Get models endpoint proxy (lazy initialization)"""
        if self._models is None:
            context = self._create_ssl_context()
            self._models = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/object',
                context=context
            )
        return self._models
    
    def authenticate(self) -> Optional[int]:
        """Authenticate with Odoo and return user ID"""
        try:
            self._uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
            if self._uid:
                logger.info(f"Authenticated with Odoo as user ID: {self._uid}")
            else:
                logger.error("Odoo authentication failed - invalid credentials")
            return self._uid
        except Exception as e:
            logger.error(f"Odoo authentication error: {e}")
            return None
    
    @property
    def uid(self) -> Optional[int]:
        """Get authenticated user ID (authenticates if needed)"""
        if self._uid is None:
            self.authenticate()
        return self._uid
    
    def check_connection(self) -> bool:
        """Check if Odoo connection is working"""
        try:
            version = self.common.version()
            logger.info(f"Odoo version: {version.get('server_version', 'unknown')}")
            return self.uid is not None
        except Exception as e:
            logger.error(f"Odoo connection check failed: {e}")
            return False
    
    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute a method on an Odoo model"""
        if not self.uid:
            raise Exception("Not authenticated with Odoo")
        
        try:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, list(args), kwargs
            )
        except Exception as e:
            logger.error(f"Odoo execute error on {model}.{method}: {e}")
            raise
    
    # ============== Product Methods ==============
    
    def create_product(self, data: Dict[str, Any]) -> int:
        """Create a new product in Odoo"""
        product_data = {
            'name': data['name'],
            'detailed_type': 'product',  # Can be 'consu' (consumable) or 'service'
        }
        
        # Optional fields
        if data.get('price') or data.get('sales_price'):
            product_data['list_price'] = data.get('price') or data.get('sales_price', 0)
        
        if data.get('cost'):
            product_data['standard_price'] = data['cost']
        
        if data.get('internal_ref'):
            product_data['default_code'] = data['internal_ref']
        
        if data.get('description'):
            product_data['description_sale'] = data['description']
        
        # Handle category
        if data.get('category'):
            category_id = self._get_or_create_category(data['category'])
            if category_id:
                product_data['categ_id'] = category_id
        
        product_id = self.execute('product.template', 'create', product_data)
        logger.info(f"Created product in Odoo: {data['name']} (ID: {product_id})")
        return product_id
    
    def update_product(self, odoo_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing product in Odoo"""
        product_data = {}
        
        if 'name' in data:
            product_data['name'] = data['name']
        
        if data.get('price') or data.get('sales_price'):
            product_data['list_price'] = data.get('price') or data.get('sales_price')
        
        if data.get('cost'):
            product_data['standard_price'] = data['cost']
        
        if data.get('internal_ref'):
            product_data['default_code'] = data['internal_ref']
        
        if data.get('description'):
            product_data['description_sale'] = data['description']
        
        if data.get('category'):
            category_id = self._get_or_create_category(data['category'])
            if category_id:
                product_data['categ_id'] = category_id
        
        if product_data:
            self.execute('product.template', 'write', [odoo_id], product_data)
            logger.info(f"Updated product in Odoo: ID {odoo_id}")
            return True
        return False
    
    def search_product_by_name(self, name: str) -> Optional[int]:
        """Search for a product by name"""
        products = self.execute(
            'product.template', 'search',
            [['name', '=', name]], limit=1
        )
        return products[0] if products else None
    
    def _get_or_create_category(self, category_name: str) -> Optional[int]:
        """Get or create a product category"""
        try:
            # Search for existing category
            categories = self.execute(
                'product.category', 'search',
                [['name', '=', category_name]], limit=1
            )
            
            if categories:
                return categories[0]
            
            # Create new category
            category_id = self.execute(
                'product.category', 'create',
                {'name': category_name}
            )
            logger.info(f"Created product category: {category_name}")
            return category_id
        except Exception as e:
            logger.warning(f"Could not get/create category '{category_name}': {e}")
            return None
    
    # ============== Contact/Partner Methods ==============
    
    def create_contact(self, data: Dict[str, Any]) -> int:
        """Create a new contact (res.partner) in Odoo"""
        partner_data = {
            'name': data['name'],
            'is_company': bool(data.get('company_name')),
        }
        
        # Map fields
        field_mapping = {
            'email': 'email',
            'phone': 'phone',
            'mobile': 'mobile',
            'street': 'street',
            'city': 'city',
        }
        
        for source, target in field_mapping.items():
            if data.get(source):
                partner_data[target] = data[source]
        
        # Handle company name
        if data.get('company_name') or data.get('company'):
            partner_data['name'] = data.get('company_name') or data.get('company') or data['name']
        
        # Handle state/country
        if data.get('state'):
            state_id = self._get_state_id(data['state'], data.get('country'))
            if state_id:
                partner_data['state_id'] = state_id
        
        if data.get('country'):
            country_id = self._get_country_id(data['country'])
            if country_id:
                partner_data['country_id'] = country_id
        
        # Customer/Vendor flags (Odoo 14+ uses different field names)
        # In Odoo 16/17, these are handled via customer_rank/supplier_rank
        if data.get('is_customer'):
            partner_data['customer_rank'] = 1
        
        if data.get('is_vendor'):
            partner_data['supplier_rank'] = 1
        
        # Tags
        if data.get('tags'):
            tag_ids = self._get_or_create_partner_tags(data['tags'])
            if tag_ids:
                partner_data['category_id'] = [(6, 0, tag_ids)]
        
        partner_id = self.execute('res.partner', 'create', partner_data)
        logger.info(f"Created contact in Odoo: {data['name']} (ID: {partner_id})")
        return partner_id
    
    def update_contact(self, odoo_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing contact in Odoo"""
        partner_data = {}
        
        field_mapping = {
            'name': 'name',
            'email': 'email',
            'phone': 'phone',
            'mobile': 'mobile',
            'street': 'street',
            'city': 'city',
        }
        
        for source, target in field_mapping.items():
            if source in data and data[source]:
                partner_data[target] = data[source]
        
        if data.get('is_customer'):
            partner_data['customer_rank'] = 1
        
        if data.get('is_vendor'):
            partner_data['supplier_rank'] = 1
        
        if partner_data:
            self.execute('res.partner', 'write', [odoo_id], partner_data)
            logger.info(f"Updated contact in Odoo: ID {odoo_id}")
            return True
        return False
    
    def search_contact_by_email(self, email: str) -> Optional[int]:
        """Search for a contact by email"""
        if not email:
            return None
        partners = self.execute(
            'res.partner', 'search',
            [['email', '=', email]], limit=1
        )
        return partners[0] if partners else None
    
    def search_contact_by_name(self, name: str) -> Optional[int]:
        """Search for a contact by name"""
        partners = self.execute(
            'res.partner', 'search',
            [['name', '=', name]], limit=1
        )
        return partners[0] if partners else None
    
    def _get_country_id(self, country_name: str) -> Optional[int]:
        """Get country ID by name or code"""
        try:
            countries = self.execute(
                'res.country', 'search',
                ['|', ['name', 'ilike', country_name], ['code', '=', country_name.upper()]],
                limit=1
            )
            return countries[0] if countries else None
        except Exception:
            return None
    
    def _get_state_id(self, state_name: str, country_name: Optional[str] = None) -> Optional[int]:
        """Get state ID by name"""
        try:
            domain = [['name', 'ilike', state_name]]
            if country_name:
                country_id = self._get_country_id(country_name)
                if country_id:
                    domain.append(['country_id', '=', country_id])
            
            states = self.execute('res.country.state', 'search', domain, limit=1)
            return states[0] if states else None
        except Exception:
            return None
    
    def _get_or_create_partner_tags(self, tags_str: str) -> List[int]:
        """Get or create partner category tags from comma-separated string"""
        tag_ids = []
        tags = [t.strip() for t in tags_str.split(',') if t.strip()]
        
        for tag_name in tags:
            try:
                # Search existing
                existing = self.execute(
                    'res.partner.category', 'search',
                    [['name', '=', tag_name]], limit=1
                )
                
                if existing:
                    tag_ids.append(existing[0])
                else:
                    # Create new
                    new_id = self.execute(
                        'res.partner.category', 'create',
                        {'name': tag_name}
                    )
                    tag_ids.append(new_id)
            except Exception as e:
                logger.warning(f"Could not get/create tag '{tag_name}': {e}")
        
        return tag_ids


# Singleton instance
_odoo_service: Optional[OdooService] = None


def get_odoo_service() -> OdooService:
    """Get or create Odoo service instance"""
    global _odoo_service
    if _odoo_service is None:
        _odoo_service = OdooService()
    return _odoo_service
