"""Transaction business logic service."""

import logging
from typing import List, Optional, Tuple
from datetime import date, datetime
from decimal import Decimal

from .transactions_repository import TransactionsRepository
from .transactions_schemas import (
    TransactionCreate,
    TransactionUpdate,
    Transaction,
    TransactionQuery,
    TransactionListResponse
)
from services.mock_data_service import get_mock_data_service

logger = logging.getLogger(__name__)


class TransactionsService:
    """Service layer for transaction business logic."""
    
    def __init__(self):
        """Initialize service with repository."""
        self.repository = TransactionsRepository()
        self.mock_service = get_mock_data_service()
    
    async def create_transaction(
        self, 
        user_id: str, 
        transaction_data: TransactionCreate
    ) -> Transaction:
        """Create a new transaction with business logic validation."""
        try:
            # Validate business rules
            await self._validate_transaction_creation(user_id, transaction_data)
            
            # Create transaction
            transaction = await self.repository.create_transaction(
                user_id, transaction_data
            )
            
            logger.info(f"Created transaction {transaction.id} for user {user_id}")
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to create transaction: {e}")
            raise
    
    async def get_transactions_paginated(
        self, 
        user_id: str, 
        query: TransactionQuery
    ) -> TransactionListResponse:
        """Get paginated transactions with metadata."""
        try:
            # Check if this is a mock user - if so, use mock data
            if self.mock_service.is_mock_user(user_id):
                logger.info(f"Using mock data for user {user_id}")
                return self._get_mock_transactions_paginated(user_id, query)
            
            # Get transactions and total count in parallel for real users
            transactions = await self.repository.get_transactions(user_id, query)
            total_count = await self.repository.count_transactions(user_id, query)
            
            # Calculate pagination metadata
            total_pages = (total_count + query.limit - 1) // query.limit
            current_page = (query.offset // query.limit) + 1
            has_next = current_page < total_pages
            has_previous = current_page > 1
            
            return TransactionListResponse(
                transactions=transactions,
                total_count=total_count,
                total_pages=total_pages,
                current_page=current_page,
                has_next=has_next,
                has_previous=has_previous,
                limit=query.limit,
                offset=query.offset
            )
            
        except Exception as e:
            logger.error(f"Failed to get paginated transactions: {e}")
            raise
    
    async def get_transaction_by_id(
        self, 
        user_id: str, 
        transaction_id: str
    ) -> Optional[Transaction]:
        """Get a specific transaction by ID."""
        try:
            transaction = await self.repository.get_transaction_by_id(
                user_id, transaction_id
            )
            
            if not transaction:
                logger.warning(f"Transaction {transaction_id} not found for user {user_id}")
                
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to get transaction {transaction_id}: {e}")
            raise
    
    async def update_transaction(
        self, 
        user_id: str, 
        transaction_id: str, 
        update_data: TransactionUpdate
    ) -> Optional[Transaction]:
        """Update an existing transaction with validation."""
        try:
            # Validate update
            await self._validate_transaction_update(user_id, transaction_id, update_data)
            
            # Update transaction
            updated = await self.repository.update_transaction(
                user_id, transaction_id, update_data
            )
            
            if updated:
                logger.info(f"Updated transaction {transaction_id} for user {user_id}")
            else:
                logger.warning(f"Transaction {transaction_id} not found for update")
                
            return updated
            
        except Exception as e:
            logger.error(f"Failed to update transaction {transaction_id}: {e}")
            raise
    
    async def delete_transaction(
        self, 
        user_id: str, 
        transaction_id: str
    ) -> bool:
        """Delete a transaction with validation."""
        try:
            # Validate deletion
            await self._validate_transaction_deletion(user_id, transaction_id)
            
            # Delete transaction
            deleted = await self.repository.delete_transaction(user_id, transaction_id)
            
            if deleted:
                logger.info(f"Deleted transaction {transaction_id} for user {user_id}")
            else:
                logger.warning(f"Transaction {transaction_id} not found for deletion")
                
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete transaction {transaction_id}: {e}")
            raise
    
    async def _validate_transaction_creation(
        self, 
        user_id: str, 
        transaction_data: TransactionCreate
    ) -> None:
        """Validate transaction creation business rules."""
        # Amount validation
        if transaction_data.amount == 0:
            raise ValueError("Transaction amount cannot be zero")
        
        # Date validation (not future dates)
        if transaction_data.transaction_date > date.today():
            raise ValueError("Transaction date cannot be in the future")
        
        # Category validation based on type
        if transaction_data.type.value == "expense" and transaction_data.amount > 0:
            # For expenses, amount should be negative or will be converted
            transaction_data.amount = -abs(transaction_data.amount)
        elif transaction_data.type.value == "income" and transaction_data.amount < 0:
            # For income, amount should be positive
            transaction_data.amount = abs(transaction_data.amount)
    
    async def _validate_transaction_update(
        self, 
        user_id: str, 
        transaction_id: str, 
        update_data: TransactionUpdate
    ) -> None:
        """Validate transaction update business rules."""
        # Check if transaction exists
        existing = await self.repository.get_transaction_by_id(user_id, transaction_id)
        if not existing:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        # Amount validation
        if update_data.amount is not None and update_data.amount == 0:
            raise ValueError("Transaction amount cannot be zero")
        
        # Date validation
        if update_data.transaction_date and update_data.transaction_date > date.today():
            raise ValueError("Transaction date cannot be in the future")
    
    async def _validate_transaction_deletion(
        self, 
        user_id: str, 
        transaction_id: str
    ) -> None:
        """Validate transaction deletion business rules."""
        # Check if transaction exists
        existing = await self.repository.get_transaction_by_id(user_id, transaction_id)
        if not existing:
            raise ValueError(f"Transaction {transaction_id} not found")
    
    def _get_mock_transactions_paginated(
        self, 
        user_id: str, 
        query: TransactionQuery
    ) -> TransactionListResponse:
        """Get paginated mock transactions."""
        # Get all mock transactions for the user
        all_transactions = self.mock_service.get_mock_transactions(user_id)
        
        # Apply filtering
        filtered_transactions = []
        for tx in all_transactions:
            # Date range filtering
            if query.start_date and tx.transaction_date < query.start_date:
                continue
            if query.end_date and tx.transaction_date > query.end_date:
                continue
            
            # Category filtering
            if query.category and tx.category != query.category:
                continue
            
            # Type filtering
            if query.transaction_type and tx.type != query.transaction_type:
                continue
            
            filtered_transactions.append(tx)
        
        # Sort by date (newest first)
        filtered_transactions.sort(key=lambda x: x.transaction_date, reverse=True)
        
        # Apply pagination
        total_count = len(filtered_transactions)
        start_idx = query.offset
        end_idx = start_idx + query.limit
        paginated_transactions = filtered_transactions[start_idx:end_idx]
        
        # Calculate pagination metadata
        total_pages = (total_count + query.limit - 1) // query.limit if total_count > 0 else 0
        current_page = (query.offset // query.limit) + 1
        has_next = current_page < total_pages
        has_previous = current_page > 1
        
        return TransactionListResponse(
            transactions=paginated_transactions,
            total_count=total_count,
            total_pages=total_pages,
            current_page=current_page,
            has_next=has_next,
            has_previous=has_previous,
            limit=query.limit,
            offset=query.offset
        )