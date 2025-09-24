"""Authentication controller for API endpoints."""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials

from services.auth_middleware import get_current_user, security
from .service import AuthService
from .schemas import (
    LoginRequest, 
    RegisterRequest, 
    TokenResponse, 
    UserProfile, 
    RefreshTokenRequest,
    PasswordResetRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    """Authenticate user and return access token."""
    try:
        auth_service = AuthService()
        return auth_service.login(login_data)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/register", response_model=TokenResponse)
def register(register_data: RegisterRequest):
    """Register new user and return access token."""
    try:
        auth_service = AuthService()
        logger.info(f"Attempting to register user: {register_data.email}")
        return auth_service.register(register_data)
        
    except ValueError as e:
        logger.error(f"Registration validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration error: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        auth_service = AuthService()
        return auth_service.refresh_token(refresh_data.refresh_token)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Token refresh endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user and invalidate token."""
    try:
        auth_service = AuthService()
        success = auth_service.logout(credentials.credentials)
        
        if success:
            return {"message": "Successfully logged out"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )
            
    except Exception as e:
        logger.error(f"Logout endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=UserProfile)
def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current authenticated user profile."""
    try:
        auth_service = AuthService()
        user_profile = auth_service.get_user_profile(current_user["user_id"])
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return user_profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user profile endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/reset-password")
def reset_password(reset_data: PasswordResetRequest):
    """Send password reset email to user."""
    try:
        auth_service = AuthService()
        success = auth_service.reset_password(reset_data.email)
        
        if success:
            return {"message": "Password reset email sent"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset failed"
            )
            
    except Exception as e:
        logger.error(f"Password reset endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/verify-token")
def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Verify if the provided token is valid."""
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "email": current_user["email"]
    }


@router.get("/test")
def test_auth():
    """Test endpoint to verify auth module is working."""
    return {
        "message": "Auth module is working",
        "endpoints": [
            "POST /api/auth/login",
            "POST /api/auth/register", 
            "POST /api/auth/refresh",
            "POST /api/auth/logout",
            "GET /api/auth/me",
            "POST /api/auth/reset-password",
            "GET /api/auth/verify-token"
        ]
    }


@router.get("/profile")
def get_user_profile(current_user: UserProfile = Depends(get_current_user)):
    """Get current user profile (protected endpoint)."""
    return {
        "status": "success",
        "user": current_user,
        "message": "Profile retrieved successfully"
    }


@router.post("/create-test-user")
def create_test_user():
    """Create a test user for development (bypasses normal registration flow)."""
    try:
        from supabase import create_client
        from config.settings import get_settings
        import uuid
        
        settings = get_settings()
        client = create_client(settings.supabase_url, settings.supabase_key)
        
        # Generate unique test user
        test_id = str(uuid.uuid4())[:8]
        test_email = f"devtest.{test_id}@stori-app.dev"
        test_password = "DevTest123!"
        
        # Try to register the user
        response = client.auth.sign_up({
            "email": test_email,
            "password": test_password,
            "options": {
                "data": {
                    "full_name": f"Dev Test User {test_id}"
                }
            }
        })
        
        result = {
            "status": "success",
            "test_user": {
                "email": test_email,
                "password": test_password,
                "user_id": response.user.id if response.user else None,
                "email_confirmed": response.user.email_confirmed_at is not None if response.user else False,
                "has_session": response.session is not None
            },
            "instructions": [
                "This test user has been created for development purposes.",
                "If email confirmation is required, check your Supabase dashboard.",
                "In production, users would need to confirm their email.",
                f"Use POST /api/auth/login with email: {test_email} and password: {test_password}"
            ]
        }
        
        if response.session:
            result["test_token"] = {
                "access_token": response.session.access_token,
                "token_type": response.session.token_type,
                "expires_in": response.session.expires_in
            }
            result["instructions"].append("User was automatically logged in - use the provided token for testing.")
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "suggestion": "Try using a different email domain or check Supabase project settings."
        }