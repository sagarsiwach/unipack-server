"""
Configuration settings for UniPack API
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    app_name: str = "UniPack API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Authentication
    api_key: str = "unipack-api-key-2024"
    
    # Odoo Configuration
    odoo_url: str = "https://erp.unipack.asia"
    odoo_db: str = "unipack"
    odoo_user: str = "hello@unipack.asia"
    odoo_api_key: str = "8452eb0dc0dc4a3e1bcf8aae9c5cce53b0cd41f4"
    
    # Gemini AI
    gemini_api_key: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
