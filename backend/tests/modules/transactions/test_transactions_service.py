"""Tests for TransactionsService business logic."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from decimal import Decimal
from datetime import date, datetime

from src.modules.transactions.transactions_service import TransactionsService
from src.modules.transactions.transactions_schemas import (
    TransactionCreate, Transaction, TransactionQuery, TransactionListResponse, TransactionUpdate
)
from core.models import TransactionType


@pytest.mark.asyncio
class TestTransactionsService:
    """Test suite for TransactionsService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance with mocked repository."""
        with patch('src.modules.transactions.transactions_service.TransactionsRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            service = TransactionsService()
            service.repository = mock_repo
            return service, mock_repo
    
    async def test_create_transaction_success(self, service, sample_transaction_data, sample_transaction_response):
        """Test successful transaction creation."""
        service_instance, mock_repo = service
        
        # Setup mock response
        expected_transaction = Transaction(**sample_transaction_response)
        mock_repo.create_transaction.return_value = expected_transaction
        
        # Create transaction data
        transaction_data = TransactionCreate(**sample_transaction_data)
        
        # Execute
        result = await service_instance.create_transaction("user123", transaction_data)
        
        # Assertions
        assert result == expected_transaction
        mock_repo.create_transaction.assert_called_once_with("user123", transaction_data)
    
    async def test_create_transaction_validation_error(self, service, sample_transaction_data):
        """Test transaction creation with validation error."""
        service_instance, mock_repo = service
        
        # Setup validation to fail
        with patch.object(service_instance, '_validate_transaction_creation', 
                         side_effect=ValueError("Invalid transaction")):
            transaction_data = TransactionCreate(**sample_transaction_data)
            
            # Execute and assert exception
            with pytest.raises(ValueError, match="Invalid transaction"):
                await service_instance.create_transaction("user123", transaction_data)
            
            # Ensure repository was not called
            mock_repo.create_transaction.assert_not_called()
    
    async def test_get_transactions_paginated_success(self, service):
        """Test successful paginated transaction retrieval."""
        service_instance, mock_repo = service
        
        # Setup mock response
        from datetime import datetime
        mock_transactions = [
            Transaction(
                id="1",
                user_id="user123",
                type=TransactionType.EXPENSE,
                amount=Decimal("-50.00"),
                description="Test 1",
                category="groceries",
                date=date(2024, 1, 15),
                created_at=datetime(2024, 1, 15, 10, 0, 0),
                updated_at=datetime(2024, 1, 15, 10, 0, 0)
            ),
            Transaction(
                id="2", 
                user_id="user123",
                type=TransactionType.INCOME,
                amount=Decimal("100.00"),
                description="Test 2",
                category="salary",
                date=date(2024, 1, 16),
                created_at=datetime(2024, 1, 16, 10, 0, 0),
                updated_at=datetime(2024, 1, 16, 10, 0, 0)
            )
        ]
        mock_total = 2
        mock_repo.get_transactions.return_value = mock_transactions
        mock_repo.count_transactions.return_value = mock_total
        
        # Create query
        query = TransactionQuery(
            limit=10, 
            offset=0,
            min_amount=Decimal("1"), 
            max_amount=Decimal("1000")
        )
        
        # Execute
        result = await service_instance.get_transactions_paginated("user123", query)
        
        # Assertions
        assert isinstance(result, TransactionListResponse)
        assert result.transactions == mock_transactions
        assert result.total_count == mock_total
        assert result.has_more is False
        mock_repo.get_transactions.assert_called_once_with("user123", query)
        mock_repo.count_transactions.assert_called_once_with("user123", query)
    
    async def test_get_transaction_by_id_found(self, service, sample_transaction_response):
        """Test retrieving transaction by ID when found."""
        service_instance, mock_repo = service
        
        # Setup mock response
        expected_transaction = Transaction(**sample_transaction_response)
        mock_repo.get_transaction_by_id.return_value = expected_transaction
        
        # Execute
        result = await service_instance.get_transaction_by_id("user123", "transaction123")
        
        # Assertions
        assert result == expected_transaction
        mock_repo.get_transaction_by_id.assert_called_once_with("user123", "transaction123")
    
    async def test_get_transaction_by_id_not_found(self, service):
        """Test retrieving transaction by ID when not found."""
        service_instance, mock_repo = service
        
        # Setup mock to return None
        mock_repo.get_transaction_by_id.return_value = None
        
        # Execute
        result = await service_instance.get_transaction_by_id("user123", "nonexistent")
        
        # Assertions
        assert result is None
        mock_repo.get_transaction_by_id.assert_called_once_with("user123", "nonexistent")
    
    async def test_update_transaction_success(self, service, sample_transaction_response):
        """Test successful transaction update."""
        service_instance, mock_repo = service
        
        # Setup mock response
        updated_transaction = Transaction(**sample_transaction_response)
        updated_transaction.description = "Updated description"
        mock_repo.update_transaction.return_value = updated_transaction
        
        # Create update data
        update_data = TransactionUpdate(description="Updated description")
        
        # Execute
        result = await service_instance.update_transaction("user123", "transaction123", update_data)
        
        # Assertions
        assert result == updated_transaction
        assert result.description == "Updated description"
        mock_repo.update_transaction.assert_called_once_with("user123", "transaction123", update_data)
    
    async def test_delete_transaction_success(self, service):
        """Test successful transaction deletion."""
        service_instance, mock_repo = service
        
        # Setup mock response
        mock_repo.delete_transaction.return_value = True
        
        # Execute
        result = await service_instance.delete_transaction("user123", "transaction123")
        
        # Assertions
        assert result is True
        mock_repo.delete_transaction.assert_called_once_with("user123", "transaction123")
    
    async def test_delete_transaction_not_found(self, service):
        """Test deleting non-existent transaction."""
        service_instance, mock_repo = service
        
        # Setup mock response
        mock_repo.delete_transaction.return_value = False
        
        # Execute
        result = await service_instance.delete_transaction("user123", "nonexistent")
        
        # Assertions
        assert result is False
        mock_repo.delete_transaction.assert_called_once_with("user123", "nonexistent")
    
    async def test_service_initialization(self, service):
        """Test that service initializes correctly."""
        service_instance, mock_repo = service
        
        # Execute and assert
        assert service_instance is not None
        assert service_instance.repository == mock_repo