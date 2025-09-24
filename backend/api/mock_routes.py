"""Mock data controller for demonstration purposes."""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from services.mock_data_service import get_mock_data_service
from populate_mock_data import mock_populator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/mock", tags=["mock-data"])


@router.get("/users")
async def get_mock_users():
    """Get all mock users."""
    try:
        mock_service = get_mock_data_service()
        users = mock_service.get_mock_users()
        
        return {
            "success": True,
            "count": len(users),
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "profile_type": user.preferences.get("profile_type", "unknown"),
                    "preferences": user.preferences
                }
                for user in users
            ]
        }
    except Exception as e:
        logger.error(f"Error getting mock users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{user_id}/transactions")
async def get_mock_user_transactions(user_id: str):
    """Get transactions for a specific mock user."""
    try:
        mock_service = get_mock_data_service()
        
        # Check if user exists
        user = mock_service.get_mock_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Mock user not found")
        
        transactions = mock_service.get_mock_transactions(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "count": len(transactions),
            "transactions": [
                {
                    "id": tx.id,
                    "amount": float(tx.amount),
                    "description": tx.description,
                    "category": tx.category,
                    "type": tx.type,
                    "date": tx.transaction_date.isoformat(),
                    "created_at": tx.created_at.isoformat()
                }
                for tx in transactions
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transactions for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/users/{user_id}/summary")
async def get_mock_user_summary(user_id: str):
    """Get financial summary for a specific mock user."""
    try:
        mock_service = get_mock_data_service()
        
        # Check if user exists
        user = mock_service.get_mock_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Mock user not found")
        
        summary = mock_service.get_mock_user_summary(user_id)
        
        return {
            "success": True,
            **summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/summary")
async def get_all_mock_summaries():
    """Get financial summaries for all mock users."""
    try:
        summary = mock_populator.get_mock_data_summary()
        return {
            "success": True,
            **summary
        }
    except Exception as e:
        logger.error(f"Error getting mock summaries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/populate")
async def populate_mock_data():
    """Populate Supabase with mock data."""
    try:
        results = await mock_populator.populate_all_mock_data()
        return {
            "success": True,
            "message": "Mock data population completed",
            **results
        }
    except Exception as e:
        logger.error(f"Error populating mock data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/clear")
async def clear_mock_data():
    """Clear all mock data from Supabase."""
    try:
        results = await mock_populator.clear_mock_data()
        return {
            "success": True,
            "message": "Mock data cleared successfully",
            **results
        }
    except Exception as e:
        logger.error(f"Error clearing mock data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")