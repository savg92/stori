"""Tests for expenses module."""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from src.modules.expenses.repository import ExpenseRepository
from src.modules.expenses.service import ExpenseService
from src.modules.expenses.schemas import ExpenseFilters, ExpensePeriod


class TestExpenseRepository:
    """Test cases for ExpenseRepository."""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        return MagicMock()
    
    @pytest.fixture
    def repository(self, mock_supabase):
        """Expense repository instance."""
        return ExpenseRepository(mock_supabase)
    
    @pytest.mark.asyncio
    async def test_get_expense_summary(self, repository, mock_supabase):
        """Test expense summary retrieval."""
        # Mock data
        mock_transactions = [
            {
                'user_id': 'user123',
                'type': 'expense',
                'category': 'food',
                'amount': 50.0,
                'date': '2024-01-15'
            },
            {
                'user_id': 'user123', 
                'type': 'income',
                'category': 'salary',
                'amount': 1000.0,
                'date': '2024-01-01'
            }
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_transactions
        
        filters = ExpenseFilters(period=ExpensePeriod.MONTHLY)
        result = await repository.get_expense_summary('user123', filters)
        
        assert result['total_expenses'] == Decimal('50.0')
        assert result['total_income'] == Decimal('1000.0')
        assert result['net_amount'] == Decimal('950.0')
        assert 'food' in result['category_totals']


class TestExpenseService:
    """Test cases for ExpenseService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock expense repository."""
        return AsyncMock(spec=ExpenseRepository)
    
    @pytest.fixture
    def service(self, mock_repository):
        """Expense service instance."""
        return ExpenseService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_get_expense_summary(self, service, mock_repository):
        """Test expense summary service."""
        # Mock repository response
        mock_repository.get_expense_summary.return_value = {
            'total_expenses': Decimal('200.0'),
            'total_income': Decimal('1500.0'),
            'net_amount': Decimal('1300.0'),
            'category_totals': {'food': Decimal('100.0'), 'transport': Decimal('100.0')},
            'category_counts': {'food': 5, 'transport': 2},
            'transaction_count': 7,
            'transactions': []
        }
        
        filters = ExpenseFilters(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            period=ExpensePeriod.MONTHLY
        )
        
        result = await service.get_expense_summary('user123', filters)
        
        assert result.total_expenses == Decimal('200.0')
        assert result.total_income == Decimal('1500.0')
        assert len(result.category_breakdown) == 2
        assert result.category_breakdown[0].percentage_of_total == 50.0  # Both categories equal
    
    @pytest.mark.asyncio
    async def test_get_expense_trends(self, service, mock_repository):
        """Test expense trends service."""
        mock_repository.get_expense_trends.return_value = [
            {
                'date': date(2024, 1, 1),
                'total_amount': Decimal('150.0'),
                'category_amounts': {'food': Decimal('100.0'), 'transport': Decimal('50.0')},
                'transaction_count': 3
            }
        ]
        
        result = await service.get_expense_trends('user123', ExpensePeriod.DAILY, 30)
        
        assert len(result) == 1
        assert result[0].total_amount == Decimal('150.0')
        assert result[0].date == date(2024, 1, 1)
    
    @pytest.mark.asyncio
    async def test_monthly_comparison(self, service, mock_repository):
        """Test monthly comparison service."""
        # Mock two different monthly summaries
        current_data = {
            'total_expenses': Decimal('300.0'),
            'total_income': Decimal('2000.0'),
            'net_amount': Decimal('1700.0'),
            'category_totals': {'food': Decimal('200.0'), 'transport': Decimal('100.0')},
            'category_counts': {'food': 10, 'transport': 5},
            'transaction_count': 15,
            'transactions': []
        }
        
        previous_data = {
            'total_expenses': Decimal('250.0'),
            'total_income': Decimal('2000.0'),
            'net_amount': Decimal('1750.0'),
            'category_totals': {'food': Decimal('150.0'), 'transport': Decimal('100.0')},
            'category_counts': {'food': 8, 'transport': 5},
            'transaction_count': 13,
            'transactions': []
        }
        
        mock_repository.get_expense_summary.side_effect = [current_data, previous_data]
        
        result = await service.get_monthly_comparison('user123')
        
        assert result['amount_change'] == Decimal('50.0')
        assert result['percentage_change'] == 20.0  # 50/250 * 100
        assert result['is_increase'] is True


class TestExpenseSchemas:
    """Test cases for expense schemas."""
    
    def test_expense_filters_validation(self):
        """Test expense filters validation."""
        filters = ExpenseFilters(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            categories=['food', 'transport'],
            period=ExpensePeriod.MONTHLY
        )
        
        assert filters.start_date == date(2024, 1, 1)
        assert filters.categories == ['food', 'transport']
        assert filters.period == ExpensePeriod.MONTHLY
    
    def test_empty_categories_filter(self):
        """Test that empty categories list becomes None."""
        filters = ExpenseFilters(categories=[])
        assert filters.categories is None