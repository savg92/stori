"""Timeline controller for API endpoints."""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from services.supabase_service import get_supabase_client
from services.auth_middleware import get_current_user
from .repository import TimelineRepository
from .service import TimelineService
from .schemas import (
    CashFlowResponse,
    CategoryTimelineResponse,
    TimelineFilters,
    TimelineGrouping,
    TimelineResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/timeline", tags=["timeline"])


def get_timeline_service(
    supabase_client: Client = Depends(get_supabase_client)
) -> TimelineService:
    """Dependency to get timeline service."""
    repository = TimelineRepository(supabase_client)
    return TimelineService(repository)


@router.get("", response_model=TimelineResponse)
async def get_timeline(
    grouping: TimelineGrouping = Query(TimelineGrouping.MONTHLY, description="Time period grouping"),
    start_date: Optional[date] = Query(None, description="Start date for timeline"),
    end_date: Optional[date] = Query(None, description="End date for timeline"),
    categories: Optional[List[str]] = Query(None, description="Filter by categories"),
    include_income: bool = Query(True, description="Include income transactions"),
    include_expenses: bool = Query(True, description="Include expense transactions"),
    min_amount: Optional[float] = Query(None, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, description="Maximum transaction amount"),
    current_user: dict = Depends(get_current_user),
    service: TimelineService = Depends(get_timeline_service)
):
    """Get timeline data with specified grouping and filters."""
    try:
        filters = TimelineFilters(
            start_date=start_date,
            end_date=end_date,
            grouping=grouping,
            categories=categories,
            include_income=include_income,
            include_expenses=include_expenses,
            min_amount=Decimal(str(min_amount)) if min_amount else None,
            max_amount=Decimal(str(max_amount)) if max_amount else None
        )
        
        return await service.get_timeline(current_user["user_id"], filters)
        
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to get timeline data")


@router.get("/category/{category}", response_model=CategoryTimelineResponse)
async def get_category_timeline(
    category: str,
    grouping: TimelineGrouping = Query(TimelineGrouping.MONTHLY, description="Time period grouping"),
    months_back: int = Query(12, description="Number of months to look back"),
    current_user: dict = Depends(get_current_user),
    service: TimelineService = Depends(get_timeline_service)
):
    """Get timeline data for a specific category."""
    try:
        if months_back < 1 or months_back > 60:
            raise HTTPException(status_code=400, detail="months_back must be between 1 and 60")
        
        return await service.get_category_timeline(
            current_user["user_id"], 
            category, 
            grouping, 
            months_back
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category timeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to get category timeline")


@router.get("/cash-flow", response_model=CashFlowResponse)
async def get_cash_flow(
    grouping: TimelineGrouping = Query(TimelineGrouping.MONTHLY, description="Time period grouping"),
    months_back: int = Query(12, description="Number of months to look back"),
    starting_balance: float = Query(0.0, description="Starting balance for cash flow analysis"),
    current_user: dict = Depends(get_current_user),
    service: TimelineService = Depends(get_timeline_service)
):
    """Get cash flow analysis with running balance."""
    try:
        if months_back < 1 or months_back > 60:
            raise HTTPException(status_code=400, detail="months_back must be between 1 and 60")
        
        return await service.get_cash_flow(
            current_user["user_id"], 
            grouping, 
            months_back, 
            Decimal(str(starting_balance))
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cash flow: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cash flow data")


@router.get("/velocity")
async def get_spending_velocity(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: dict = Depends(get_current_user),
    service: TimelineService = Depends(get_timeline_service)
):
    """Get spending velocity metrics."""
    try:
        if days < 7 or days > 365:
            raise HTTPException(status_code=400, detail="days must be between 7 and 365")
        
        return await service.get_spending_velocity(current_user["user_id"], days)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting spending velocity: {e}")
        raise HTTPException(status_code=500, detail="Failed to get spending velocity")


@router.get("/summary")
async def get_timeline_summary(
    grouping: TimelineGrouping = Query(TimelineGrouping.MONTHLY, description="Time period grouping"),
    periods: int = Query(6, description="Number of recent periods to summarize"),
    current_user: dict = Depends(get_current_user),
    service: TimelineService = Depends(get_timeline_service)
):
    """Get summary of recent timeline periods."""
    try:
        if periods < 1 or periods > 24:
            raise HTTPException(status_code=400, detail="periods must be between 1 and 24")
        
        # Calculate appropriate date range based on grouping and periods
        end_date = date.today()
        if grouping == TimelineGrouping.DAILY:
            start_date = end_date - timedelta(days=periods)
        elif grouping == TimelineGrouping.WEEKLY:
            start_date = end_date - timedelta(weeks=periods)
        elif grouping == TimelineGrouping.MONTHLY:
            months_back = periods
            start_date = end_date - timedelta(days=months_back * 30)
        else:  # YEARLY
            start_date = end_date - timedelta(days=periods * 365)
        
        filters = TimelineFilters(
            start_date=start_date,
            end_date=end_date,
            grouping=grouping
        )
        
        timeline = await service.get_timeline(current_user["user_id"], filters)
        
        # Return simplified summary
        return {
            'periods_analyzed': len(timeline.data_points),
            'date_range': timeline.date_range,
            'summary_stats': timeline.summary_stats,
            'latest_period': timeline.data_points[-1] if timeline.data_points else None,
            'best_period': max(timeline.data_points, key=lambda x: x.net_amount) if timeline.data_points else None,
            'worst_period': min(timeline.data_points, key=lambda x: x.net_amount) if timeline.data_points else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting timeline summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get timeline summary")