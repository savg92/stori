"""Expense repository for data access operations."""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from services.supabase_service import SupabaseClient

from core.models import Transaction, TransactionType
from .schemas import ExpenseFilters, ExpensePeriod

logger = logging.getLogger(__name__)


class ExpenseRepository:
    """Repository for expense data operations."""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase = supabase_client
    
    async def get_expense_summary(
        self, 
        user_id: str, 
        filters: ExpenseFilters
    ) -> Dict:
        """Get expense summary with category breakdown."""
        try:
            # Build base query
            query = self.supabase.client.table('transactions').select('*')
            
            # Apply user filter
            query = query.eq('user_id', user_id)
            
            # Apply date filters
            if filters.start_date:
                query = query.gte('date', filters.start_date.isoformat())
            if filters.end_date:
                query = query.lte('date', filters.end_date.isoformat())
            
            # Apply category filters
            if filters.categories:
                query = query.in_('category', filters.categories)
            
            # Apply amount filters
            if filters.min_amount:
                query = query.gte('amount', float(filters.min_amount))
            if filters.max_amount:
                query = query.lte('amount', float(filters.max_amount))
            
            result = query.execute()
            transactions = result.data
            
            # Calculate summary statistics
            total_expenses = Decimal('0')
            total_income = Decimal('0')
            category_totals = {}
            category_counts = {}
            
            for txn in transactions:
                amount = Decimal(str(txn['amount']))
                category = txn['category']
                txn_type = txn['type']
                
                if txn_type == TransactionType.EXPENSE.value:
                    total_expenses += amount
                    if category not in category_totals:
                        category_totals[category] = Decimal('0')
                        category_counts[category] = 0
                    category_totals[category] += amount
                    category_counts[category] += 1
                elif txn_type == TransactionType.INCOME.value:
                    total_income += amount
            
            return {
                'total_expenses': total_expenses,
                'total_income': total_income,
                'net_amount': total_income - total_expenses,
                'category_totals': category_totals,
                'category_counts': category_counts,
                'transaction_count': len(transactions),
                'transactions': transactions
            }
            
        except Exception as e:
            logger.error(f"Error getting expense summary: {e}")
            raise
    
    async def get_expense_trends(
        self, 
        user_id: str, 
        period: ExpensePeriod,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """Get expense trends grouped by time period."""
        try:
            query = (self.supabase.client.table('transactions')
                    .select('*')
                    .eq('user_id', user_id)
                    .eq('type', TransactionType.EXPENSE.value)
                    .gte('date', start_date.isoformat())
                    .lte('date', end_date.isoformat())
                    .order('date'))
            
            result = query.execute()
            transactions = result.data
            
            # Group transactions by period
            trends = {}
            for txn in transactions:
                txn_date = datetime.fromisoformat(txn['date']).date()
                
                # Determine period key based on period type
                if period == ExpensePeriod.DAILY:
                    period_key = txn_date
                elif period == ExpensePeriod.WEEKLY:
                    # Get Monday of the week
                    period_key = txn_date - datetime.timedelta(days=txn_date.weekday())
                elif period == ExpensePeriod.MONTHLY:
                    period_key = txn_date.replace(day=1)
                else:  # YEARLY
                    period_key = txn_date.replace(month=1, day=1)
                
                if period_key not in trends:
                    trends[period_key] = {
                        'date': period_key,
                        'total_amount': Decimal('0'),
                        'category_amounts': {},
                        'transaction_count': 0
                    }
                
                amount = Decimal(str(txn['amount']))
                category = txn['category']
                
                trends[period_key]['total_amount'] += amount
                trends[period_key]['transaction_count'] += 1
                
                if category not in trends[period_key]['category_amounts']:
                    trends[period_key]['category_amounts'][category] = Decimal('0')
                trends[period_key]['category_amounts'][category] += amount
            
            return list(trends.values())
            
        except Exception as e:
            logger.error(f"Error getting expense trends: {e}")
            raise
    
    async def get_top_categories(
        self, 
        user_id: str, 
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict]:
        """Get top expense categories by total amount."""
        try:
            query = (self.supabase.client.table('transactions')
                    .select('*')
                    .eq('user_id', user_id)
                    .eq('type', TransactionType.EXPENSE.value))
            
            if start_date:
                query = query.gte('date', start_date.isoformat())
            if end_date:
                query = query.lte('date', end_date.isoformat())
            
            result = query.execute()
            transactions = result.data
            
            # Group by category
            category_stats = {}
            for txn in transactions:
                category = txn['category']
                amount = Decimal(str(txn['amount']))
                
                if category not in category_stats:
                    category_stats[category] = {
                        'category': category,
                        'total_amount': Decimal('0'),
                        'transaction_count': 0
                    }
                
                category_stats[category]['total_amount'] += amount
                category_stats[category]['transaction_count'] += 1
            
            # Sort by total amount and return top categories
            sorted_categories = sorted(
                category_stats.values(),
                key=lambda x: x['total_amount'],
                reverse=True
            )
            
            return sorted_categories[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top categories: {e}")
            raise

    async def get_user_transaction_date_range(self, user_id: str) -> Optional[Tuple[date, date]]:
        """Get the date range of transactions for a user."""
        try:
            # Get the earliest and latest transaction dates
            response = self.supabase.client.table('transactions').select('date').eq('user_id', user_id).order('date').execute()
            
            if not response.data:
                return None
                
            dates = [datetime.fromisoformat(row['date']).date() for row in response.data]
            return (min(dates), max(dates))
            
        except Exception as e:
            logger.error(f"Error getting user transaction date range: {e}")
            return None