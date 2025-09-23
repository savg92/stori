"""API routes for the Stori expense tracker application."""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, date

from core.models import (
    AskRequest,
    AskResponse,
    RebuildStoreRequest,
    LLMUpdateRequest,
    LLMConfigResponse,
    EmbeddingUpdateRequest,
    EmbeddingConfigResponse,
)
from services import AIAdvisorService
from providers.llms import LLMProviderFactory


router = APIRouter()

# TODO: Replace with proper database service
# Temporary in-memory storage for development
transactions_db: List[Transaction] = []


@router.get("/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "stori-expense-tracker"
    }


@router.get("/llm", response_model=LLMConfigResponse)
def get_current_llm(handler: APIHandlerService = Depends(get_api_handler)) -> LLMConfigResponse:
    """Get current LLM configuration snapshot (sanitized)."""
    return handler.get_current_llm()


@router.post("/llm", response_model=LLMConfigResponse)
def update_llm(
    request: LLMUpdateRequest,
    handler: APIHandlerService = Depends(get_api_handler)
) -> LLMConfigResponse:
    """Update/switch the LLM provider at runtime and refresh the QA chain."""
    return handler.update_llm(request)




@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(
    start_date: date = None,
    end_date: date = None,
    group_by: str = "day"
) -> TimelineResponse:
    """Get transaction timeline data for charts."""
    # TODO: Replace with database aggregation
    filtered_transactions = transactions_db[:]
    
    if start_date:
        filtered_transactions = [t for t in filtered_transactions if t.date >= start_date]
    if end_date:
        filtered_transactions = [t for t in filtered_transactions if t.date <= end_date]
    
    # Simple daily grouping for now
    daily_data = {}
    for transaction in filtered_transactions:
        date_key = transaction.date.isoformat()
        if date_key not in daily_data:
            daily_data[date_key] = {"income": 0, "expenses": 0}
        
        if transaction.type == "income":
            daily_data[date_key]["income"] += transaction.amount
        else:
            daily_data[date_key]["expenses"] += transaction.amount
    
    return TimelineResponse(
        period_start=start_date,
        period_end=end_date,
        group_by=group_by,
        data=daily_data
    )


@router.post("/ai/advice", response_model=AIAdviceResponse)
async def get_ai_advice(request: AIAdviceRequest) -> AIAdviceResponse:
    """Get AI-powered financial advice based on user transactions."""
    try:
        # Initialize AI components
        llm = LLMProviderFactory.create_llm("openai")
        advisor_service = AIAdvisorService()
        llm_chain = advisor_service.create_advisor_chain(llm)
        
        # Get recent transactions for context
        # TODO: Replace with database query filtered by user
        recent_transactions = transactions_db[-30:]  # Last 30 transactions
        
        # Generate advice
        advice_response = advisor_service.get_financial_advice(
            llm_chain=llm_chain,
            request=request,
            transactions=recent_transactions,
            chat_history=[]  # TODO: Implement chat history storage
        )
        
        return advice_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating financial advice: {str(e)}"
        )
