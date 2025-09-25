"""Expense controller for API endpoints."""

import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from services.supabase_service import get_supabase_client
from services.auth_middleware import get_current_user
from .repository import ExpenseRepository
from .service import ExpenseService
from .schemas import (
    CategorySummaryResponse,
    ExpenseFilters,
    ExpensePeriod,
    ExpenseSummaryResponse,
    ExpenseTrendResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expenses", tags=["expenses"])


def get_expense_service(
    supabase_client: Client = Depends(get_supabase_client)
) -> ExpenseService:
    """Dependency to get expense service."""
    repository = ExpenseRepository(supabase_client)
    return ExpenseService(repository)


@router.get("/summary", response_model=ExpenseSummaryResponse)
async def get_expense_summary(
    period: ExpensePeriod = Query(ExpensePeriod.MONTHLY, description="Time period for summary"),
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    categories: Optional[List[str]] = Query(None, description="Filter by categories"),
    min_amount: Optional[float] = Query(None, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, description="Maximum transaction amount"),
    current_user: dict = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service)
):
    """Get comprehensive expense summary with category breakdown."""
    try:
        filters = ExpenseFilters(
            start_date=start_date,
            end_date=end_date,
            categories=categories,
            min_amount=min_amount,
            max_amount=max_amount,
            period=period
        )
        
        return await service.get_expense_summary(current_user["user_id"], filters)
        
    except Exception as e:
        logger.error(f"Error getting expense summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get expense summary")


@router.get("/trends", response_model=List[ExpenseTrendResponse])
async def get_expense_trends(
    period: ExpensePeriod = Query(ExpensePeriod.MONTHLY, description="Time period for trends"),
    months_back: int = Query(12, description="Number of months to look back"),
    current_user: dict = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service)
):
    """Get expense trends over time."""
    try:
        if months_back < 1 or months_back > 60:
            raise HTTPException(status_code=400, detail="months_back must be between 1 and 60")
        
        return await service.get_expense_trends(current_user["user_id"], period, months_back)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting expense trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get expense trends")


@router.get("/categories/top", response_model=List[CategorySummaryResponse])
async def get_top_categories(
    limit: int = Query(10, description="Number of top categories to return"),
    period: ExpensePeriod = Query(ExpensePeriod.MONTHLY, description="Time period for analysis"),
    current_user: dict = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service)
):
    """Get top expense categories by amount."""
    try:
        if limit < 1 or limit > 50:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 50")
        
        return await service.get_top_expense_categories(current_user["user_id"], limit, period)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting top categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get top categories")


@router.get("/comparison/monthly")
async def get_monthly_comparison(
    month: Optional[date] = Query(None, description="Month to compare (defaults to current)"),
    current_user: dict = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service)
):
    """Compare current month expenses to previous month."""
    try:
        current_month = month or date.today().replace(day=1)
        return await service.get_monthly_comparison(current_user["user_id"], current_month)
        
    except Exception as e:
        logger.error(f"Error getting monthly comparison: {e}")
        raise HTTPException(status_code=500, detail="Failed to get monthly comparison")


@router.get("/categories", response_model=List[str])
async def get_expense_categories(
    current_user: dict = Depends(get_current_user),
    service: ExpenseService = Depends(get_expense_service)
):
    """Get list of all expense categories used by the user."""
    try:
        # Get all categories from top categories with no limit
        categories_data = await service.get_top_expense_categories(
            current_user["user_id"], 
            limit=1000,  # Large limit to get all categories
            period=ExpensePeriod.YEARLY
        )
        
        return [cat.category for cat in categories_data]
        
    except Exception as e:
        logger.error(f"Error getting expense categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get expense categories")