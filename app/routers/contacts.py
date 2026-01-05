"""
Contacts Router
Single contact operations
"""

from fastapi import APIRouter, HTTPException, status
import logging

from ..models import ContactCreate, ContactResponse
from ..services.odoo_service import get_odoo_service

router = APIRouter(prefix="/contacts", tags=["Contacts"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_contact(contact: ContactCreate):
    """
    Create a single contact directly in Odoo
    
    Args:
        contact: Contact data to create
    
    Returns:
        ContactResponse with the created contact ID
    """
    try:
        odoo = get_odoo_service()
        
        # Ensure authenticated
        if not odoo.uid:
            if not odoo.authenticate():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to authenticate with Odoo"
                )
        
        # Prepare contact data
        contact_data = {
            "name": contact.name,
            "email": contact.email,
            "phone": contact.phone,
            "mobile": contact.mobile,
            "company_name": contact.company,
            "street": contact.street,
            "city": contact.city,
            "state": contact.state,
            "country": contact.country,
            "is_customer": contact.is_customer,
            "is_vendor": contact.is_vendor,
            "tags": contact.tags,
        }
        
        # Create contact in Odoo
        contact_id = odoo.create_contact(contact_data)
        
        logger.info(f"Created contact '{contact.name}' with Odoo ID: {contact_id}")
        
        return ContactResponse(
            id=contact_id,
            name=contact.name,
            success=True,
            message=f"Contact created successfully in Odoo"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create contact: {str(e)}"
        )


@router.get("/{contact_id}")
async def get_contact(contact_id: int):
    """
    Get a contact from Odoo by ID
    
    Args:
        contact_id: Odoo contact/partner ID
    
    Returns:
        Contact data from Odoo
    """
    try:
        odoo = get_odoo_service()
        
        if not odoo.uid:
            if not odoo.authenticate():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to authenticate with Odoo"
                )
        
        # Read contact from Odoo
        contacts = odoo.execute(
            'res.partner', 'read',
            [contact_id],
            {'fields': ['name', 'email', 'phone', 'mobile', 'street', 'city', 'state_id', 'country_id', 'is_company', 'customer_rank', 'supplier_rank']}
        )
        
        if not contacts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact with ID {contact_id} not found"
            )
        
        contact = contacts[0]
        return {
            "id": contact["id"],
            "name": contact["name"],
            "email": contact.get("email"),
            "phone": contact.get("phone"),
            "mobile": contact.get("mobile"),
            "street": contact.get("street"),
            "city": contact.get("city"),
            "state": contact.get("state_id", [None, None])[1] if contact.get("state_id") else None,
            "country": contact.get("country_id", [None, None])[1] if contact.get("country_id") else None,
            "is_company": contact.get("is_company", False),
            "is_customer": contact.get("customer_rank", 0) > 0,
            "is_vendor": contact.get("supplier_rank", 0) > 0,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching contact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch contact: {str(e)}"
        )
