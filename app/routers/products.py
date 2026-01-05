"""
Products Router
Single product operations
"""

from fastapi import APIRouter, HTTPException, status
import logging

from ..models import ProductCreate, ProductResponse
from ..services.odoo_service import get_odoo_service

router = APIRouter(prefix="/products", tags=["Products"])
logger = logging.getLogger(__name__)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_product(product: ProductCreate):
    """
    Create a single product directly in Odoo
    
    Args:
        product: Product data to create
    
    Returns:
        ProductResponse with the created product ID
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
        
        # Prepare product data
        product_data = {
            "name": product.name,
            "price": product.price,
            "category": product.category,
            "internal_ref": product.internal_ref,
            "cost": product.cost,
            "description": product.description,
        }
        
        # Create product in Odoo
        product_id = odoo.create_product(product_data)
        
        logger.info(f"Created product '{product.name}' with Odoo ID: {product_id}")
        
        return ProductResponse(
            id=product_id,
            name=product.name,
            success=True,
            message=f"Product created successfully in Odoo"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}"
        )


@router.get("/{product_id}")
async def get_product(product_id: int):
    """
    Get a product from Odoo by ID
    
    Args:
        product_id: Odoo product ID
    
    Returns:
        Product data from Odoo
    """
    try:
        odoo = get_odoo_service()
        
        if not odoo.uid:
            if not odoo.authenticate():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to authenticate with Odoo"
                )
        
        # Read product from Odoo
        products = odoo.execute(
            'product.template', 'read',
            [product_id],
            {'fields': ['name', 'list_price', 'standard_price', 'default_code', 'categ_id', 'description_sale']}
        )
        
        if not products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found"
            )
        
        product = products[0]
        return {
            "id": product["id"],
            "name": product["name"],
            "price": product.get("list_price", 0),
            "cost": product.get("standard_price", 0),
            "internal_ref": product.get("default_code"),
            "category": product.get("categ_id", [None, None])[1] if product.get("categ_id") else None,
            "description": product.get("description_sale")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch product: {str(e)}"
        )
