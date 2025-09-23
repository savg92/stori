"""Tests for timeline module."""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from src.modules.timeline.repository import TimelineRepository
from src.modules.timeline.service import TimelineService
from src.modules.timeline.schemas import TimelineFilters, TimelineGrouping


class TestTimelineRepository:
    """Test cases for TimelineRepository."""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        return MagicMock()
    
    @pytest.fixture
    def repository(self, mock_supabase):
        """Timeline repository instance."""
        return TimelineRepository(mock_supabase)
    
    @pytest.mark.asyncio
    async def test_get_timeline_data(self, repository, mock_supabase):
        """Test timeline data retrieval."""
        # Mock data
        mock_transactions = [
            {
                'user_id': 'user123',
                'type': 'expense',
                'category': 'food',
                'amount': 50.0,
                'date': '2024-01-15T00:00:00'
            },
            {
                'user_id': 'user123',
                'type': 'income',
                'category': 'salary',
                'amount': 1000.0,
                'date': '2024-01-01T00:00:00'
            }
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = mock_transactions
        
        filters = TimelineFilters(grouping=TimelineGrouping.MONTHLY)
        result = await repository.get_timeline_data('user123', filters)
        
        assert len(result) == 1  # Both transactions in same month
        assert result[0]['total_income'] == Decimal('1000.0')
        assert result[0]['total_expenses'] == Decimal('50.0')
        assert result[0]['net_amount'] == Decimal('950.0')
    
    def test_get_period_key_daily(self, repository):
        """Test daily period key generation."""
        test_date = date(2024, 1, 15)
        result = repository._get_period_key(test_date, TimelineGrouping.DAILY)
        assert result == test_date
    
    def test_get_period_key_monthly(self, repository):
        """Test monthly period key generation."""
        test_date = date(2024, 1, 15)
        result = repository._get_period_key(test_date, TimelineGrouping.MONTHLY)
        assert result == date(2024, 1, 1)
    
    def test_get_period_key_weekly(self, repository):
        """Test weekly period key generation."""
        # Wednesday, January 17, 2024
        test_date = date(2024, 1, 17)
        result = repository._get_period_key(test_date, TimelineGrouping.WEEKLY)
        # Should return Monday of that week (January 15, 2024)
        expected = date(2024, 1, 15)
        assert result == expected


class TestTimelineService:
    """Test cases for TimelineService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock timeline repository."""
        return AsyncMock(spec=TimelineRepository)
    
    @pytest.fixture
    def service(self, mock_repository):
        """Timeline service instance."""
        return TimelineService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_get_timeline(self, service, mock_repository):
        """Test timeline service."""
        # Mock repository response
        mock_repository.get_timeline_data.return_value = [
            {
                'date': date(2024, 1, 1),
                'total_income': Decimal('1000.0'),
                'total_expenses': Decimal('200.0'),
                'net_amount': Decimal('800.0'),
                'transaction_count': 5,
                'largest_expense': Decimal('100.0'),
                'largest_income': Decimal('1000.0')
            },
            {
                'date': date(2024, 2, 1),
                'total_income': Decimal('1000.0'),
                'total_expenses': Decimal('250.0'),
                'net_amount': Decimal('750.0'),
                'transaction_count': 7,
                'largest_expense': Decimal('120.0'),
                'largest_income': Decimal('1000.0')
            }
        ]
        
        filters = TimelineFilters(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 28),
            grouping=TimelineGrouping.MONTHLY
        )
        
        result = await service.get_timeline('user123', filters)
        
        assert result.grouping == TimelineGrouping.MONTHLY
        assert len(result.data_points) == 2
        assert result.total_periods == 2
        assert result.summary_stats['total_income'] == Decimal('2000.0')
        assert result.summary_stats['total_expenses'] == Decimal('450.0')
    
    @pytest.mark.asyncio
    async def test_get_category_timeline(self, service, mock_repository):
        """Test category timeline service."""
        mock_repository.get_category_timeline.return_value = [
            {
                'date': date(2024, 1, 1),
                'category': 'food',
                'amount': Decimal('200.0'),
                'transaction_count': 10,
                'avg_amount': Decimal('20.0'),
                'transactions': []
            }
        ]
        
        result = await service.get_category_timeline(
            'user123', 
            'food', 
            TimelineGrouping.MONTHLY, 
            6
        )
        
        assert result.category == 'food'
        assert result.grouping == TimelineGrouping.MONTHLY
        assert len(result.data_points) == 1
        assert result.total_amount == Decimal('200.0')
        assert result.avg_per_period == Decimal('200.0')
    
    @pytest.mark.asyncio
    async def test_get_cash_flow(self, service, mock_repository):
        """Test cash flow service."""
        mock_repository.get_cash_flow_data.return_value = [
            {
                'date': date(2024, 1, 1),
                'opening_balance': Decimal('1000.0'),
                'total_income': Decimal('1500.0'),
                'total_expenses': Decimal('800.0'),
                'closing_balance': Decimal('1700.0'),
                'net_change': Decimal('700.0')
            }
        ]
        
        result = await service.get_cash_flow(
            'user123',
            TimelineGrouping.MONTHLY,
            6,
            Decimal('1000.0')
        )
        
        assert result.grouping == TimelineGrouping.MONTHLY
        assert len(result.cash_flow_points) == 1
        assert result.starting_balance == Decimal('1000.0')
        assert result.ending_balance == Decimal('1700.0')
        assert result.net_cash_flow == Decimal('700.0')
    
    @pytest.mark.asyncio
    async def test_spending_velocity(self, service, mock_repository):
        """Test spending velocity calculation."""
        # Mock timeline data for 10 days
        mock_timeline_data = []
        for i in range(10):
            mock_timeline_data.append({
                'date': date(2024, 1, 1) + timedelta(days=i),
                'total_income': Decimal('0'),
                'total_expenses': Decimal(str(50 + i * 5)),  # Increasing spending
                'net_amount': Decimal(str(-50 - i * 5)),
                'transaction_count': 1
            })
        
        mock_repository.get_timeline_data.return_value = mock_timeline_data
        
        result = await service.get_spending_velocity('user123', 10)
        
        assert result['days_analyzed'] == 10
        assert result['velocity_trend'] == 'increasing'  # Spending is increasing
        assert result['total_spent'] > Decimal('0')


class TestTimelineSchemas:
    """Test cases for timeline schemas."""
    
    def test_timeline_filters_validation(self):
        """Test timeline filters validation."""
        filters = TimelineFilters(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            grouping=TimelineGrouping.DAILY,
            categories=['food', 'transport'],
            include_income=True,
            include_expenses=True
        )
        
        assert filters.start_date == date(2024, 1, 1)
        assert filters.grouping == TimelineGrouping.DAILY
        assert filters.categories == ['food', 'transport']
    
    def test_empty_categories_filter(self):
        """Test that empty categories list becomes None."""
        filters = TimelineFilters(categories=[])
        assert filters.categories is None