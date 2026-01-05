"""
Pydantic models for API request/response
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime


# ============== Product Models ==============

class Product(BaseModel):
    """Product for batch creation"""
    product_code: Optional[str] = ""
    product_name: str
    category_id: Optional[int] = 1
    sales_price: Optional[float] = 0
    cost: Optional[float] = 0
    description: Optional[str] = ""
    hsn_code: Optional[str] = ""
    sales_tax_id: Optional[int] = None


class ProductBatchRequest(BaseModel):
    """Batch product creation request"""
    products: List[Product]
    generate_ai_content: bool = False


class ProductResult(BaseModel):
    """Single product operation result"""
    success: bool
    id: Optional[int] = None
    message: str


class ProductBatchResponse(BaseModel):
    """Batch product response"""
    success: bool
    results: List[ProductResult]


# ============== Customer Models ==============

class Customer(BaseModel):
    """Customer for batch creation"""
    company_name: str
    contact_name: Optional[str] = ""
    mobile: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    address_line_1: Optional[str] = ""
    address_line_2: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    pincode: Optional[str] = ""
    gst_number: Optional[str] = ""
    pan: Optional[str] = ""
    customer_type: Optional[str] = "B2B"


class CustomerBatchRequest(BaseModel):
    """Batch customer creation request"""
    customers: List[Customer]


class CustomerResult(BaseModel):
    """Single customer operation result"""
    success: bool
    id: Optional[int] = None
    message: str


class CustomerBatchResponse(BaseModel):
    """Batch customer response"""
    success: bool
    results: List[CustomerResult]


# ============== Reference Data Models ==============

class Category(BaseModel):
    """Product category"""
    id: int
    name: str
    complete_name: Optional[str] = None


class Tax(BaseModel):
    """Tax record"""
    id: int
    name: str
    amount: float


class Country(BaseModel):
    """Country record"""
    id: int
    name: str
    code: str


class CategoriesResponse(BaseModel):
    success: bool
    categories: List[Category]


class TaxesResponse(BaseModel):
    success: bool
    taxes: List[Tax]


class CountriesResponse(BaseModel):
    success: bool
    countries: List[Country]


# ============== AI Models ==============

class AIGenerateNameRequest(BaseModel):
    """AI name generation request"""
    product_code: str
    machine_name: str
    size: Optional[str] = "Standard"


class AIGenerateNameResponse(BaseModel):
    success: bool
    name: str


class AIGenerateDescriptionRequest(BaseModel):
    """AI description generation request"""
    product_name: str
    category: Optional[str] = ""
    specifications: Optional[str] = ""


class AIGenerateDescriptionResponse(BaseModel):
    success: bool
    description: str


# ============== Health Check ==============

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    odoo_connected: bool
    version: str
    error: Optional[str] = None
