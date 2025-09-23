"""API routes for the Stori expense tracker application."""

import logging
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

from config.settings import get_settings

# Import modular controllers
from src.modules.transactions.transactions_controller import router as transactions_router
from src.modules.expenses.controller import router as expenses_router
from src.modules.timeline.controller import router as timeline_router
from src.modules.ai.controller import router as ai_router

logger = logging.getLogger(__name__)

# Create main router
router = APIRouter()

# Security scheme
security = HTTPBearer()

# Include all module routers
router.include_router(transactions_router)
router.include_router(expenses_router)
router.include_router(timeline_router)
router.include_router(ai_router)


async def get_current_user(token: str = Depends(security)) -> Dict:
    """Extract user information from JWT token."""
    try:
        settings = get_settings()
        payload = jwt.decode(
            token.credentials, 
            settings.supabase_jwt_secret, 
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/health")
async def health_check():
    """Application health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "modules": [
            "transactions",
            "expenses", 
            "timeline",
            "ai"
        ]
    }