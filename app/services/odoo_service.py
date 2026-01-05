"""
Odoo XML-RPC Service
"""

import xmlrpc.client
import ssl
from typing import Optional, Dict, Any, List
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


class OdooService:
    """Service for Odoo XML-RPC operations"""
    
    INDIA_COUNTRY_ID = 104  # India's ID in Odoo
    
    def __init__(self):
        self.settings = get_settings()
        self.url = self.settings.odoo_url
        self.db = self.settings.odoo_db
        self.username = self.settings.odoo_user
        self.api_key = self.settings.odoo_api_key
        self._uid: Optional[int] = None
        self._common = None
        self._models = None
    
    def _get_ssl_context(self):
        return ssl.create_default_context()
    
    @property
    def common(self):
        if self._common is None:
            self._common = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/common',
                context=self._get_ssl_context()
            )
        return self._common
    
    @property
    def models(self):
        if self._models is None:
            self._models = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/object',
                context=self._get_ssl_context()
            )
        return self._models
    
    def authenticate(self) -> Optional[int]:
        """Authenticate and return uid"""
        try:
            self._uid = self.common.authenticate(
                self.db, self.username, self.api_key, {}
            )
            return self._uid
        except Exception as e:
            logger.error(f"Odoo auth error: {e}")
            return None
    
    @property
    def uid(self) -> Optional[int]:
        if self._uid is None:
            self.authenticate()
        return self._uid
    
    def check_connection(self) -> bool:
        """Check Odoo connection"""
        try:
            self.common.version()
            return self.uid is not None and self.uid > 0
        except Exception as e:
            logger.error(f"Odoo connection error: {e}")
            return False
    
    def execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute Odoo method"""
        if not self.uid:
            raise Exception("Not authenticated")
        return self.models.execute_kw(
            self.db, self.uid, self.api_key,
            model, method, list(args), kwargs
        )
    
    # ============== Reference Data ==============
    
    def get_categories(self) -> List[Dict]:
        """Get product categories"""
        return self.execute(
            'product.category', 'search_read', [],
            fields=['id', 'name', 'complete_name']
        )
    
    def get_taxes(self) -> List[Dict]:
        """Get sales taxes"""
        return self.execute(
            'account.tax', 'search_read',
            [['type_tax_use', '=', 'sale']],
            fields=['id', 'name', 'amount']
        )
    
    def get_countries(self) -> List[Dict]:
        """Get countries"""
        return self.execute(
            'res.country', 'search_read', [],
            fields=['id', 'name', 'code']
        )
    
    def get_state_id(self, state_name: str) -> Optional[int]:
        """Get Indian state ID by name"""
        if not state_name:
            return None
        states = self.execute(
            'res.country.state', 'search',
            [['name', 'ilike', state_name], ['country_id', '=', self.INDIA_COUNTRY_ID]],
            limit=1
        )
        return states[0] if states else None
    
    # ============== Products ==============
    
    def create_or_update_product(self, data: Dict) -> Dict:
        """Create or update a product"""
        try:
            vals = {
                'name': data['product_name'],
                'default_code': data.get('product_code', ''),
                'list_price': data.get('sales_price', 0),
                'standard_price': data.get('cost', 0),
                'categ_id': data.get('category_id', 1),
                'description_sale': data.get('description', ''),
                'type': 'consu',
                'sale_ok': True,
                'purchase_ok': True,
            }
            
            # HSN Code (India localization)
            if data.get('hsn_code'):
                vals['l10n_in_hsn_code'] = data['hsn_code']
            
            # Sales Tax
            if data.get('sales_tax_id'):
                vals['taxes_id'] = [(6, 0, [data['sales_tax_id']])]
            
            # Check if exists by product_code
            existing = None
            if data.get('product_code'):
                existing = self.execute(
                    'product.template', 'search',
                    [['default_code', '=', data['product_code']]],
                    limit=1
                )
            
            if existing:
                self.execute('product.template', 'write', existing, vals)
                return {"success": True, "id": existing[0], "message": "Updated"}
            else:
                new_id = self.execute('product.template', 'create', vals)
                return {"success": True, "id": new_id, "message": "Created"}
                
        except Exception as e:
            return {"success": False, "id": None, "message": str(e)}
    
    # ============== Customers ==============
    
    def create_or_update_customer(self, data: Dict) -> Dict:
        """Create or update a customer (res.partner)"""
        try:
            state_id = self.get_state_id(data.get('state', ''))
            
            vals = {
                'name': data['company_name'],
                'is_company': True,
                'mobile': data.get('mobile', ''),
                'phone': data.get('phone', ''),
                'email': data.get('email', ''),
                'street': data.get('address_line_1', ''),
                'street2': data.get('address_line_2', ''),
                'city': data.get('city', ''),
                'state_id': state_id,
                'zip': data.get('pincode', ''),
                'country_id': self.INDIA_COUNTRY_ID,
                'customer_rank': 1,
            }
            
            # GST Number (India localization)
            if data.get('gst_number'):
                vals['vat'] = data['gst_number']
            
            # PAN (India localization)
            if data.get('pan'):
                vals['l10n_in_pan'] = data['pan']
            
            # Check if exists by GST
            existing = None
            if data.get('gst_number'):
                existing = self.execute(
                    'res.partner', 'search',
                    [['vat', '=', data['gst_number']]],
                    limit=1
                )
            
            if existing:
                self.execute('res.partner', 'write', existing, vals)
                return {"success": True, "id": existing[0], "message": "Updated"}
            else:
                new_id = self.execute('res.partner', 'create', vals)
                return {"success": True, "id": new_id, "message": "Created"}
                
        except Exception as e:
            return {"success": False, "id": None, "message": str(e)}


# Singleton
_odoo_service: Optional[OdooService] = None

def get_odoo_service() -> OdooService:
    global _odoo_service
    if _odoo_service is None:
        _odoo_service = OdooService()
    return _odoo_service
