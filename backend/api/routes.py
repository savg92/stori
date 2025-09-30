"""API routes for the Stori expense tracker application."""

import logging
from fastapi import APIRouter

# Import modular controllers
from src.modules.transactions.transactions_controller import router as transactions_router
from src.modules.expenses.controller import router as expenses_router
from src.modules.timeline.controller import router as timeline_router
from src.modules.ai.controller import router as ai_router
from src.modules.auth.controller import router as auth_router
from api.mock_routes import router as mock_router

logger = logging.getLogger(__name__)

# Create main router
router = APIRouter()


@router.get("/health")
async def health_check():
    """Application health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "modules": [
            "auth",
            "transactions",
            "expenses", 
            "timeline",
            "ai",
        ]
    }

# Include all module routers
router.include_router(auth_router)
router.include_router(transactions_router)
router.include_router(expenses_router)
router.include_router(timeline_router)
router.include_router(ai_router)
router.include_router(mock_router)