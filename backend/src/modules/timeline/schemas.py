"""Timeline-related Pydantic schemas for request/response validation."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, field_validator, field_serializer


class TimelineGrouping(str, Enum):
    """Grouping options for timeline data."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class TimelineDataPoint(BaseModel):
    """Individual data point in timeline."""
    model_config = ConfigDict(from_attributes=True)
    
    date: date
    total_income: Decimal
    total_expenses: Decimal
    net_amount: Decimal
    transaction_count: int
    largest_expense: Optional[Decimal] = None
    largest_income: Optional[Decimal] = None

    @field_serializer('total_income', 'total_expenses', 'net_amount', 'largest_expense', 'largest_income')
    def serialize_decimal(self, value: Optional[Decimal]) -> Optional[float]:
        """Convert Decimal to float for JSON serialization."""
        return float(value) if value is not None else None


class CategoryTimelinePoint(BaseModel):
    """Timeline point with category breakdown."""
    model_config = ConfigDict(from_attributes=True)
    
    date: date
    category: str
    amount: Decimal
    transaction_count: int
    avg_amount: Decimal

    @field_serializer('amount', 'avg_amount')
    def serialize_decimal(self, value: Decimal) -> float:
        """Convert Decimal to float for JSON serialization."""
        return float(value)


class TimelineResponse(BaseModel):
    """Response model for timeline data."""
    model_config = ConfigDict(from_attributes=True)
    
    grouping: TimelineGrouping
    data_points: List[TimelineDataPoint]
    date_range: Dict[str, date]
    total_periods: int
    summary_stats: Dict[str, Decimal]


class CategoryTimelineResponse(BaseModel):
    """Response model for category-specific timeline."""
    model_config = ConfigDict(from_attributes=True)
    
    category: str
    grouping: TimelineGrouping
    data_points: List[CategoryTimelinePoint]
    date_range: Dict[str, date]
    total_amount: Decimal
    avg_per_period: Decimal


class TimelineFilters(BaseModel):
    """Filters for timeline queries."""
    model_config = ConfigDict(from_attributes=True)
    
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    grouping: TimelineGrouping = TimelineGrouping.MONTHLY
    categories: Optional[List[str]] = None
    include_income: bool = True
    include_expenses: bool = True
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None

    @field_validator('categories')
    @classmethod
    def validate_categories(cls, v):
        """Validate categories list."""
        if v is not None and len(v) == 0:
            return None
        return v


class CashFlowPoint(BaseModel):
    """Cash flow data point."""
    model_config = ConfigDict(from_attributes=True)
    
    date: date
    opening_balance: Decimal
    total_income: Decimal
    total_expenses: Decimal
    closing_balance: Decimal
    net_change: Decimal


class CashFlowResponse(BaseModel):
    """Response model for cash flow analysis."""
    model_config = ConfigDict(from_attributes=True)
    
    grouping: TimelineGrouping
    cash_flow_points: List[CashFlowPoint]
    date_range: Dict[str, date]
    starting_balance: Decimal
    ending_balance: Decimal
    total_income: Decimal
    total_expenses: Decimal
    net_cash_flow: Decimal