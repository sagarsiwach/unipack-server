"""
Configuration settings for UniPack API
Loads from environment variables with sensible defaults
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "UniPack API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # NocoDB Configuration
    nocodb_url: str = "https://noco.unipack.asia"
    nocodb_api_token: str = ""
    nocodb_base_id: str = ""  # Will be set after creating the base
    
    # Odoo Configuration
    odoo_url: str = "https://erp.unipack.asia"
    odoo_db: str = "unipack"
    odoo_user: str = "hello@unipack.asia"
    odoo_password: str = ""
    
    # API Configuration
    api_prefix: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
