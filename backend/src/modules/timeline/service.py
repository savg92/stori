"""Timeline service layer for business logic."""

import logging
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import List

from .repository import TimelineRepository
from services.mock_data_service import MockDataService
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
        self.mock_service = MockDataService()
    
    async def get_timeline(
        self, 
        user_id: str, 
        filters: TimelineFilters
    ) -> TimelineResponse:
        """Get comprehensive timeline data."""
        try:
            # Check if this is a mock user
            if self.mock_service.is_mock_user(user_id):
                return self._get_mock_timeline(user_id, filters)
            
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
            # Check if this is a mock user
            if self.mock_service.is_mock_user(user_id):
                return self._get_mock_category_timeline(user_id, category, grouping, months_back)
            
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
            # Check if this is a mock user
            if self.mock_service.is_mock_user(user_id):
                return self._get_mock_cash_flow(user_id, grouping, months_back, starting_balance)
            
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
    
    async def get_spending_velocity(
        self, 
        user_id: str,
        days: int = 30
    ) -> dict:
        """Get spending velocity metrics."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            filters = TimelineFilters(
                start_date=start_date,
                end_date=end_date,
                grouping=TimelineGrouping.DAILY,
                include_income=False,
                include_expenses=True
            )
            
            timeline = await self.get_timeline(user_id, filters)
            
            if not timeline.data_points:
                return {
                    'daily_avg': Decimal('0'),
                    'velocity_trend': 'stable',
                    'days_analyzed': days,
                    'total_spent': Decimal('0')
                }
            
            # Calculate daily average
            total_spent = sum(point.total_expenses for point in timeline.data_points)
            daily_avg = total_spent / len(timeline.data_points)
            
            # Analyze trend (simple comparison of first half vs second half)
            mid_point = len(timeline.data_points) // 2
            first_half_avg = (
                sum(point.total_expenses for point in timeline.data_points[:mid_point]) / mid_point
                if mid_point > 0 else Decimal('0')
            )
            second_half_avg = (
                sum(point.total_expenses for point in timeline.data_points[mid_point:]) / 
                (len(timeline.data_points) - mid_point)
                if (len(timeline.data_points) - mid_point) > 0 else Decimal('0')
            )
            
            # Determine trend
            if second_half_avg > first_half_avg * Decimal('1.1'):  # 10% increase
                velocity_trend = 'increasing'
            elif second_half_avg < first_half_avg * Decimal('0.9'):  # 10% decrease
                velocity_trend = 'decreasing'
            else:
                velocity_trend = 'stable'
            
            return {
                'daily_avg': daily_avg,
                'velocity_trend': velocity_trend,
                'days_analyzed': len(timeline.data_points),
                'total_spent': total_spent,
                'first_half_avg': first_half_avg,
                'second_half_avg': second_half_avg
            }
            
        except Exception as e:
            logger.error(f"Error in spending velocity service: {e}")
            raise
    
    def _get_mock_timeline(self, user_id: str, filters: TimelineFilters) -> TimelineResponse:
        """Get timeline data from mock data."""
        # Get all mock transactions
        all_transactions = self.mock_service.get_mock_transactions(user_id)
        
        # Set defaults if not provided
        if not filters.start_date or not filters.end_date:
            end_date = date.today()
            if filters.grouping == TimelineGrouping.DAILY:
                start_date = end_date - timedelta(days=30)
            elif filters.grouping == TimelineGrouping.WEEKLY:
                start_date = end_date - timedelta(weeks=12)
            elif filters.grouping == TimelineGrouping.MONTHLY:
                start_date = end_date - timedelta(days=365)
            else:  # YEARLY
                start_date = end_date - timedelta(days=365 * 5)
            
            filters.start_date = filters.start_date or start_date
            filters.end_date = filters.end_date or end_date
        
        # Filter transactions by date range
        filtered_transactions = [
            tx for tx in all_transactions
            if filters.start_date <= tx.transaction_date <= filters.end_date
        ]
        
        # Group by period
        period_groups = defaultdict(list)
        
        for tx in filtered_transactions:
            if filters.grouping == TimelineGrouping.DAILY:
                period_key = tx.transaction_date
            elif filters.grouping == TimelineGrouping.WEEKLY:
                # Get Monday of the week
                period_key = tx.transaction_date - timedelta(days=tx.transaction_date.weekday())
            elif filters.grouping == TimelineGrouping.MONTHLY:
                period_key = tx.transaction_date.replace(day=1)
            else:  # YEARLY
                period_key = tx.transaction_date.replace(month=1, day=1)
            
            period_groups[period_key].append(tx)
        
        # Create data points
        data_points = []
        total_income = Decimal('0')
        total_expenses = Decimal('0')
        total_transactions = 0
        
        for period_date, transactions in period_groups.items():
            income_txs = [tx for tx in transactions if tx.type == "income"]
            expense_txs = [tx for tx in transactions if tx.type == "expense"]
            
            period_income = sum(tx.amount for tx in income_txs)
            period_expenses = sum(abs(tx.amount) for tx in expense_txs)  # abs for display
            
            data_point = TimelineDataPoint(
                date=period_date,
                total_income=period_income,
                total_expenses=period_expenses,
                net_amount=period_income - period_expenses,
                transaction_count=len(transactions),
                largest_expense=max((abs(tx.amount) for tx in expense_txs), default=Decimal('0')),
                largest_income=max((tx.amount for tx in income_txs), default=Decimal('0'))
            )
            data_points.append(data_point)
            
            total_income += period_income
            total_expenses += period_expenses
            total_transactions += len(transactions)
        
        # Sort by date
        data_points.sort(key=lambda x: x.date)
        
        # Calculate summary stats
        avg_income = total_income / len(data_points) if data_points else Decimal('0')
        avg_expenses = total_expenses / len(data_points) if data_points else Decimal('0')
        
        summary_stats = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_amount': total_income - total_expenses,
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
    
    def _get_mock_category_timeline(
        self, 
        user_id: str, 
        category: str, 
        grouping: TimelineGrouping, 
        months_back: int
    ) -> CategoryTimelineResponse:
        """Get category timeline from mock data."""
        # Get all mock transactions for the user
        all_transactions = self.mock_service.get_mock_transactions(user_id)
        
        # Date range
        end_date = date.today()
        start_date = end_date - timedelta(days=months_back * 30)
        
        # Filter by category and date range
        category_transactions = [
            tx for tx in all_transactions
            if (tx.category == category and 
                start_date <= tx.transaction_date <= end_date)
        ]
        
        # Group by period
        period_groups = defaultdict(list)
        
        for tx in category_transactions:
            if grouping == TimelineGrouping.DAILY:
                period_key = tx.transaction_date
            elif grouping == TimelineGrouping.WEEKLY:
                period_key = tx.transaction_date - timedelta(days=tx.transaction_date.weekday())
            elif grouping == TimelineGrouping.MONTHLY:
                period_key = tx.transaction_date.replace(day=1)
            else:  # YEARLY
                period_key = tx.transaction_date.replace(month=1, day=1)
            
            period_groups[period_key].append(tx)
        
        # Create data points
        data_points = []
        total_amount = Decimal('0')
        
        for period_date, transactions in period_groups.items():
            period_amount = sum(abs(tx.amount) for tx in transactions)  # abs for consistency
            avg_amount = period_amount / len(transactions) if transactions else Decimal('0')
            
            data_point = CategoryTimelinePoint(
                date=period_date,
                category=category,
                amount=period_amount,
                transaction_count=len(transactions),
                avg_amount=avg_amount
            )
            data_points.append(data_point)
            total_amount += period_amount
        
        # Sort by date
        data_points.sort(key=lambda x: x.date)
        
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
    
    def _get_mock_cash_flow(
        self, 
        user_id: str, 
        grouping: TimelineGrouping, 
        months_back: int, 
        starting_balance: Decimal
    ) -> CashFlowResponse:
        """Get cash flow analysis from mock data."""
        # Get all mock transactions
        all_transactions = self.mock_service.get_mock_transactions(user_id)
        
        # Date range
        end_date = date.today()
        start_date = end_date - timedelta(days=months_back * 30)
        
        # Filter by date range
        filtered_transactions = [
            tx for tx in all_transactions
            if start_date <= tx.transaction_date <= end_date
        ]
        
        # Group by period
        period_groups = defaultdict(list)
        
        for tx in filtered_transactions:
            if grouping == TimelineGrouping.DAILY:
                period_key = tx.transaction_date
            elif grouping == TimelineGrouping.WEEKLY:
                period_key = tx.transaction_date - timedelta(days=tx.transaction_date.weekday())
            elif grouping == TimelineGrouping.MONTHLY:
                period_key = tx.transaction_date.replace(day=1)
            else:  # YEARLY
                period_key = tx.transaction_date.replace(month=1, day=1)
            
            period_groups[period_key].append(tx)
        
        # Create cash flow points
        cash_flow_points = []
        running_balance = starting_balance
        total_income = Decimal('0')
        total_expenses = Decimal('0')
        
        # Sort periods chronologically
        sorted_periods = sorted(period_groups.keys())
        
        for period_date in sorted_periods:
            transactions = period_groups[period_date]
            
            opening_balance = running_balance
            period_income = sum(tx.amount for tx in transactions if tx.type == "income")
            period_expenses = sum(abs(tx.amount) for tx in transactions if tx.type == "expense")
            net_change = period_income - period_expenses
            closing_balance = opening_balance + net_change
            
            cash_flow_point = CashFlowPoint(
                date=period_date,
                opening_balance=opening_balance,
                total_income=period_income,
                total_expenses=period_expenses,
                closing_balance=closing_balance,
                net_change=net_change
            )
            
            cash_flow_points.append(cash_flow_point)
            running_balance = closing_balance
            total_income += period_income
            total_expenses += period_expenses
        
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