"""AI controller for API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from services.supabase_service import get_supabase_client
from services.auth_middleware import get_current_user
from providers.llms import LLMProviderFactory
from .repository import AIRepository
from .service import AIService
from .schemas import (
    AdviceRequest,
    AIAdviceResponse,
    AnalysisRequest,
    AnalysisResult,
    ChatRequest,
    ChatResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])


def get_llm_provider():
    """Dependency to get LLM provider."""
    return LLMProviderFactory.create_llm()


def get_ai_service(
    supabase_client: Client = Depends(get_supabase_client),
    llm_provider=Depends(get_llm_provider)
) -> AIService:
    """Dependency to get AI service."""
    repository = AIRepository(supabase_client)
    return AIService(repository, llm_provider)


@router.post("/advice", response_model=AIAdviceResponse)
async def get_financial_advice(
    request: AdviceRequest,
    current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Get AI-powered financial advice based on transaction data."""
    try:
        return await service.get_financial_advice(current_user["sub"], request)
        
    except Exception as e:
        logger.error(f"Error getting financial advice: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate financial advice")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Chat with AI about financial matters."""
    try:
        return await service.chat_with_ai(current_user["sub"], request)
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat request")


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_financial_data(
    request: AnalysisRequest,
    current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Perform AI-powered financial data analysis."""
    try:
        return await service.analyze_financial_data(current_user["sub"], request)
        
    except Exception as e:
        logger.error(f"Error analyzing financial data: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze financial data")


@router.get("/insights/quick")
async def get_quick_insights(
    days_back: int = 30,
    current_user: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """Get quick financial insights for dashboard."""
    try:
        # Get basic financial context
        financial_context = await service.repository.get_financial_context(
            current_user["sub"], days_back
        )
        
        # Generate quick insights
        insights = []
        
        # Net cash flow insight
        if financial_context.net_amount > 0:
            insights.append({
                'type': 'positive',
                'title': 'Positive Cash Flow',
                'message': f'You saved ${financial_context.net_amount:.2f} over the last {days_back} days',
                'icon': '💰'
            })
        else:
            insights.append({
                'type': 'warning',
                'title': 'Negative Cash Flow',
                'message': f'You overspent by ${abs(financial_context.net_amount):.2f} over the last {days_back} days',
                'icon': '⚠️'
            })
        
        # Top category insight
        if financial_context.top_categories:
            top_cat = financial_context.top_categories[0]
            insights.append({
                'type': 'info',
                'title': 'Top Spending Category',
                'message': f'You spent ${top_cat["total_amount"]:.2f} on {top_cat["category"]}',
                'icon': '📊'
            })
        
        # Transaction frequency insight
        daily_txn_rate = financial_context.transaction_count / days_back
        if daily_txn_rate > 3:
            insights.append({
                'type': 'info',
                'title': 'High Transaction Frequency',
                'message': f'You make {daily_txn_rate:.1f} transactions per day on average',
                'icon': '🔄'
            })
        
        return {
            'insights': insights,
            'period_days': days_back,
            'total_transactions': financial_context.transaction_count,
            'financial_summary': {
                'income': float(financial_context.total_income),
                'expenses': float(financial_context.total_expenses),
                'net': float(financial_context.net_amount)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting quick insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get quick insights")


@router.get("/health")
async def get_ai_health():
    """Get AI service health and capabilities."""
    try:
        # Check if LLM provider is available
        try:
            llm_provider = LLMProviderFactory.create_llm()
            llm_available = llm_provider is not None
            llm_status = "connected" if llm_available else "not_configured"
        except Exception:
            llm_available = False
            llm_status = "error"
        
        capabilities = [
            "financial_advice",
            "spending_analysis", 
            "anomaly_detection",
            "quick_insights"
        ]
        
        if llm_available:
            capabilities.extend([
                "ai_chat",
                "advanced_analysis",
                "predictions"
            ])
        
        return {
            'status': 'healthy',
            'llm_available': llm_available,
            'llm_status': llm_status,
            'capabilities': capabilities,
            'fallback_mode': not llm_available
        }
        
    except Exception as e:
        logger.error(f"Error checking AI health: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'llm_available': False,
            'capabilities': ['basic_analysis']
        }