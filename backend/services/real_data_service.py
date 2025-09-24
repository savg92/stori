"""Real database service for fetching actual user financial data."""

import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from supabase import Client

logger = logging.getLogger(__name__)


class RealDataService:
    """Service for fetching real user financial data from the database."""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client

    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile data."""
        try:
            result = self.supabase.table('users').select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            return None

    async def get_user_transactions(self, user_id: str, days: int = 90) -> List[Dict]:
        """Get user transactions for the specified number of days."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            result = self.supabase.table('transactions').select('*').eq('user_id', user_id).gte('date', cutoff_date).order('date', desc=True).execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching user transactions: {e}")
            return []

    async def get_financial_summary(self, user_id: str, days: int = 30) -> Dict:
        """Get comprehensive financial summary for a user."""
        try:
            transactions = await self.get_user_transactions(user_id, days)
            
            if not transactions:
                return self._get_empty_summary()
            
            # Calculate totals
            total_income = Decimal('0')
            total_expenses = Decimal('0')
            category_breakdown = {}
            monthly_data = {}
            
            for tx in transactions:
                amount = Decimal(str(tx['amount']))
                category = tx['category']
                tx_type = tx['type']
                tx_date = tx['date']
                month_key = tx_date[:7]  # YYYY-MM
                
                # Track by type
                if tx_type == 'income':
                    total_income += amount
                else:
                    total_expenses += abs(amount)
                
                # Category breakdown
                if category not in category_breakdown:
                    category_breakdown[category] = {
                        'total': Decimal('0'),
                        'count': 0,
                        'type': tx_type
                    }
                
                category_breakdown[category]['total'] += abs(amount)
                category_breakdown[category]['count'] += 1
                
                # Monthly breakdown
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'income': Decimal('0'),
                        'expenses': Decimal('0'),
                        'transactions': 0
                    }
                
                if tx_type == 'income':
                    monthly_data[month_key]['income'] += amount
                else:
                    monthly_data[month_key]['expenses'] += abs(amount)
                monthly_data[month_key]['transactions'] += 1
            
            # Calculate metrics
            net_savings = total_income - total_expenses
            savings_rate = float(net_savings / total_income) if total_income > 0 else 0
            
            # Get top spending categories
            top_categories = sorted(
                [(cat, data) for cat, data in category_breakdown.items() if data['type'] == 'expense'],
                key=lambda x: x[1]['total'],
                reverse=True
            )[:5]
            
            return {
                'user_id': user_id,
                'period_days': days,
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'net_savings': float(net_savings),
                'savings_rate': savings_rate,
                'transaction_count': len(transactions),
                'category_breakdown': {
                    cat: {
                        'total': float(data['total']),
                        'count': data['count'],
                        'type': data['type']
                    }
                    for cat, data in category_breakdown.items()
                },
                'top_expense_categories': [
                    {
                        'category': cat,
                        'amount': float(data['total']),
                        'count': data['count'],
                        'percentage': float(data['total'] / total_expenses * 100) if total_expenses > 0 else 0
                    }
                    for cat, data in top_categories
                ],
                'monthly_data': {
                    month: {
                        'income': float(data['income']),
                        'expenses': float(data['expenses']),
                        'net': float(data['income'] - data['expenses']),
                        'transactions': data['transactions']
                    }
                    for month, data in monthly_data.items()
                },
                'financial_health_score': self._calculate_health_score(
                    savings_rate, 
                    float(total_income), 
                    len(category_breakdown)
                ),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating financial summary: {e}")
            return self._get_empty_summary()

    def _calculate_health_score(self, savings_rate: float, income: float, category_diversity: int) -> float:
        """Calculate a financial health score (0-10)."""
        score = 5.0  # Base score
        
        # Savings rate component (0-4 points)
        if savings_rate >= 0.3:
            score += 4
        elif savings_rate >= 0.2:
            score += 3
        elif savings_rate >= 0.1:
            score += 2
        elif savings_rate >= 0.05:
            score += 1
        
        # Income component (0-2 points)
        if income >= 50000:
            score += 2
        elif income >= 30000:
            score += 1
        
        # Category diversity (good spending habits) (0-1 point)
        if category_diversity >= 5:
            score += 1
        elif category_diversity >= 3:
            score += 0.5
        
        # Cap at 10
        return min(10.0, score)

    def _get_empty_summary(self) -> Dict:
        """Return empty summary structure."""
        return {
            'total_income': 0,
            'total_expenses': 0,
            'net_savings': 0,
            'savings_rate': 0,
            'transaction_count': 0,
            'category_breakdown': {},
            'top_expense_categories': [],
            'monthly_data': {},
            'financial_health_score': 0,
            'generated_at': datetime.now().isoformat()
        }

    async def get_spending_trends(self, user_id: str, days: int = 90) -> Dict:
        """Get spending trend analysis."""
        try:
            transactions = await self.get_user_transactions(user_id, days)
            
            if not transactions:
                return {'trends': [], 'insights': []}
            
            # Group by week
            weekly_data = {}
            for tx in transactions:
                if tx['type'] == 'expense':
                    tx_date = datetime.strptime(tx['date'], '%Y-%m-%d').date()
                    # Get week start (Monday)
                    week_start = tx_date - timedelta(days=tx_date.weekday())
                    week_key = week_start.strftime('%Y-W%U')
                    
                    if week_key not in weekly_data:
                        weekly_data[week_key] = {
                            'total': Decimal('0'),
                            'count': 0,
                            'start_date': week_start.strftime('%Y-%m-%d')
                        }
                    
                    weekly_data[week_key]['total'] += abs(Decimal(str(tx['amount'])))
                    weekly_data[week_key]['count'] += 1
            
            # Convert to trend data
            trends = []
            for week_key in sorted(weekly_data.keys()):
                data = weekly_data[week_key]
                trends.append({
                    'period': week_key,
                    'start_date': data['start_date'],
                    'total_spent': float(data['total']),
                    'transaction_count': data['count'],
                    'avg_transaction': float(data['total'] / data['count']) if data['count'] > 0 else 0
                })
            
            # Generate insights
            insights = []
            if len(trends) >= 2:
                latest_week = trends[-1]['total_spent']
                previous_week = trends[-2]['total_spent']
                
                if latest_week > previous_week * 1.2:
                    insights.append("Spending increased significantly this week (+20%)")
                elif latest_week < previous_week * 0.8:
                    insights.append("Good job! Spending decreased this week (-20%)")
                
                # Check for patterns
                avg_spending = sum(t['total_spent'] for t in trends) / len(trends)
                if latest_week > avg_spending * 1.3:
                    insights.append("This week's spending is well above average")
                elif latest_week < avg_spending * 0.7:
                    insights.append("This week's spending is well below average")
            
            return {
                'trends': trends,
                'insights': insights,
                'avg_weekly_spending': sum(t['total_spent'] for t in trends) / len(trends) if trends else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting spending trends: {e}")
            return {'trends': [], 'insights': []}

    async def get_available_users(self) -> List[Dict]:
        """Get list of available users in the database."""
        try:
            result = self.supabase.table('users').select('id, email, full_name').execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Error fetching available users: {e}")
            return []