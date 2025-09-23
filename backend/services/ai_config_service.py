"""AI configuration management service for expense tracker."""

import logging
import threading
from typing import Dict, Any, Optional
from fastapi import HTTPException

from core.models import LLMConfigResponse, LLMUpdateRequest
from providers.llms import LLMProviderFactory
from config import get_settings


class AIConfigService:
    """Service for managing AI provider configuration at runtime."""
    
    def __init__(self):
        self.config_lock = threading.Lock()
        self._current_llm = None
        
    def get_current_llm_config(self) -> LLMConfigResponse:
        """Get current LLM configuration (sanitized, no secrets)."""
        settings = get_settings()
        config_details = settings.current_llm_config()
        
        return LLMConfigResponse(
            provider=settings.llm_provider,
            model_name=config_details.get("model", "Not configured"),
            temperature=config_details.get("temperature", 0.7),
            max_tokens=config_details.get("max_tokens", 1000),
            details=config_details
        )

    def update_llm_provider(self, request: LLMUpdateRequest) -> LLMConfigResponse:
        """Update LLM provider and settings at runtime."""
        settings = get_settings()
        
        with self.config_lock:
            try:
                # Update settings in-memory
                settings.update_llm_settings(
                    request.provider,
                    llm_temperature=getattr(request, 'llm_temperature', None),
                    openai_api_key=getattr(request, 'openai_api_key', None),
                    openai_model=getattr(request, 'openai_model', None),
                    ollama_llm_model=getattr(request, 'ollama_llm_model', None),
                    ollama_base_url=getattr(request, 'ollama_base_url', None),
                    azure_api_key=getattr(request, 'azure_api_key', None),
                    azure_endpoint=getattr(request, 'azure_endpoint', None),
                    azure_llm_deployment=getattr(request, 'azure_llm_deployment', None),
                    bedrock_model_id=getattr(request, 'bedrock_model_id', None),
                    aws_region=getattr(request, 'aws_region', None),
                )
                
                # Test the new configuration by creating LLM instance
                test_llm = LLMProviderFactory.create_llm()
                self._current_llm = test_llm
                
                logging.info(f"Successfully updated LLM provider to: {request.provider}")
                
            except ValueError as e:
                logging.error(f"Invalid LLM configuration: {e}")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logging.error(f"Failed to update LLM provider: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to update LLM: {e}")
        
        return self.get_current_llm_config()
    
    def get_llm_instance(self):
        """Get current LLM instance for financial advice generation."""
        if self._current_llm is None:
            # Create default LLM instance
            self._current_llm = LLMProviderFactory.create_llm()
        return self._current_llm
    
    def health_check(self) -> Dict[str, Any]:
        """Check AI service health."""
        settings = get_settings()
        return {
            "status": "healthy",
            "llm_provider": settings.llm_provider,
            "llm_configured": self._current_llm is not None,
            "available_providers": ["openai", "ollama", "azure", "bedrock"]
        }