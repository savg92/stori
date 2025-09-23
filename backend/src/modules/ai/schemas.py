"""AI-related Pydantic schemas for request/response validation."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator


class AdviceType(str, Enum):
    """Types of AI financial advice."""
    SPENDING_INSIGHTS = "spending_insights"
    BUDGET_RECOMMENDATIONS = "budget_recommendations" 
    SAVINGS_OPPORTUNITIES = "savings_opportunities"
    CATEGORY_ANALYSIS = "category_analysis"
    TREND_ANALYSIS = "trend_analysis"
    GOAL_SETTING = "goal_setting"


class AdvicePriority(str, Enum):
    """Priority levels for AI advice."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AdviceRequest(BaseModel):
    """Request model for AI financial advice."""
    model_config = ConfigDict(from_attributes=True)
    
    advice_type: AdviceType
    context: Optional[str] = None
    include_data_analysis: bool = True
    specific_categories: Optional[List[str]] = None
    time_period_days: int = 30

    @field_validator('time_period_days')
    @classmethod
    def validate_time_period(cls, v):
        """Validate time period is reasonable."""
        if v < 1 or v > 365:
            raise ValueError("time_period_days must be between 1 and 365")
        return v


class AdviceInsight(BaseModel):
    """Individual insight within AI advice."""
    model_config = ConfigDict(from_attributes=True)
    
    title: str
    description: str
    priority: AdvicePriority
    category: Optional[str] = None
    amount_impact: Optional[Decimal] = None
    confidence_score: float
    actionable_steps: List[str]


class AIAdviceResponse(BaseModel):
    """Response model for AI financial advice."""
    model_config = ConfigDict(from_attributes=True)
    
    advice_type: AdviceType
    generated_at: datetime
    insights: List[AdviceInsight]
    summary: str
    data_analysis: Dict[str, Union[str, float, Decimal]]
    recommendations: List[str]
    confidence_score: float


class ChatMessage(BaseModel):
    """Chat message model."""
    model_config = ConfigDict(from_attributes=True)
    
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime


class ChatRequest(BaseModel):
    """Request model for AI chat."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str
    conversation_history: Optional[List[ChatMessage]] = None
    include_financial_context: bool = True
    max_context_days: int = 30

    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        """Validate message is not empty."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for AI chat."""
    model_config = ConfigDict(from_attributes=True)
    
    message: str
    conversation_id: Optional[str] = None
    suggested_actions: Optional[List[str]] = None
    financial_insights: Optional[List[str]] = None
    confidence_score: float


class FinancialContext(BaseModel):
    """Financial context for AI analysis."""
    model_config = ConfigDict(from_attributes=True)
    
    total_income: Decimal
    total_expenses: Decimal
    net_amount: Decimal
    top_categories: List[Dict[str, Union[str, Decimal, int]]]
    recent_trends: List[Dict[str, Union[str, Decimal]]]
    transaction_count: int
    date_range: Dict[str, str]


class AnalysisRequest(BaseModel):
    """Request for financial data analysis."""
    model_config = ConfigDict(from_attributes=True)
    
    analysis_type: str
    parameters: Optional[Dict[str, Union[str, int, float]]] = None
    include_predictions: bool = False
    context_days: int = 90

    @field_validator('analysis_type')
    @classmethod
    def validate_analysis_type(cls, v):
        """Validate analysis type."""
        valid_types = [
            'spending_patterns',
            'category_breakdown',
            'trend_analysis',
            'anomaly_detection',
            'budget_variance',
            'cash_flow_forecast'
        ]
        if v not in valid_types:
            raise ValueError(f"analysis_type must be one of: {valid_types}")
        return v


class AnalysisResult(BaseModel):
    """Result of financial data analysis."""
    model_config = ConfigDict(from_attributes=True)
    
    analysis_type: str
    results: Dict[str, Union[str, float, Decimal, List]]
    insights: List[str]
    visualizations: Optional[List[Dict[str, Union[str, List]]]] = None
    confidence_score: float
    generated_at: datetime