"""Timeline repository for data access operations."""

import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from supabase import Client

from core.models import TransactionType
from .schemas import TimelineFilters, TimelineGrouping

logger = logging.getLogger(__name__)


class TimelineRepository:
    """Repository for timeline data operations."""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_timeline_data(
        self, 
        user_id: str, 
        filters: TimelineFilters
    ) -> List[Dict]:
        """Get timeline data with specified grouping."""
        try:
            # Build base query
            query = self.supabase.table('transactions').select('*')
            
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
            
            # Apply transaction type filters
            type_filters = []
            if filters.include_income:
                type_filters.append(TransactionType.INCOME.value)
            if filters.include_expenses:
                type_filters.append(TransactionType.EXPENSE.value)
            
            if type_filters:
                query = query.in_('type', type_filters)
            
            query = query.order('date')
            result = query.execute()
            transactions = result.data
            
            # Group transactions by time period
            grouped_data = {}
            
            for txn in transactions:
                txn_date = datetime.fromisoformat(txn['date']).date()
                period_key = self._get_period_key(txn_date, filters.grouping)
                
                if period_key not in grouped_data:
                    grouped_data[period_key] = {
                        'date': period_key,
                        'income_transactions': [],
                        'expense_transactions': [],
                        'total_income': Decimal('0'),
                        'total_expenses': Decimal('0'),
                        'transaction_count': 0
                    }
                
                amount = Decimal(str(txn['amount']))
                txn_type = txn['type']
                
                grouped_data[period_key]['transaction_count'] += 1
                
                if txn_type == TransactionType.INCOME.value:
                    grouped_data[period_key]['income_transactions'].append(txn)
                    grouped_data[period_key]['total_income'] += amount
                elif txn_type == TransactionType.EXPENSE.value:
                    grouped_data[period_key]['expense_transactions'].append(txn)
                    grouped_data[period_key]['total_expenses'] += amount
            
            # Calculate additional metrics for each period
            for period_data in grouped_data.values():
                period_data['net_amount'] = (
                    period_data['total_income'] - period_data['total_expenses']
                )
                
                # Find largest transactions
                if period_data['expense_transactions']:
                    period_data['largest_expense'] = max(
                        Decimal(str(txn['amount'])) 
                        for txn in period_data['expense_transactions']
                    )
                
                if period_data['income_transactions']:
                    period_data['largest_income'] = max(
                        Decimal(str(txn['amount'])) 
                        for txn in period_data['income_transactions']
                    )
            
            return list(grouped_data.values())
            
        except Exception as e:
            logger.error(f"Error getting timeline data: {e}")
            raise
    
    async def get_category_timeline(
        self, 
        user_id: str,
        category: str,
        grouping: TimelineGrouping,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """Get timeline data for a specific category."""
        try:
            query = (self.supabase.table('transactions')
                    .select('*')
                    .eq('user_id', user_id)
                    .eq('category', category)
                    .gte('date', start_date.isoformat())
                    .lte('date', end_date.isoformat())
                    .order('date'))
            
            result = query.execute()
            transactions = result.data
            
            # Group by time period
            grouped_data = {}
            
            for txn in transactions:
                txn_date = datetime.fromisoformat(txn['date']).date()
                period_key = self._get_period_key(txn_date, grouping)
                
                if period_key not in grouped_data:
                    grouped_data[period_key] = {
                        'date': period_key,
                        'category': category,
                        'amount': Decimal('0'),
                        'transaction_count': 0,
                        'transactions': []
                    }
                
                amount = Decimal(str(txn['amount']))
                grouped_data[period_key]['amount'] += amount
                grouped_data[period_key]['transaction_count'] += 1
                grouped_data[period_key]['transactions'].append(txn)
            
            # Calculate average amount per period
            for period_data in grouped_data.values():
                count = period_data['transaction_count']
                period_data['avg_amount'] = (
                    period_data['amount'] / count if count > 0 else Decimal('0')
                )
            
            return list(grouped_data.values())
            
        except Exception as e:
            logger.error(f"Error getting category timeline: {e}")
            raise
    
    async def get_cash_flow_data(
        self, 
        user_id: str,
        grouping: TimelineGrouping,
        start_date: date,
        end_date: date,
        starting_balance: Decimal = Decimal('0')
    ) -> List[Dict]:
        """Get cash flow data with running balance."""
        try:
            # Get all transactions in date range
            query = (self.supabase.table('transactions')
                    .select('*')
                    .eq('user_id', user_id)
                    .gte('date', start_date.isoformat())
                    .lte('date', end_date.isoformat())
                    .order('date'))
            
            result = query.execute()
            transactions = result.data
            
            # Group by periods and calculate running balance
            grouped_data = {}
            current_balance = starting_balance
            
            # Generate all periods in range first
            current_date = start_date
            while current_date <= end_date:
                period_key = self._get_period_key(current_date, grouping)
                
                if period_key not in grouped_data:
                    grouped_data[period_key] = {
                        'date': period_key,
                        'opening_balance': current_balance,
                        'total_income': Decimal('0'),
                        'total_expenses': Decimal('0'),
                        'transactions': []
                    }
                
                # Move to next period
                if grouping == TimelineGrouping.DAILY:
                    current_date += timedelta(days=1)
                elif grouping == TimelineGrouping.WEEKLY:
                    current_date += timedelta(weeks=1)
                elif grouping == TimelineGrouping.MONTHLY:
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                else:  # YEARLY
                    current_date = current_date.replace(year=current_date.year + 1)
            
            # Process transactions in chronological order
            for txn in transactions:
                txn_date = datetime.fromisoformat(txn['date']).date()
                period_key = self._get_period_key(txn_date, grouping)
                
                if period_key in grouped_data:
                    amount = Decimal(str(txn['amount']))
                    txn_type = txn['type']
                    
                    grouped_data[period_key]['transactions'].append(txn)
                    
                    if txn_type == TransactionType.INCOME.value:
                        grouped_data[period_key]['total_income'] += amount
                    elif txn_type == TransactionType.EXPENSE.value:
                        grouped_data[period_key]['total_expenses'] += amount
            
            # Calculate closing balances and net changes
            periods = sorted(grouped_data.keys())
            running_balance = starting_balance
            
            cash_flow_data = []
            for period_key in periods:
                period_data = grouped_data[period_key]
                period_data['opening_balance'] = running_balance
                
                net_change = period_data['total_income'] - period_data['total_expenses']
                running_balance += net_change
                
                period_data['closing_balance'] = running_balance
                period_data['net_change'] = net_change
                
                cash_flow_data.append(period_data)
            
            return cash_flow_data
            
        except Exception as e:
            logger.error(f"Error getting cash flow data: {e}")
            raise
    
    def _get_period_key(self, txn_date: date, grouping: TimelineGrouping) -> date:
        """Get period key for grouping transactions."""
        if grouping == TimelineGrouping.DAILY:
            return txn_date
        elif grouping == TimelineGrouping.WEEKLY:
            # Get Monday of the week
            return txn_date - timedelta(days=txn_date.weekday())
        elif grouping == TimelineGrouping.MONTHLY:
            return txn_date.replace(day=1)
        else:  # YEARLY
            return txn_date.replace(month=1, day=1)