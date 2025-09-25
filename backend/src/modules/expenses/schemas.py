"""Expense-related Pydantic schemas for request/response validation."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator, field_serializer


class ExpensePeriod(str, Enum):
    """Time periods for expense analysis."""
    DAILY = "daily"
    WEEKLY = "weekly" 
    MONTHLY = "monthly"
    YEARLY = "yearly"


class CategorySummaryResponse(BaseModel):
    """Response model for category-based expense summary."""
    model_config = ConfigDict(from_attributes=True)
    
    category: str
    total_amount: Decimal
    transaction_count: int
    percentage_of_total: float
    avg_amount: Decimal

    @field_serializer('total_amount', 'avg_amount')
    def serialize_decimal(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class ExpenseSummaryResponse(BaseModel):
    """Response model for comprehensive expense summary."""
    model_config = ConfigDict(from_attributes=True)
    
    period: ExpensePeriod
    total_expenses: Decimal
    total_income: Decimal
    net_amount: Decimal
    category_breakdown: List[CategorySummaryResponse]
    transaction_count: int
    date_range: Dict[str, date]

    @field_serializer('total_expenses', 'total_income', 'net_amount')
    def serialize_decimal(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class ExpenseTrendResponse(BaseModel):
    """Response model for expense trends over time."""
    model_config = ConfigDict(from_attributes=True)
    
    date: date
    total_amount: Decimal
    category_amounts: Dict[str, Decimal]
    transaction_count: int

    @field_serializer('total_amount')
    def serialize_decimal(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)
        
    @field_serializer('category_amounts')
    def serialize_category_amounts(self, value: Dict[str, Decimal]) -> Dict[str, float]:
        """Convert Decimal values in dict to float for JSON serialization."""
        return {k: float(v) for k, v in value.items()}


class BudgetComparisonResponse(BaseModel):
    """Response model for budget vs actual comparison."""
    model_config = ConfigDict(from_attributes=True)
    
    category: str
    budgeted_amount: Optional[Decimal]
    actual_amount: Decimal
    variance: Decimal
    variance_percentage: Optional[float]
    is_over_budget: bool


class ExpenseFilters(BaseModel):
    """Filters for expense queries."""
    model_config = ConfigDict(from_attributes=True)
    
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    categories: Optional[List[str]] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    period: ExpensePeriod = ExpensePeriod.MONTHLY

    @field_validator('categories')
    @classmethod
    def validate_categories(cls, v):
        """Validate categories list."""
        if v is not None and len(v) == 0:
            return None
        return v