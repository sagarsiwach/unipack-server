"""
AI Service using Google Gemini
"""

import logging
from typing import Optional

from ..config import get_settings

logger = logging.getLogger(__name__)

# Try to import Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed, AI features disabled")


class AIService:
    """Service for AI content generation using Gemini"""
    
    def __init__(self):
        self.settings = get_settings()
        self._model = None
        
        if GEMINI_AVAILABLE and self.settings.gemini_api_key:
            genai.configure(api_key=self.settings.gemini_api_key)
            self._model = genai.GenerativeModel('gemini-2.0-flash')
    
    @property
    def is_available(self) -> bool:
        return self._model is not None
    
    def generate_product_name(
        self, 
        product_code: str, 
        machine_name: str, 
        size: str = "Standard"
    ) -> str:
        """Generate a professional product name"""
        if not self.is_available:
            return f"UniPack {machine_name}"
        
        try:
            prompt = f"""Generate a professional, sales-friendly product name for:
- Machine Code: {product_code}
- Machine Type: {machine_name}
- Size: {size}

Return ONLY the product name, no explanation.
Example format: "UniPack Smart Line 120 (3-Ply)"
"""
            response = self._model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return f"UniPack {machine_name}"
    
    def generate_product_description(
        self, 
        product_name: str, 
        category: str = "", 
        specifications: str = ""
    ) -> str:
        """Generate a professional product description"""
        if not self.is_available:
            return f"{product_name} - Professional corrugated packaging equipment."
        
        try:
            prompt = f"""Generate a professional, SEO-friendly product description for:
- Product: {product_name}
- Category: {category or "Industrial Machinery"}
- Specifications: {specifications or "Standard"}

Write 2-3 paragraphs highlighting key features and benefits.
Focus on: reliability, efficiency, quality output, and ROI.
"""
            response = self._model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return f"{product_name} - Professional corrugated packaging equipment."


# Singleton
_ai_service: Optional[AIService] = None

def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
