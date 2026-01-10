"""
API v1 Router - All endpoints (Parallel-safe version)
Updated: 2026-01-10 - Added ThreadPoolExecutor for parallel processing
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

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
logger = logging.getLogger(__name__)

# Thread pool for blocking Odoo operations (10 workers = 10 concurrent Odoo calls)
executor = ThreadPoolExecutor(max_workers=10)


# ============== Health ==============

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check - no auth required"""
    settings = get_settings()
    try:
        odoo = get_odoo_service()
        # Run blocking check in thread to not block event loop
        connected = await asyncio.get_event_loop().run_in_executor(
            executor, odoo.check_connection
        )
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
    categories = await asyncio.get_event_loop().run_in_executor(
        executor, odoo.get_categories
    )
    return CategoriesResponse(success=True, categories=categories)


@router.get("/reference/taxes", response_model=TaxesResponse)
async def get_taxes(token: str = Depends(verify_token)):
    """Get sales taxes from Odoo"""
    odoo = get_odoo_service()
    taxes = await asyncio.get_event_loop().run_in_executor(
        executor, odoo.get_taxes
    )
    return TaxesResponse(success=True, taxes=taxes)


@router.get("/reference/countries", response_model=CountriesResponse)
async def get_countries(token: str = Depends(verify_token)):
    """Get countries from Odoo"""
    odoo = get_odoo_service()
    countries = await asyncio.get_event_loop().run_in_executor(
        executor, odoo.get_countries
    )
    return CountriesResponse(success=True, countries=countries)


# ============== Products ==============

def _process_single_product(product_data: dict, generate_ai: bool = False) -> dict:
    """Process a single product (runs in thread pool)"""
    odoo = get_odoo_service()
    ai = get_ai_service()

    data = product_data

    # Optional AI content generation
    if generate_ai and ai.is_available:
        if not data.get('product_name') and data.get('product_code'):
            data['product_name'] = ai.generate_product_name(
                data['product_code'],
                data.get('machine_name', 'Machine'),
                data.get('size', 'Standard')
            )

    return odoo.create_or_update_product(data)


@router.post("/products/batch", response_model=ProductBatchResponse)
async def batch_create_products(
    request: ProductBatchRequest,
    token: str = Depends(verify_token)
):
    """Batch create/update products in Odoo (parallel processing)"""
    loop = asyncio.get_event_loop()

    # Process all products in parallel using thread pool
    tasks = [
        loop.run_in_executor(
            executor,
            _process_single_product,
            product.model_dump(),
            request.generate_ai_content
        )
        for product in request.products
    ]

    # Wait for all to complete
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    for r in raw_results:
        if isinstance(r, Exception):
            results.append(ProductResult(success=False, id=None, message=str(r)))
        else:
            results.append(ProductResult(**r))

    return ProductBatchResponse(
        success=all(r.success for r in results),
        results=results
    )


# ============== Customers ==============

def _process_single_customer(customer_data: dict) -> dict:
    """Process a single customer (runs in thread pool)"""
    odoo = get_odoo_service()
    return odoo.create_or_update_customer(customer_data)


@router.post("/customers/batch", response_model=CustomerBatchResponse)
async def batch_create_customers(
    request: CustomerBatchRequest,
    token: str = Depends(verify_token)
):
    """Batch create/update customers in Odoo (parallel processing)"""
    loop = asyncio.get_event_loop()

    # Process all customers in parallel using thread pool
    tasks = [
        loop.run_in_executor(
            executor,
            _process_single_customer,
            customer.model_dump()
        )
        for customer in request.customers
    ]

    # Wait for all to complete
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    for r in raw_results:
        if isinstance(r, Exception):
            results.append(CustomerResult(success=False, id=None, message=str(r)))
        else:
            results.append(CustomerResult(**r))

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

    def _generate():
        return ai.generate_product_name(
            request.product_code,
            request.machine_name,
            request.size
        )

    name = await asyncio.get_event_loop().run_in_executor(executor, _generate)
    return AIGenerateNameResponse(success=True, name=name)


@router.post("/ai/generate-description", response_model=AIGenerateDescriptionResponse)
async def ai_generate_description(
    request: AIGenerateDescriptionRequest,
    token: str = Depends(verify_token)
):
    """Generate product description using AI"""
    ai = get_ai_service()

    def _generate():
        return ai.generate_product_description(
            request.product_name,
            request.category,
            request.specifications
        )

    description = await asyncio.get_event_loop().run_in_executor(executor, _generate)
    return AIGenerateDescriptionResponse(success=True, description=description)
