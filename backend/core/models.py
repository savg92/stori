"""Core data models for the Stori Expense Tracker application."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator, field_serializer


class TransactionType(str, Enum):
    """Transaction type enumeration."""
    INCOME = "income"
    EXPENSE = "expense"


class ExpenseCategory(str, Enum):
    """Expense category enumeration."""
    RENT = "rent"
    GROCERIES = "groceries"
    UTILITIES = "utilities"
    DINING = "dining"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    TRAVEL = "travel"
    OTHER = "other"


class IncomeCategory(str, Enum):
    """Income category enumeration."""
    SALARY = "salary"
    FREELANCE = "freelance"
    INVESTMENT = "investment"
    GIFT = "gift"
    OTHER = "other"


# Transaction Models
class TransactionBase(BaseModel):
    """Base transaction model with common fields."""
    amount: Decimal = Field(..., description="Transaction amount (negative for expenses, positive for income)")
    description: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., description="Transaction category")
    type: TransactionType = Field(..., description="Transaction type: income or expense")
    transaction_date: date = Field(..., description="Transaction date", alias="date")
    
    @validator('category')
    def validate_category(cls, v, values):
        """Validate category based on transaction type."""
        if 'type' in values:
            if values['type'] == TransactionType.EXPENSE:
                if v not in [cat.value for cat in ExpenseCategory]:
                    raise ValueError(f"Invalid expense category: {v}")
            elif values['type'] == TransactionType.INCOME:
                if v not in [cat.value for cat in IncomeCategory]:
                    raise ValueError(f"Invalid income category: {v}")
        return v
    
    @validator('amount')
    def validate_amount_sign(cls, v, values):
        """Validate amount sign matches transaction type."""
        if 'type' in values:
            if values['type'] == TransactionType.EXPENSE and v > 0:
                raise ValueError("Expense amounts should be negative")
            elif values['type'] == TransactionType.INCOME and v < 0:
                raise ValueError("Income amounts should be positive")
        return v

    @field_serializer('amount')
    def serialize_decimal(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class TransactionCreate(TransactionBase):
    """Model for creating a new transaction."""
    pass


class TransactionUpdate(BaseModel):
    """Model for updating an existing transaction."""
    amount: Optional[Decimal] = Field(None, description="Transaction amount")
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, description="Transaction category")
    type: Optional[TransactionType] = Field(None, description="Transaction type")
    transaction_date: Optional[date] = Field(None, description="Transaction date", alias="date")

    @field_serializer('amount')
    def serialize_decimal(self, value: Optional[Decimal]) -> Optional[float]:
        """Convert Decimal to float for JSON serialization."""
        return float(value) if value is not None else None


class Transaction(TransactionBase):
    """Full transaction model with database fields."""
    id: str = Field(..., description="Transaction unique identifier")
    user_id: str = Field(..., description="User who owns this transaction")
    created_at: datetime = Field(..., description="Transaction creation timestamp")
    updated_at: datetime = Field(..., description="Transaction last update timestamp")
    
    class Config:
        from_attributes = True


# Expense Summary Models
class CategorySummary(BaseModel):
    """Summary for a specific category."""
    category: str
    total_amount: Decimal
    percentage: float = Field(..., ge=0, le=100)
    transaction_count: int = Field(..., ge=0)

    @field_serializer('total_amount')
    def serialize_decimal(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class ExpenseSummaryResponse(BaseModel):
    """Response model for expense summary."""
    total_expenses: Decimal
    total_income: Decimal
    net_income: Decimal
    expense_categories: List[CategorySummary]
    income_categories: List[CategorySummary]
    period_start: date
    period_end: date

    @field_serializer('total_expenses', 'total_income', 'net_income')
    def serialize_decimal(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


# Timeline Models
class TimelineEntry(BaseModel):
    """Single entry in the timeline chart."""
    entry_date: date
    total_income: Decimal
    total_expenses: Decimal
    net_amount: Decimal
    transaction_count: int

    @field_serializer('total_income', 'total_expenses', 'net_amount')
    def serialize_decimal(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class TimelineResponse(BaseModel):
    """Response model for timeline data."""
    timeline_data: List[TimelineEntry]
    period_start: date
    period_end: date
    total_income: Decimal
    total_expenses: Decimal
    average_monthly_income: Decimal
    average_monthly_expenses: Decimal

    @field_serializer('total_income', 'total_expenses', 'average_monthly_income', 'average_monthly_expenses')
    def serialize_decimal(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


# AI Advisor Models
class AIAdviceRequest(BaseModel):
    """Request model for AI financial advice."""
    question: str = Field(..., min_length=1, max_length=500)
    context_period_days: int = Field(default=30, ge=7, le=365)


class AIAdviceResponse(BaseModel):
    """Response model for AI financial advice."""
    advice: str
    insights: List[str]
    recommendations: List[str]
    financial_score: Optional[float] = Field(None, ge=0, le=100)


# User Models
class UserProfile(BaseModel):
    """User profile information."""
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


# Query Models
class DateRangeQuery(BaseModel):
    """Model for date range queries."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate that end_date is after start_date."""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError("end_date must be after start_date")
        return v


class TransactionQuery(DateRangeQuery):
    """Query model for filtering transactions."""
    transaction_type: Optional[TransactionType] = None
    category: Optional[str] = None
    min_amount: Optional[Decimal] = Field(None, gt=0)
    max_amount: Optional[Decimal] = Field(None, gt=0)
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# Response Models
class TransactionListResponse(BaseModel):
    """Response model for transaction lists."""
    items: List[Transaction]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# LLM Configuration Models
class LLMConfigResponse(BaseModel):
    """Response model for LLM configuration."""
    provider: str
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    is_active: bool = True
    capabilities: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = None


class LLMUpdateRequest(BaseModel):
    """Request model for updating LLM configuration."""
    provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=100000)
    api_key: Optional[str] = None
    
    @validator('provider')
    def validate_provider(cls, v):
        """Validate LLM provider."""
        if v:
            valid_providers = [
                'openai', 'ollama', 'azure', 'bedrock', 
                'lmstudio', 'openrouter'
            ]
            if v.lower() not in valid_providers:
                raise ValueError(f"Provider must be one of: {valid_providers}")
        return v