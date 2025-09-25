"""Transaction controller for HTTP endpoints."""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from services.auth_middleware import get_current_user
from .transactions_service import TransactionsService
from .transactions_schemas import (
    TransactionCreate,
    TransactionUpdate,
    Transaction,
    TransactionQuery,
    TransactionListResponse,
    TransactionType
)

logger = logging.getLogger(__name__)


class TransactionsController:
    """Controller for transaction endpoints."""
    
    def __init__(self):
        """Initialize controller with service."""
        self.service = TransactionsService()
        self.router = APIRouter(prefix="/transactions", tags=["transactions"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.router.post("/", response_model=Transaction, status_code=201)
        async def create_transaction(
            transaction_data: TransactionCreate,
            current_user: Dict[str, Any] = Depends(get_current_user)
        ) -> Transaction:
            """Create a new transaction."""
            try:
                return await self.service.create_transaction(
                    current_user["user_id"], transaction_data
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Error creating transaction: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.router.get("/", response_model=TransactionListResponse)
        async def get_transactions(
            transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
            category: Optional[str] = Query(None, description="Filter by category"),
            start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
            end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
            limit: int = Query(50, ge=1, le=100, description="Number of results per page"),
            offset: int = Query(0, ge=0, description="Number of results to skip"),
            current_user: Dict[str, Any] = Depends(get_current_user)
        ) -> TransactionListResponse:
            """Get paginated transactions for the current user."""
            try:
                # Debug logging
                logger.info(f"🔍 Transactions Controller - User ID: {current_user['user_id']}")
                logger.info(f"🔍 Transactions Controller - User Email: {current_user.get('email', 'Unknown')}")
                
                # Build query object
                query = TransactionQuery(
                    transaction_type=transaction_type,
                    category=category,
                    start_date=start_date,
                    end_date=end_date,
                    limit=limit,
                    offset=offset
                )
                
                return await self.service.get_transactions_paginated(
                    current_user["user_id"], query
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Error getting transactions: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.router.get("/{transaction_id}", response_model=Transaction)
        async def get_transaction_by_id(
            transaction_id: str,
            current_user: Dict[str, Any] = Depends(get_current_user)
        ) -> Transaction:
            """Get a specific transaction by ID."""
            try:
                transaction = await self.service.get_transaction_by_id(
                    current_user["user_id"], transaction_id
                )
                
                if not transaction:
                    raise HTTPException(status_code=404, detail="Transaction not found")
                
                return transaction
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting transaction {transaction_id}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.router.put("/{transaction_id}", response_model=Transaction)
        async def update_transaction(
            transaction_id: str,
            update_data: TransactionUpdate,
            current_user: Dict[str, Any] = Depends(get_current_user)
        ) -> Transaction:
            """Update an existing transaction."""
            try:
                updated = await self.service.update_transaction(
                    current_user["user_id"], transaction_id, update_data
                )
                
                if not updated:
                    raise HTTPException(status_code=404, detail="Transaction not found")
                
                return updated
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error updating transaction {transaction_id}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.router.delete("/{transaction_id}")
        async def delete_transaction(
            transaction_id: str,
            current_user: Dict[str, Any] = Depends(get_current_user)
        ) -> JSONResponse:
            """Delete a transaction."""
            try:
                deleted = await self.service.delete_transaction(
                    current_user["user_id"], transaction_id
                )
                
                if not deleted:
                    raise HTTPException(status_code=404, detail="Transaction not found")
                
                return JSONResponse(
                    content={"message": "Transaction deleted successfully"},
                    status_code=200
                )
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error deleting transaction {transaction_id}: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        # Health endpoint for the transactions module
        @self.router.get("/health/status")
        async def transactions_health():
            """Health check for transactions module."""
            return {"module": "transactions", "status": "healthy"}


# Create controller instance for use in main router
transactions_controller = TransactionsController()
router = transactions_controller.router