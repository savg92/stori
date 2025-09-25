"""Transaction repository for database operations."""

import logging
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal

from services.supabase_service import SupabaseClient
from .transactions_schemas import (
    TransactionCreate,
    TransactionUpdate, 
    Transaction,
    TransactionQuery
)

logger = logging.getLogger(__name__)


class TransactionsRepository:
    """Repository for transaction database operations."""
    
    def __init__(self):
        """Initialize repository with Supabase client."""
        self.db = SupabaseClient()
    
    async def create_transaction(
        self, 
        user_id: str, 
        transaction_data: TransactionCreate
    ) -> Transaction:
        """Create a new transaction in the database."""
        try:
            # Prepare transaction data for database
            db_data = {
                "user_id": user_id,
                "amount": float(transaction_data.amount),
                "description": transaction_data.description,
                "category": transaction_data.category,
                "type": transaction_data.type.value,
                "transaction_date": transaction_data.transaction_date.isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert into database
            result = await self.db.create_transaction(db_data)
            
            # Convert back to response model
            return Transaction(**result)
            
        except Exception as e:
            logger.error(f"Failed to create transaction: {e}")
            raise
    
    async def get_transactions(
        self, 
        user_id: str, 
        query: TransactionQuery
    ) -> List[Transaction]:
        """Get transactions for a user with optional filtering."""
        try:
            # Build query parameters
            filters = {"user_id": user_id}
            
            if query.transaction_type:
                filters["transaction_type"] = query.transaction_type.value
                
            if query.category:
                filters["category"] = query.category
                
            # Apply date range filtering
            if query.start_date:
                filters["start_date"] = query.start_date.isoformat()
            if query.end_date:
                filters["end_date"] = query.end_date.isoformat()
                
            # Get transactions from database
            transactions = await self.db.get_transactions(
                user_id=user_id,
                filters=filters,
                limit=query.limit,
                offset=query.offset
            )
            
            # Convert to response models
            return [Transaction(**tx) for tx in transactions]
            
        except Exception as e:
            logger.error(f"Failed to get transactions: {e}")
            raise
    
    async def get_transaction_by_id(
        self, 
        user_id: str, 
        transaction_id: str
    ) -> Optional[Transaction]:
        """Get a specific transaction by ID."""
        try:
            transaction = await self.db.get_transaction_by_id(user_id, transaction_id)
            
            if transaction:
                return Transaction(**transaction)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get transaction {transaction_id}: {e}")
            raise
    
    async def update_transaction(
        self, 
        user_id: str, 
        transaction_id: str, 
        update_data: TransactionUpdate
    ) -> Optional[Transaction]:
        """Update an existing transaction."""
        try:
            # Prepare update data
            db_update = {}
            
            if update_data.amount is not None:
                db_update["amount"] = float(update_data.amount)
            if update_data.description is not None:
                db_update["description"] = update_data.description
            if update_data.category is not None:
                db_update["category"] = update_data.category
            if update_data.type is not None:
                db_update["type"] = update_data.type.value
            if update_data.transaction_date is not None:
                db_update["transaction_date"] = update_data.transaction_date.isoformat()
                
            db_update["updated_at"] = datetime.utcnow().isoformat()
            
            # Update in database
            updated = await self.db.update_transaction(transaction_id, db_update)
            
            if updated:
                return Transaction(**updated)
            return None
            
        except Exception as e:
            logger.error(f"Failed to update transaction {transaction_id}: {e}")
            raise
    
    async def delete_transaction(
        self, 
        user_id: str, 
        transaction_id: str
    ) -> bool:
        """Delete a transaction."""
        try:
            return await self.db.delete_transaction(transaction_id)
            
        except Exception as e:
            logger.error(f"Failed to delete transaction {transaction_id}: {e}")
            raise
    
    async def count_transactions(
        self, 
        user_id: str, 
        query: TransactionQuery
    ) -> int:
        """Count total transactions matching query criteria."""
        try:
            # Build filters same as get_transactions
            filters = {"user_id": user_id}
            
            if query.transaction_type:
                filters["type"] = query.transaction_type.value
                
            if query.category:
                filters["category"] = query.category
                
            # Apply date range filtering
            if query.start_date:
                filters["start_date"] = query.start_date.isoformat()
            if query.end_date:
                filters["end_date"] = query.end_date.isoformat()
                
            return await self.db.count_transactions(user_id, filters)
            
        except Exception as e:
            logger.error(f"Failed to count transactions: {e}")
            raise