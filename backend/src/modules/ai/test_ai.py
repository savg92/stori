"""Tests for AI module."""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from src.modules.ai.repository import AIRepository
from src.modules.ai.service import AIService
from src.modules.ai.schemas import (
    AdviceRequest,
    AdviceType,
    AnalysisRequest,
    ChatRequest,
    FinancialContext
)


class TestAIRepository:
    """Test cases for AIRepository."""
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        return MagicMock()
    
    @pytest.fixture
    def repository(self, mock_supabase):
        """AI repository instance."""
        return AIRepository(mock_supabase)
    
    @pytest.mark.asyncio
    async def test_get_financial_context(self, repository, mock_supabase):
        """Test financial context retrieval."""
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
            },
            {
                'user_id': 'user123',
                'type': 'expense',
                'category': 'transport',
                'amount': 30.0,
                'date': '2024-01-10T00:00:00'
            }
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value.data = mock_transactions
        
        result = await repository.get_financial_context('user123', 30)
        
        assert result.total_income == 1000.0
        assert result.total_expenses == 80.0
        assert result.net_amount == 920.0
        assert len(result.top_categories) == 2
        assert result.transaction_count == 3
    
    @pytest.mark.asyncio
    async def test_get_spending_patterns(self, repository, mock_supabase):
        """Test spending patterns analysis."""
        mock_transactions = [
            {
                'amount': 25.0,
                'category': 'food',
                'date': '2024-01-15T00:00:00',
                'description': 'Lunch'
            },
            {
                'amount': 150.0,
                'category': 'shopping',
                'date': '2024-01-16T00:00:00',
                'description': 'Clothes'
            }
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value.data = mock_transactions
        
        result = await repository.get_spending_patterns('user123', 30)
        
        assert 'daily_averages' in result
        assert 'category_frequency' in result
        assert 'amount_distribution' in result
        assert result['transaction_count'] == 2
        assert result['total_analyzed'] == 175.0
    
    @pytest.mark.asyncio
    async def test_get_anomalies(self, repository, mock_supabase):
        """Test anomaly detection."""
        # Create transactions where one is clearly an anomaly
        mock_transactions = [
            {'id': '1', 'amount': 20.0, 'category': 'food', 'date': '2024-01-01', 'description': 'Normal'},
            {'id': '2', 'amount': 25.0, 'category': 'food', 'date': '2024-01-02', 'description': 'Normal'},
            {'id': '3', 'amount': 500.0, 'category': 'shopping', 'date': '2024-01-03', 'description': 'Expensive'},
            {'id': '4', 'amount': 22.0, 'category': 'food', 'date': '2024-01-04', 'description': 'Normal'}
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value.data = mock_transactions
        
        result = await repository.get_anomalies('user123', 30)
        
        assert len(result) >= 1
        # The $500 transaction should be detected as an anomaly
        anomaly = result[0]
        assert anomaly['amount'] == 500.0
        assert anomaly['anomaly_type'] == 'high_amount'


class TestAIService:
    """Test cases for AIService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock AI repository."""
        return AsyncMock(spec=AIRepository)
    
    @pytest.fixture
    def mock_llm_provider(self):
        """Mock LLM provider."""
        mock = AsyncMock()
        mock.generate_response.return_value = '{"summary": "Test summary", "recommendations": ["Test rec"], "data_analysis": {}}'
        return mock
    
    @pytest.fixture
    def service(self, mock_repository):
        """AI service instance without LLM."""
        return AIService(mock_repository)
    
    @pytest.fixture
    def service_with_llm(self, mock_repository, mock_llm_provider):
        """AI service instance with LLM."""
        return AIService(mock_repository, mock_llm_provider)
    
    @pytest.mark.asyncio
    async def test_get_financial_advice_fallback(self, service, mock_repository):
        """Test financial advice generation without LLM."""
        # Mock repository responses
        mock_context = FinancialContext(
            total_income=Decimal('1000'),
            total_expenses=Decimal('800'),
            net_amount=Decimal('200'),
            top_categories=[{'category': 'food', 'total_amount': 300, 'transaction_count': 10, 'avg_amount': 30}],
            recent_trends=[],
            transaction_count=15,
            date_range={'start_date': '2024-01-01', 'end_date': '2024-01-31'}
        )
        
        mock_repository.get_financial_context.return_value = mock_context
        mock_repository.get_spending_patterns.return_value = {}
        
        request = AdviceRequest(
            advice_type=AdviceType.SPENDING_INSIGHTS,
            time_period_days=30
        )
        
        result = await service.get_financial_advice('user123', request)
        
        assert result.advice_type == AdviceType.SPENDING_INSIGHTS
        assert result.summary is not None
        assert len(result.recommendations) > 0
        assert result.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_get_financial_advice_with_llm(self, service_with_llm, mock_repository):
        """Test financial advice generation with LLM."""
        mock_context = FinancialContext(
            total_income=Decimal('1000'),
            total_expenses=Decimal('1200'),  # Overspending scenario
            net_amount=Decimal('-200'),
            top_categories=[{'category': 'food', 'total_amount': 500, 'transaction_count': 10, 'avg_amount': 50}],
            recent_trends=[],
            transaction_count=15,
            date_range={'start_date': '2024-01-01', 'end_date': '2024-01-31'}
        )
        
        mock_repository.get_financial_context.return_value = mock_context
        mock_repository.get_spending_patterns.return_value = {}
        
        request = AdviceRequest(
            advice_type=AdviceType.SPENDING_INSIGHTS,
            time_period_days=30
        )
        
        result = await service_with_llm.get_financial_advice('user123', request)
        
        assert result.advice_type == AdviceType.SPENDING_INSIGHTS
        assert result.summary == "Test summary"
        assert "Test rec" in result.recommendations
        assert len(result.insights) > 0  # Should detect overspending
    
    @pytest.mark.asyncio
    async def test_chat_with_ai_fallback(self, service, mock_repository):
        """Test AI chat without LLM."""
        mock_context = FinancialContext(
            total_income=Decimal('1000'),
            total_expenses=Decimal('800'),
            net_amount=Decimal('200'),
            top_categories=[],
            recent_trends=[],
            transaction_count=10,
            date_range={'start_date': '2024-01-01', 'end_date': '2024-01-31'}
        )
        
        mock_repository.get_financial_context.return_value = mock_context
        
        request = ChatRequest(
            message="How am I doing financially?",
            include_financial_context=True
        )
        
        result = await service.chat_with_ai('user123', request)
        
        assert result.message is not None
        assert result.confidence_score > 0
        assert result.suggested_actions is not None
    
    @pytest.mark.asyncio
    async def test_analyze_financial_data_spending_patterns(self, service, mock_repository):
        """Test financial data analysis for spending patterns."""
        mock_patterns = {
            'daily_averages': {
                'Monday': {'total': 100, 'count': 5, 'average': 20},
                'Tuesday': {'total': 150, 'count': 3, 'average': 50}
            },
            'category_frequency': {'food': 8, 'transport': 5},
            'amount_distribution': {'small': 10, 'medium': 5, 'large': 2},
            'total_analyzed': 500.0,
            'transaction_count': 17,
            'daily_average': 16.67
        }
        
        mock_repository.get_spending_patterns.return_value = mock_patterns
        
        request = AnalysisRequest(
            analysis_type='spending_patterns',
            context_days=30
        )
        
        result = await service.analyze_financial_data('user123', request)
        
        assert result.analysis_type == 'spending_patterns'
        assert result.results == mock_patterns
        assert len(result.insights) > 0
        assert result.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_analyze_financial_data_anomalies(self, service, mock_repository):
        """Test financial data analysis for anomalies."""
        mock_anomalies = [
            {
                'transaction_id': '123',
                'amount': 500.0,
                'category': 'shopping',
                'date': '2024-01-15',
                'deviation_factor': 5.5,
                'anomaly_type': 'high_amount'
            }
        ]
        
        mock_repository.get_anomalies.return_value = mock_anomalies
        
        request = AnalysisRequest(
            analysis_type='anomaly_detection',
            context_days=60
        )
        
        result = await service.analyze_financial_data('user123', request)
        
        assert result.analysis_type == 'anomaly_detection'
        assert result.results['anomalies'] == mock_anomalies
        assert len(result.insights) > 0
    
    def test_generate_fallback_advice(self, service):
        """Test fallback advice generation."""
        mock_context = FinancialContext(
            total_income=Decimal('1000'),
            total_expenses=Decimal('800'),
            net_amount=Decimal('200'),
            top_categories=[{'category': 'food', 'total_amount': 300, 'transaction_count': 10}],
            recent_trends=[],
            transaction_count=15,
            date_range={'start_date': '2024-01-01', 'end_date': '2024-01-31'}
        )
        
        request = AdviceRequest(
            advice_type=AdviceType.SPENDING_INSIGHTS,
            time_period_days=30
        )
        
        result = service._generate_fallback_advice(mock_context, request, [])
        
        assert 'positive cash flow' in result['summary'].lower()
        assert len(result['recommendations']) >= 0
        assert 'income_expense_ratio' in result['data_analysis']
        assert result['confidence_score'] > 0


class TestAISchemas:
    """Test cases for AI schemas."""
    
    def test_advice_request_validation(self):
        """Test advice request validation."""
        request = AdviceRequest(
            advice_type=AdviceType.SPENDING_INSIGHTS,
            time_period_days=30,
            specific_categories=['food', 'transport']
        )
        
        assert request.advice_type == AdviceType.SPENDING_INSIGHTS
        assert request.time_period_days == 30
        assert request.include_data_analysis is True
    
    def test_advice_request_invalid_time_period(self):
        """Test advice request with invalid time period."""
        with pytest.raises(ValueError):
            AdviceRequest(
                advice_type=AdviceType.SPENDING_INSIGHTS,
                time_period_days=400  # Invalid: > 365
            )
    
    def test_chat_request_validation(self):
        """Test chat request validation."""
        request = ChatRequest(
            message="How am I doing?",
            include_financial_context=True,
            max_context_days=30
        )
        
        assert request.message == "How am I doing?"
        assert request.include_financial_context is True
    
    def test_chat_request_empty_message(self):
        """Test chat request with empty message."""
        with pytest.raises(ValueError):
            ChatRequest(message="")
    
    def test_analysis_request_validation(self):
        """Test analysis request validation."""
        request = AnalysisRequest(
            analysis_type='spending_patterns',
            parameters={'category': 'food'},
            include_predictions=True
        )
        
        assert request.analysis_type == 'spending_patterns'
        assert request.parameters['category'] == 'food'
        assert request.include_predictions is True
    
    def test_analysis_request_invalid_type(self):
        """Test analysis request with invalid type."""
        with pytest.raises(ValueError):
            AnalysisRequest(analysis_type='invalid_type')