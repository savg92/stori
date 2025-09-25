"""AI repository for data access operations."""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from services.supabase_service import SupabaseClient

from core.models import TransactionType
from .schemas import FinancialContext

logger = logging.getLogger(__name__)


class AIRepository:
    """Repository for AI-related data operations."""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase = supabase_client
    
    async def get_financial_context(
        self, 
        user_id: str,
        days_back: int = 30
    ) -> FinancialContext:
        """Get comprehensive financial context for AI analysis."""
        try:
            # First, get the user's actual transaction date range
            date_range_query = (self.supabase.client.table('transactions')
                              .select('date')
                              .eq('user_id', user_id)
                              .order('date', desc=False))
            
            date_range_result = date_range_query.execute()
            
            if not date_range_result.data:
                # No transactions found, use default date range
                end_date = date.today()
                start_date = end_date - timedelta(days=days_back)
            else:
                # Get the most recent transactions within a reasonable range
                # Use the last transaction date as end_date, and look back from there
                all_dates = [datetime.fromisoformat(row['date']).date() for row in date_range_result.data]
                latest_date = max(all_dates)
                
                # Use either the specified days_back or get recent significant period
                start_date = latest_date - timedelta(days=days_back)
                end_date = latest_date
            
            # Get all transactions in the period
            query = (self.supabase.client.table('transactions')
                    .select('*')
                    .eq('user_id', user_id)
                    .gte('date', start_date.isoformat())
                    .lte('date', end_date.isoformat())
                    .order('date', desc=True))
            
            result = query.execute()
            transactions = result.data
            
            # Calculate basic metrics
            total_income = 0
            total_expenses = 0
            category_totals = {}
            category_counts = {}
            
            for txn in transactions:
                amount = abs(float(txn['amount']))  # Ensure positive amount for calculations
                category = txn['category']
                txn_type = txn['type']
                
                if txn_type == TransactionType.INCOME.value:
                    total_income += amount
                elif txn_type == TransactionType.EXPENSE.value:
                    total_expenses += amount
                    
                    if category not in category_totals:
                        category_totals[category] = 0
                        category_counts[category] = 0
                    category_totals[category] += amount
                    category_counts[category] += 1
            
            # Get top expense categories
            top_categories = []
            for category, total in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]:
                top_categories.append({
                    'category': category,
                    'total_amount': total,
                    'transaction_count': category_counts[category],
                    'avg_amount': total / category_counts[category] if category_counts[category] > 0 else 0
                })
            
            # Calculate weekly trends
            recent_trends = await self._calculate_weekly_trends(user_id, start_date, end_date)
            
            return FinancialContext(
                total_income=total_income,
                total_expenses=total_expenses,
                net_amount=total_income - total_expenses,
                top_categories=top_categories,
                recent_trends=recent_trends,
                transaction_count=len(transactions),
                date_range={
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting financial context: {e}")
            raise
    
    async def get_spending_patterns(
        self, 
        user_id: str,
        days_back: int = 90
    ) -> Dict:
        """Analyze spending patterns for AI insights."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            query = (self.supabase.client.table('transactions')
                    .select('*')
                    .eq('user_id', user_id)
                    .eq('type', TransactionType.EXPENSE.value)
                    .gte('date', start_date.isoformat())
                    .lte('date', end_date.isoformat())
                    .order('date'))
            
            result = query.execute()
            transactions = result.data
            
            # Analyze patterns
            patterns = {
                'daily_averages': {},
                'category_frequency': {},
                'amount_distribution': {'small': 0, 'medium': 0, 'large': 0},
                'seasonal_trends': {},
                'largest_expenses': []
            }
            
            total_amount = 0
            for txn in transactions:
                amount = float(txn['amount'])
                total_amount += amount
                
                # Daily patterns
                txn_date = datetime.fromisoformat(txn['date'])
                day_name = txn_date.strftime('%A')
                if day_name not in patterns['daily_averages']:
                    patterns['daily_averages'][day_name] = {'total': 0, 'count': 0}
                patterns['daily_averages'][day_name]['total'] += amount
                patterns['daily_averages'][day_name]['count'] += 1
                
                # Category frequency
                category = txn['category']
                if category not in patterns['category_frequency']:
                    patterns['category_frequency'][category] = 0
                patterns['category_frequency'][category] += 1
                
                # Amount distribution
                if amount < 20:
                    patterns['amount_distribution']['small'] += 1
                elif amount < 100:
                    patterns['amount_distribution']['medium'] += 1
                else:
                    patterns['amount_distribution']['large'] += 1
                
                # Track largest expenses
                patterns['largest_expenses'].append({
                    'amount': amount,
                    'category': category,
                    'date': txn['date'],
                    'description': txn.get('description', '')
                })
            
            # Calculate daily averages
            for day in patterns['daily_averages']:
                data = patterns['daily_averages'][day]
                data['average'] = data['total'] / data['count'] if data['count'] > 0 else 0
            
            # Sort largest expenses
            patterns['largest_expenses'].sort(key=lambda x: x['amount'], reverse=True)
            patterns['largest_expenses'] = patterns['largest_expenses'][:10]
            
            patterns['total_analyzed'] = total_amount
            patterns['transaction_count'] = len(transactions)
            patterns['daily_average'] = total_amount / days_back if days_back > 0 else 0
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing spending patterns: {e}")
            raise
    
    async def get_anomalies(
        self, 
        user_id: str,
        days_back: int = 60
    ) -> List[Dict]:
        """Detect spending anomalies for AI insights."""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            query = (self.supabase.client.table('transactions')
                    .select('*')
                    .eq('user_id', user_id)
                    .eq('type', TransactionType.EXPENSE.value)
                    .gte('date', start_date.isoformat())
                    .lte('date', end_date.isoformat())
                    .order('amount', desc=True))
            
            result = query.execute()
            transactions = result.data
            
            if not transactions:
                return []
            
            # Calculate basic statistics
            amounts = [float(txn['amount']) for txn in transactions]
            avg_amount = sum(amounts) / len(amounts)
            
            # Simple anomaly detection: transactions > 2 standard deviations from mean
            variance = sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)
            std_dev = variance ** 0.5
            anomaly_threshold = avg_amount + (2 * std_dev)
            
            anomalies = []
            for txn in transactions:
                amount = float(txn['amount'])
                if amount > anomaly_threshold:
                    anomalies.append({
                        'transaction_id': txn['id'],
                        'amount': amount,
                        'category': txn['category'],
                        'date': txn['date'],
                        'description': txn.get('description', ''),
                        'deviation_factor': amount / avg_amount,
                        'anomaly_type': 'high_amount'
                    })
            
            return anomalies[:10]  # Return top 10 anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            raise
    
    async def _calculate_weekly_trends(
        self, 
        user_id: str,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """Calculate weekly spending trends."""
        try:
            # Group transactions by week
            query = (self.supabase.client.table('transactions')
                    .select('*')
                    .eq('user_id', user_id)
                    .eq('type', TransactionType.EXPENSE.value)
                    .gte('date', start_date.isoformat())
                    .lte('date', end_date.isoformat())
                    .order('date'))
            
            result = query.execute()
            transactions = result.data
            
            weekly_totals = {}
            for txn in transactions:
                txn_date = datetime.fromisoformat(txn['date']).date()
                # Get Monday of the week
                week_start = txn_date - timedelta(days=txn_date.weekday())
                
                if week_start not in weekly_totals:
                    weekly_totals[week_start] = 0
                weekly_totals[week_start] += float(txn['amount'])
            
            # Convert to list and calculate trends
            trends = []
            weeks = sorted(weekly_totals.keys())
            
            for i, week in enumerate(weeks):
                trend_data = {
                    'week_start': week.isoformat(),
                    'total_amount': weekly_totals[week]
                }
                
                # Calculate week-over-week change
                if i > 0:
                    previous_week_amount = weekly_totals[weeks[i-1]]
                    change = weekly_totals[week] - previous_week_amount
                    change_percent = (change / previous_week_amount * 100) if previous_week_amount > 0 else 0
                    trend_data['change_amount'] = change
                    trend_data['change_percent'] = change_percent
                
                trends.append(trend_data)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating weekly trends: {e}")
            return []