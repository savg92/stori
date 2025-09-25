"""Expense service layer for business logic."""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from core.models import Transaction
from .repository import ExpenseRepository
from .schemas import (
    CategorySummaryResponse,
    ExpenseFilters,
    ExpensePeriod, 
    ExpenseSummaryResponse,
    ExpenseTrendResponse
)

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service layer for expense operations."""
    
    def __init__(self, repository: ExpenseRepository):
        self.repository = repository
    
    async def get_expense_summary(
        self, 
        user_id: str, 
        filters: ExpenseFilters
    ) -> ExpenseSummaryResponse:
        """Get comprehensive expense summary."""
        try:
            # Set default date range if not provided
            if not filters.start_date or not filters.end_date:
                # Get the user's actual transaction date range
                date_range = await self.repository.get_user_transaction_date_range(user_id)
                
                if date_range:
                    earliest_date, latest_date = date_range
                    
                    # Set end date to the latest available transaction
                    end_date = latest_date
                    
                    # Set start date based on period from the latest transaction
                    if filters.period == ExpensePeriod.DAILY:
                        start_date = end_date
                    elif filters.period == ExpensePeriod.WEEKLY:
                        start_date = end_date - timedelta(days=7)
                        # Make sure we don't go before the earliest transaction
                        start_date = max(start_date, earliest_date)
                    elif filters.period == ExpensePeriod.MONTHLY:
                        # Get the month of the latest transaction
                        start_date = end_date.replace(day=1)
                    else:  # YEARLY
                        # Get the year of the latest transaction
                        start_date = end_date.replace(month=1, day=1)
                else:
                    # Fallback to current date if no transactions found
                    end_date = date.today()
                    start_date = end_date.replace(day=1)
                
                filters.start_date = filters.start_date or start_date
                filters.end_date = filters.end_date or end_date
            
            summary_data = await self.repository.get_expense_summary(user_id, filters)
            
            # Calculate category breakdown with percentages
            category_breakdown = []
            total_expenses = summary_data['total_expenses']
            
            for category, total_amount in summary_data['category_totals'].items():
                count = summary_data['category_counts'].get(category, 0)
                percentage = float(total_amount / total_expenses * 100) if total_expenses > 0 else 0
                avg_amount = total_amount / count if count > 0 else Decimal('0')
                
                category_breakdown.append(CategorySummaryResponse(
                    category=category,
                    total_amount=total_amount,
                    transaction_count=count,
                    percentage_of_total=percentage,
                    avg_amount=avg_amount
                ))
            
            # Sort by total amount descending
            category_breakdown.sort(key=lambda x: x.total_amount, reverse=True)
            
            return ExpenseSummaryResponse(
                period=filters.period,
                total_expenses=summary_data['total_expenses'],
                total_income=summary_data['total_income'],
                net_amount=summary_data['net_amount'],
                category_breakdown=category_breakdown,
                transaction_count=summary_data['transaction_count'],
                date_range={
                    'start_date': filters.start_date,
                    'end_date': filters.end_date
                }
            )
            
        except Exception as e:
            logger.error(f"Error in expense summary service: {e}")
            raise
    
    async def get_expense_trends(
        self, 
        user_id: str,
        period: ExpensePeriod = ExpensePeriod.MONTHLY,
        months_back: int = 12
    ) -> List[ExpenseTrendResponse]:
        """Get expense trends over time."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=months_back * 30)  # Approximate months
            
            trend_data = await self.repository.get_expense_trends(
                user_id, period, start_date, end_date
            )
            
            return [
                ExpenseTrendResponse(
                    date=item['date'],
                    total_amount=item['total_amount'],
                    category_amounts=item['category_amounts'],
                    transaction_count=item['transaction_count']
                )
                for item in trend_data
            ]
            
        except Exception as e:
            logger.error(f"Error in expense trends service: {e}")
            raise
    
    async def get_top_expense_categories(
        self, 
        user_id: str,
        limit: int = 10,
        period: ExpensePeriod = ExpensePeriod.MONTHLY
    ) -> List[CategorySummaryResponse]:
        """Get top expense categories."""
        try:
            # Calculate date range based on period
            end_date = date.today()
            if period == ExpensePeriod.DAILY:
                start_date = end_date
            elif period == ExpensePeriod.WEEKLY:
                start_date = end_date - timedelta(days=7)
            elif period == ExpensePeriod.MONTHLY:
                start_date = end_date.replace(day=1)
            else:  # YEARLY
                start_date = end_date.replace(month=1, day=1)
            
            categories = await self.repository.get_top_categories(
                user_id, limit, start_date, end_date
            )
            
            # Calculate total for percentage calculations
            total_amount = sum(cat['total_amount'] for cat in categories)
            
            return [
                CategorySummaryResponse(
                    category=cat['category'],
                    total_amount=cat['total_amount'],
                    transaction_count=cat['transaction_count'],
                    percentage_of_total=float(cat['total_amount'] / total_amount * 100) if total_amount > 0 else 0,
                    avg_amount=cat['total_amount'] / cat['transaction_count'] if cat['transaction_count'] > 0 else Decimal('0')
                )
                for cat in categories
            ]
            
        except Exception as e:
            logger.error(f"Error in top categories service: {e}")
            raise
    
    async def get_monthly_comparison(
        self, 
        user_id: str,
        current_month: Optional[date] = None
    ) -> dict:
        """Compare current month expenses to previous month."""
        try:
            if not current_month:
                current_month = date.today().replace(day=1)
            
            # Previous month
            if current_month.month == 1:
                previous_month = current_month.replace(year=current_month.year - 1, month=12)
            else:
                previous_month = current_month.replace(month=current_month.month - 1)
            
            # Get expenses for both months
            current_filters = ExpenseFilters(
                start_date=current_month,
                end_date=current_month.replace(day=28) + timedelta(days=4),  # End of month
                period=ExpensePeriod.MONTHLY
            )
            
            previous_filters = ExpenseFilters(
                start_date=previous_month, 
                end_date=previous_month.replace(day=28) + timedelta(days=4),
                period=ExpensePeriod.MONTHLY
            )
            
            current_summary = await self.get_expense_summary(user_id, current_filters)
            previous_summary = await self.get_expense_summary(user_id, previous_filters)
            
            # Calculate comparison metrics
            amount_change = current_summary.total_expenses - previous_summary.total_expenses
            percentage_change = (
                float(amount_change / previous_summary.total_expenses * 100) 
                if previous_summary.total_expenses > 0 else 0
            )
            
            return {
                'current_month': current_summary,
                'previous_month': previous_summary,
                'amount_change': amount_change,
                'percentage_change': percentage_change,
                'is_increase': amount_change > 0
            }
            
        except Exception as e:
            logger.error(f"Error in monthly comparison service: {e}")
            raise
    
