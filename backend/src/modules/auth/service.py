"""Authentication service for Supa            user_profile = UserProfile(
                id=response.user.id,
                email=response.user.email or "",
                full_name=response.user.user_metadata.get("full_name", ""),
                avatar_url=response.user.user_metadata.get("avatar_url"),
                created_at=response.user.created_at.isoformat() if response.user.created_at else "",
                updated_at=response.user.updated_at.isoformat() if response.user.updated_at else ""
            )egration."""

import logging
from typing import Dict, Any, Optional
from supabase import Client
from gotrue.errors import AuthError

from services.supabase_service import get_supabase_client
from .schemas import LoginRequest, RegisterRequest, UserProfile, TokenResponse

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management."""
    
    def __init__(self):
        """Initialize auth service."""
        # Get the underlying Supabase client directly
        supabase_wrapper = get_supabase_client()
        self.supabase: Client = supabase_wrapper.client
    
    def login(self, login_data: LoginRequest) -> TokenResponse:
        """Login user and return tokens."""
        try:
            # Sign in with Supabase
            response = self.supabase.auth.sign_in_with_password({
                "email": login_data.email,
                "password": login_data.password
            })
            
            if not response.session:
                raise AuthError("Login failed - no session created")
            
            user_profile = UserProfile(
                id=response.user.id,
                email=response.user.email or "",
                full_name=response.user.user_metadata.get("full_name", ""),
                avatar_url=response.user.user_metadata.get("avatar_url"),
                created_at=response.user.created_at.isoformat() if response.user.created_at else "",
                updated_at=response.user.updated_at.isoformat() if response.user.updated_at else ""
            )
            
            return TokenResponse(
                access_token=response.session.access_token,
                token_type="bearer",
                expires_in=response.session.expires_in or 3600,
                refresh_token=response.session.refresh_token,
                user=user_profile
            )
            
        except AuthError as e:
            logger.error(f"Login failed: {e}")
            raise ValueError(f"Login failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise ValueError(f"Login failed: {str(e)}")
    
    def register(self, register_data: RegisterRequest) -> TokenResponse:
        """Register new user and return tokens."""
        try:
            # Sign up with Supabase
            response = self.supabase.auth.sign_up({
                "email": register_data.email,
                "password": register_data.password,
                "options": {
                    "data": {
                        "full_name": register_data.full_name
                    }
                }
            })
            
            if not response.user:
                raise AuthError("Registration failed - no user returned")
            
            user_profile = UserProfile(
                id=response.user.id,
                email=response.user.email or "",
                full_name=register_data.full_name,
                avatar_url=response.user.user_metadata.get("avatar_url"),
                created_at=response.user.created_at.isoformat() if response.user.created_at else "",
                updated_at=response.user.updated_at.isoformat() if response.user.updated_at else ""
            )
            
            # If session exists, return tokens (immediate login)
            if response.session:
                logger.info(f"User registered and logged in: {response.user.email}")
                return TokenResponse(
                    access_token=response.session.access_token,
                    token_type="bearer",
                    expires_in=response.session.expires_in or 3600,
                    refresh_token=response.session.refresh_token,
                    user=user_profile
                )
            else:
                # Email confirmation required - return empty tokens but successful registration
                logger.info(f"User registered, email confirmation required: {response.user.email}")
                return TokenResponse(
                    access_token="EMAIL_CONFIRMATION_REQUIRED",
                    token_type="bearer",
                    expires_in=0,
                    refresh_token=None,
                    user=user_profile
                )
            
        except AuthError as e:
            logger.error(f"Registration failed: {e}")
            raise ValueError(f"Registration failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            raise ValueError(f"Registration failed: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if not response.user or not response.session:
                raise AuthError("Invalid refresh token")
            
            user_profile = UserProfile(
                id=response.user.id,
                email=response.user.email or "",
                full_name=response.user.user_metadata.get("full_name"),
                avatar_url=response.user.user_metadata.get("avatar_url"),
                created_at=response.user.created_at,
                updated_at=response.user.updated_at
            )
            
            return TokenResponse(
                access_token=response.session.access_token,
                token_type="bearer",
                expires_in=response.session.expires_in or 3600,
                refresh_token=response.session.refresh_token,
                user=user_profile
            )
            
        except AuthError as e:
            logger.error(f"Token refresh failed: {e}")
            raise ValueError(f"Token refresh failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {e}")
            raise ValueError("Token refresh failed due to server error")
    
    def logout(self, access_token: str) -> bool:
        """Logout user and invalidate token."""
        try:
            # Set the session for the client
            self.supabase.auth.set_session(access_token, "")
            
            # Sign out
            self.supabase.auth.sign_out()
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID."""
        try:
            response = self.supabase.auth.get_user()
            
            if not response.user:
                return None
            
            return UserProfile(
                id=response.user.id,
                email=response.user.email or "",
                full_name=response.user.user_metadata.get("full_name"),
                avatar_url=response.user.user_metadata.get("avatar_url"),
                created_at=response.user.created_at,
                updated_at=response.user.updated_at
            )
            
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    def reset_password(self, email: str) -> bool:
        """Send password reset email."""
        try:
            response = self.supabase.auth.reset_password_for_email(email)
            return True
            
        except AuthError as e:
            logger.error(f"Password reset failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during password reset: {e}")
            return False