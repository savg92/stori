"""Clean AI controller with only essential LLM-powered endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from services.supabase_service import SupabaseClient, get_supabase_client
from services.auth_middleware import get_current_user
from providers.llms import LLMProviderFactory
from .repository import AIRepository
from .service import AIService
from .schemas import (
    AdviceRequest,
    AIAdviceResponse,
    ChatRequest,
    ChatResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


def get_llm_provider():
    """Dependency to get LLM provider."""
    return LLMProviderFactory.create_llm()


def get_ai_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
    llm_provider=Depends(get_llm_provider)
) -> AIService:
    """Dependency to get AI service."""
    repository = AIRepository(supabase_client)
    return AIService(repository, llm_provider)


@router.get("/debug")
async def debug_config():
    """Debug endpoint to check AI configuration (without exposing secrets)."""
    try:
        from config.settings import get_settings
        settings = get_settings()
        
        return {
            "llm_provider": settings.llm_provider,
            "has_openrouter_api_key": bool(settings.openrouter_api_key),
            "openrouter_model": settings.openrouter_model,
            "has_supabase_url": bool(settings.supabase_url),
            "has_supabase_key": bool(settings.supabase_key),
            "has_jwt_secret": bool(settings.supabase_jwt_secret),
            "environment_check": "ok"
        }
    except Exception as e:
        logger.error(f"Error in debug config: {e}")
        return {
            "error": str(e),
            "environment_check": "failed"
        }


@router.get("/health")
async def ai_health():
    """AI service health check."""
    try:
        # Try to create LLM provider
        llm_provider = LLMProviderFactory.create_llm()
        
        return {
            "status": "healthy",
            "llm_available": True,
            "provider": "openrouter",
            "service": "ai_chat"
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "llm_available": False,
            "error": str(e),
            "service": "ai_chat"
        }


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Chat with AI about financial matters using real LLM."""
    try:
        return await service.chat_with_ai(current_user["user_id"], request)
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")


@router.post("/advice", response_model=AIAdviceResponse)
async def get_financial_advice(
    request: AdviceRequest,
    current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Get AI-powered financial advice based on transaction data."""
    try:
        return await service.get_financial_advice(current_user["user_id"], request)
        
    except Exception as e:
        logger.error(f"Error getting financial advice: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate financial advice")