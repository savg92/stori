"""Timeline service layer for business logic."""

import logging
from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, Any

from .repository import TimelineRepository
from .schemas import (
    CashFlowPoint,
    CashFlowResponse,
    CategoryTimelinePoint,
    CategoryTimelineResponse,
    TimelineDataPoint,
    TimelineFilters,
    TimelineGrouping,
    TimelineResponse
)

logger = logging.getLogger(__name__)


class TimelineService:
    """Service layer for timeline operations."""
    
    def __init__(self, repository: TimelineRepository):
        self.repository = repository

    async def get_timeline(
        self, 
        user_id: str, 
        filters: TimelineFilters
    ) -> TimelineResponse:
        """Get comprehensive timeline data."""
        try:
            # Set default date range if not provided
            if not filters.start_date or not filters.end_date:
                end_date = date.today()
                if filters.grouping == TimelineGrouping.DAILY:
                    start_date = end_date - timedelta(days=30)  # Last 30 days
                elif filters.grouping == TimelineGrouping.WEEKLY:
                    start_date = end_date - timedelta(weeks=12)  # Last 12 weeks
                elif filters.grouping == TimelineGrouping.MONTHLY:
                    start_date = end_date - timedelta(days=365)  # Last year
                else:  # YEARLY
                    start_date = end_date - timedelta(days=365 * 5)  # Last 5 years
                
                filters.start_date = filters.start_date or start_date
                filters.end_date = filters.end_date or end_date

            timeline_data = await self.repository.get_timeline_data(user_id, filters)
            
            # Convert to response format
            data_points = []
            total_income = Decimal('0')
            total_expenses = Decimal('0')
            total_transactions = 0
            
            for period in timeline_data:
                data_point = TimelineDataPoint(
                    date=period['date'],
                    total_income=period['total_income'],
                    total_expenses=period['total_expenses'],
                    net_amount=period['net_amount'],
                    transaction_count=period['transaction_count'],
                    largest_expense=period.get('largest_expense'),
                    largest_income=period.get('largest_income')
                )
                data_points.append(data_point)
                
                total_income += period['total_income']
                total_expenses += period['total_expenses']
                total_transactions += period['transaction_count']
            
            # Sort by date
            data_points.sort(key=lambda x: x.date)
            
            # Calculate summary statistics
            avg_income = total_income / len(data_points) if data_points else Decimal('0')
            avg_expenses = total_expenses / len(data_points) if data_points else Decimal('0')
            net_total = total_income - total_expenses
            
            summary_stats = {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_amount': net_total,
                'avg_income_per_period': avg_income,
                'avg_expenses_per_period': avg_expenses,
                'total_transactions': Decimal(str(total_transactions))
            }
            
            return TimelineResponse(
                grouping=filters.grouping,
                data_points=data_points,
                date_range={
                    'start_date': filters.start_date,
                    'end_date': filters.end_date
                },
                total_periods=len(data_points),
                summary_stats=summary_stats
            )
            
        except Exception as e:
            logger.error(f"Error in timeline service: {e}")
            raise

    async def get_category_timeline(
        self, 
        user_id: str,
        category: str,
        grouping: TimelineGrouping = TimelineGrouping.MONTHLY,
        months_back: int = 12
    ) -> CategoryTimelineResponse:
        """Get timeline for a specific category."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=months_back * 30)  # Approximate
            
            category_data = await self.repository.get_category_timeline(
                user_id, category, grouping, start_date, end_date
            )
            
            # Convert to response format
            data_points = []
            total_amount = Decimal('0')
            
            for period in category_data:
                data_point = CategoryTimelinePoint(
                    date=period['date'],
                    category=period['category'],
                    amount=period['amount'],
                    transaction_count=period['transaction_count'],
                    avg_amount=period['avg_amount']
                )
                data_points.append(data_point)
                total_amount += period['amount']
            
            # Sort by date
            data_points.sort(key=lambda x: x.date)
            
            # Calculate average per period
            avg_per_period = total_amount / len(data_points) if data_points else Decimal('0')
            
            return CategoryTimelineResponse(
                category=category,
                grouping=grouping,
                data_points=data_points,
                date_range={
                    'start_date': start_date,
                    'end_date': end_date
                },
                total_amount=total_amount,
                avg_per_period=avg_per_period
            )
            
        except Exception as e:
            logger.error(f"Error in category timeline service: {e}")
            raise

    async def get_cash_flow(
        self, 
        user_id: str,
        grouping: TimelineGrouping = TimelineGrouping.MONTHLY,
        months_back: int = 12,
        starting_balance: Decimal = Decimal('0')
    ) -> CashFlowResponse:
        """Get cash flow analysis with running balance."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=months_back * 30)  # Approximate
            
            cash_flow_data = await self.repository.get_cash_flow_data(
                user_id, grouping, start_date, end_date, starting_balance
            )
            
            # Convert to response format
            cash_flow_points = []
            total_income = Decimal('0')
            total_expenses = Decimal('0')
            
            for period in cash_flow_data:
                cash_flow_point = CashFlowPoint(
                    date=period['date'],
                    opening_balance=period['opening_balance'],
                    total_income=period['total_income'],
                    total_expenses=period['total_expenses'],
                    closing_balance=period['closing_balance'],
                    net_change=period['net_change']
                )
                cash_flow_points.append(cash_flow_point)
                
                total_income += period['total_income']
                total_expenses += period['total_expenses']
            
            # Sort by date
            cash_flow_points.sort(key=lambda x: x.date)
            
            ending_balance = cash_flow_points[-1].closing_balance if cash_flow_points else starting_balance
            net_cash_flow = total_income - total_expenses
            
            return CashFlowResponse(
                grouping=grouping,
                cash_flow_points=cash_flow_points,
                date_range={
                    'start_date': start_date,
                    'end_date': end_date
                },
                starting_balance=starting_balance,
                ending_balance=ending_balance,
                total_income=total_income,
                total_expenses=total_expenses,
                net_cash_flow=net_cash_flow
            )
            
        except Exception as e:
            logger.error(f"Error in cash flow service: {e}")
            raise
