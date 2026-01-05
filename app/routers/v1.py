"""
API v1 Router - All endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..auth import verify_token
from ..config import get_settings
from ..models import (
    HealthResponse,
    CategoriesResponse, TaxesResponse, CountriesResponse,
    ProductBatchRequest, ProductBatchResponse, ProductResult,
    CustomerBatchRequest, CustomerBatchResponse, CustomerResult,
    AIGenerateNameRequest, AIGenerateNameResponse,
    AIGenerateDescriptionRequest, AIGenerateDescriptionResponse,
)
from ..services.odoo_service import get_odoo_service
from ..services.ai_service import get_ai_service

router = APIRouter()


# ============== Health ==============

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check - no auth required"""
    settings = get_settings()
    try:
        odoo = get_odoo_service()
        connected = odoo.check_connection()
        return HealthResponse(
            status="ok" if connected else "error",
            odoo_connected=connected,
            version=settings.app_version
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            odoo_connected=False,
            version=settings.app_version,
            error=str(e)
        )


# ============== Reference Data ==============

@router.get("/reference/categories", response_model=CategoriesResponse)
async def get_categories(token: str = Depends(verify_token)):
    """Get product categories from Odoo"""
    odoo = get_odoo_service()
    categories = odoo.get_categories()
    return CategoriesResponse(success=True, categories=categories)


@router.get("/reference/taxes", response_model=TaxesResponse)
async def get_taxes(token: str = Depends(verify_token)):
    """Get sales taxes from Odoo"""
    odoo = get_odoo_service()
    taxes = odoo.get_taxes()
    return TaxesResponse(success=True, taxes=taxes)


@router.get("/reference/countries", response_model=CountriesResponse)
async def get_countries(token: str = Depends(verify_token)):
    """Get countries from Odoo"""
    odoo = get_odoo_service()
    countries = odoo.get_countries()
    return CountriesResponse(success=True, countries=countries)


# ============== Products ==============

@router.post("/products/batch", response_model=ProductBatchResponse)
async def batch_create_products(
    request: ProductBatchRequest,
    token: str = Depends(verify_token)
):
    """Batch create/update products in Odoo"""
    odoo = get_odoo_service()
    ai = get_ai_service()
    results = []
    
    for product in request.products:
        data = product.model_dump()
        
        # Optional AI content generation
        if request.generate_ai_content and ai.is_available:
            if not data.get('product_name') and data.get('product_code'):
                data['product_name'] = ai.generate_product_name(
                    data['product_code'],
                    data.get('machine_name', 'Machine'),
                    data.get('size', 'Standard')
                )
        
        result = odoo.create_or_update_product(data)
        results.append(ProductResult(**result))
    
    return ProductBatchResponse(
        success=all(r.success for r in results),
        results=results
    )


# ============== Customers ==============

@router.post("/customers/batch", response_model=CustomerBatchResponse)
async def batch_create_customers(
    request: CustomerBatchRequest,
    token: str = Depends(verify_token)
):
    """Batch create/update customers in Odoo"""
    odoo = get_odoo_service()
    results = []
    
    for customer in request.customers:
        result = odoo.create_or_update_customer(customer.model_dump())
        results.append(CustomerResult(**result))
    
    return CustomerBatchResponse(
        success=all(r.success for r in results),
        results=results
    )


# ============== AI ==============

@router.post("/ai/generate-name", response_model=AIGenerateNameResponse)
async def ai_generate_name(
    request: AIGenerateNameRequest,
    token: str = Depends(verify_token)
):
    """Generate product name using AI"""
    ai = get_ai_service()
    name = ai.generate_product_name(
        request.product_code,
        request.machine_name,
        request.size
    )
    return AIGenerateNameResponse(success=True, name=name)


@router.post("/ai/generate-description", response_model=AIGenerateDescriptionResponse)
async def ai_generate_description(
    request: AIGenerateDescriptionRequest,
    token: str = Depends(verify_token)
):
    """Generate product description using AI"""
    ai = get_ai_service()
    description = ai.generate_product_description(
        request.product_name,
        request.category,
        request.specifications
    )
    return AIGenerateDescriptionResponse(success=True, description=description)
