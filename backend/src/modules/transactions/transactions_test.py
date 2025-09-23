"""Tests for the transactions module."""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, AsyncMock

from src.modules.transactions.transactions_service import TransactionsService
from src.modules.transactions.transactions_schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionType,
    ExpenseCategory
)


class TestTransactionsService:
    """Test cases for TransactionsService."""
    
    @pytest.fixture
    def service(self):
        """Create a TransactionsService instance with mocked repository."""
        service = TransactionsService()
        service.repository = Mock()
        return service
    
    @pytest.fixture
    def sample_transaction_create(self):
        """Sample transaction creation data."""
        return TransactionCreate(
            amount=Decimal("50.00"),
            description="Test expense",
            category=ExpenseCategory.GROCERIES.value,
            type=TransactionType.EXPENSE,
            transaction_date=date.today()
        )
    
    @pytest.mark.asyncio
    async def test_create_transaction_success(self, service, sample_transaction_create):
        """Test successful transaction creation."""
        # Mock repository response
        mock_transaction = {
            "id": "test-id",
            "user_id": "user-123",
            "amount": -50.00,
            "description": "Test expense",
            "category": "groceries",
            "type": "expense",
            "transaction_date": date.today(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        service.repository.create_transaction = AsyncMock(return_value=mock_transaction)
        
        # Test creation
        result = await service.create_transaction("user-123", sample_transaction_create)
        
        # Verify
        assert result.id == "test-id"
        assert result.user_id == "user-123"
        assert result.amount == Decimal("-50.00")
        service.repository.create_transaction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_transaction_zero_amount_validation(self, service):
        """Test validation for zero amount."""
        invalid_transaction = TransactionCreate(
            amount=Decimal("0.00"),
            description="Invalid transaction",
            category=ExpenseCategory.GROCERIES.value,
            type=TransactionType.EXPENSE,
            transaction_date=date.today()
        )
        
        with pytest.raises(ValueError, match="Transaction amount cannot be zero"):
            await service.create_transaction("user-123", invalid_transaction)
    
    @pytest.mark.asyncio
    async def test_create_transaction_future_date_validation(self, service):
        """Test validation for future dates."""
        from datetime import timedelta
        
        future_transaction = TransactionCreate(
            amount=Decimal("50.00"),
            description="Future transaction",
            category=ExpenseCategory.GROCERIES.value,
            type=TransactionType.EXPENSE,
            transaction_date=date.today() + timedelta(days=1)
        )
        
        with pytest.raises(ValueError, match="Transaction date cannot be in the future"):
            await service.create_transaction("user-123", future_transaction)
    
    @pytest.mark.asyncio
    async def test_get_transaction_by_id_found(self, service):
        """Test getting transaction by ID when found."""
        mock_transaction = {
            "id": "test-id",
            "user_id": "user-123",
            "amount": -50.00,
            "description": "Test expense",
            "category": "groceries",
            "type": "expense",
            "transaction_date": date.today(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        service.repository.get_transaction_by_id = AsyncMock(return_value=mock_transaction)
        
        result = await service.get_transaction_by_id("user-123", "test-id")
        
        assert result is not None
        assert result.id == "test-id"
        service.repository.get_transaction_by_id.assert_called_once_with("user-123", "test-id")
    
    @pytest.mark.asyncio
    async def test_get_transaction_by_id_not_found(self, service):
        """Test getting transaction by ID when not found."""
        service.repository.get_transaction_by_id = AsyncMock(return_value=None)
        
        result = await service.get_transaction_by_id("user-123", "nonexistent-id")
        
        assert result is None
        service.repository.get_transaction_by_id.assert_called_once_with("user-123", "nonexistent-id")
    
    @pytest.mark.asyncio
    async def test_update_transaction_success(self, service):
        """Test successful transaction update."""
        # Mock existing transaction
        existing_transaction = {
            "id": "test-id",
            "user_id": "user-123",
            "amount": -50.00,
            "description": "Original expense",
            "category": "groceries",
            "type": "expense",
            "transaction_date": date.today(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Mock updated transaction
        updated_transaction = existing_transaction.copy()
        updated_transaction["description"] = "Updated expense"
        updated_transaction["amount"] = -75.00
        
        service.repository.get_transaction_by_id = AsyncMock(return_value=existing_transaction)
        service.repository.update_transaction = AsyncMock(return_value=updated_transaction)
        
        # Test update
        update_data = TransactionUpdate(
            description="Updated expense",
            amount=Decimal("75.00")
        )
        
        result = await service.update_transaction("user-123", "test-id", update_data)
        
        assert result is not None
        assert result.description == "Updated expense"
        assert result.amount == Decimal("-75.00")
        
        service.repository.get_transaction_by_id.assert_called_once()
        service.repository.update_transaction.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_transaction_success(self, service):
        """Test successful transaction deletion."""
        # Mock existing transaction
        existing_transaction = {
            "id": "test-id",
            "user_id": "user-123",
            "amount": -50.00,
            "description": "Test expense",
            "category": "groceries",
            "type": "expense",
            "transaction_date": date.today(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        service.repository.get_transaction_by_id = AsyncMock(return_value=existing_transaction)
        service.repository.delete_transaction = AsyncMock(return_value=True)
        
        result = await service.delete_transaction("user-123", "test-id")
        
        assert result is True
        service.repository.get_transaction_by_id.assert_called_once()
        service.repository.delete_transaction.assert_called_once_with("user-123", "test-id")


class TestTransactionModuleIntegration:
    """Integration tests for the transactions module."""
    
    def test_module_imports(self):
        """Test that all module components can be imported correctly."""
        from src.modules.transactions import (
            TransactionsController,
            TransactionsService,
            TransactionsRepository
        )
        
        # Verify classes can be instantiated
        assert TransactionsController is not None
        assert TransactionsService is not None
        assert TransactionsRepository is not None
    
    def test_schemas_import(self):
        """Test that transaction schemas can be imported."""
        from src.modules.transactions.transactions_schemas import (
            TransactionCreate,
            TransactionUpdate,
            Transaction,
            TransactionQuery
        )
        
        assert TransactionCreate is not None
        assert TransactionUpdate is not None
        assert Transaction is not None
        assert TransactionQuery is not None