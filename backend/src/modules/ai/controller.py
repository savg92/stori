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


@router.get("/health")
async def ai_health():
    """AI service health check."""
    try:
        # Test LLM provider availability
        llm_provider = get_llm_provider()
        llm_status = "available" if llm_provider else "unavailable"
        
        return {
            "status": "healthy",
            "service": "ai_chat_advice",
            "capabilities": ["chat", "financial_advice"],
            "llm_status": llm_status,
            "endpoints": ["/chat", "/advice"],
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "ai_chat_advice", 
            "error": str(e),
            "endpoints": ["/chat", "/advice"],
            "version": "1.0.0"
        }