"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SyncStatus(str, Enum):
    """Sync status enumeration"""
    PENDING = "pending"
    SYNCED = "synced"
    ERROR = "error"


# ============== Product Models ==============

class ProductBase(BaseModel):
    """Base product model with common fields"""
    name: str = Field(..., alias="product_name", min_length=1)
    internal_ref: Optional[str] = None
    category: Optional[str] = None
    sales_price: Optional[float] = Field(None, alias="list_price")
    cost: Optional[float] = None
    description: Optional[str] = None

    class Config:
        populate_by_name = True


class ProductCreate(BaseModel):
    """Product creation request model"""
    name: str = Field(..., min_length=1)
    price: Optional[float] = None
    category: Optional[str] = None
    internal_ref: Optional[str] = None
    cost: Optional[float] = None
    description: Optional[str] = None


class ProductResponse(BaseModel):
    """Product response model"""
    id: int
    name: str
    success: bool = True
    message: Optional[str] = None


class NocoDBProduct(BaseModel):
    """NocoDB Product record model"""
    Id: Optional[int] = None
    product_name: str
    internal_ref: Optional[str] = None
    category: Optional[str] = None
    sales_price: Optional[float] = None
    cost: Optional[float] = None
    description: Optional[str] = None
    odoo_id: Optional[int] = None
    sync_status: Optional[str] = "pending"
    last_synced: Optional[datetime] = None


# ============== Contact Models ==============

class ContactBase(BaseModel):
    """Base contact model with common fields"""
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    company_name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_customer: Optional[bool] = False
    is_vendor: Optional[bool] = False
    tags: Optional[str] = None


class ContactCreate(BaseModel):
    """Contact creation request model"""
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    company: Optional[str] = Field(None, alias="company_name")
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_customer: Optional[bool] = True
    is_vendor: Optional[bool] = False
    tags: Optional[str] = None

    class Config:
        populate_by_name = True


class ContactResponse(BaseModel):
    """Contact response model"""
    id: int
    name: str
    success: bool = True
    message: Optional[str] = None


class NocoDBContact(BaseModel):
    """NocoDB Contact record model"""
    Id: Optional[int] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    company_name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_customer: Optional[bool] = False
    is_vendor: Optional[bool] = False
    tags: Optional[str] = None
    odoo_id: Optional[int] = None
    sync_status: Optional[str] = "pending"
    last_synced: Optional[datetime] = None


# ============== Sync Response Models ==============

class SyncResult(BaseModel):
    """Sync operation result model"""
    success: bool
    created: int = 0
    updated: int = 0
    errors: List[str] = []
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    odoo: bool
    nocodb: bool
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
