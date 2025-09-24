"""Authentication middleware for Supabase JWT tokens."""

import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
import jwt
from datetime import datetime, timezone

from config.settings import get_settings

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer()


class AuthenticationError(Exception):
    """Custom authentication error."""
    pass


class AuthMiddleware:
    """Authentication middleware for Supabase JWT tokens."""
    
    def __init__(self):
        """Initialize auth middleware."""
        self._settings = get_settings()
        self._supabase = create_client(
            self._settings.supabase_url,
            self._settings.supabase_key
        )
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            # Set the token for the client and get user
            response = self._supabase.auth.get_user(token)
            
            if not response.user:
                raise AuthenticationError("Invalid token")
            
            return {
                "user_id": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata or {},
                "app_metadata": response.user.app_metadata or {}
            }
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise AuthenticationError(f"Token verification failed: {str(e)}")
    
    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """Get current authenticated user from JWT token."""
        try:
            token = credentials.credentials
            user_data = await self.verify_token(token)
            return user_data
            
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def get_optional_user(
        self, 
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[Dict[str, Any]]:
        """Get current user if authenticated, otherwise return None."""
        if not credentials:
            return None
        
        try:
            return await self.get_current_user(credentials)
        except HTTPException:
            return None


# Global auth middleware instance
auth_middleware = AuthMiddleware()

# Dependency functions for FastAPI
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user."""
    return await auth_middleware.get_current_user(credentials)

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """FastAPI dependency to get current user if authenticated."""
    return await auth_middleware.get_optional_user(credentials)

def require_auth(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """FastAPI dependency that requires authentication."""
    return user

def get_user_id(user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """FastAPI dependency to get current user ID."""
    return user["user_id"]


# Alternative JWT verification (if needed for custom tokens)
class JWTAuth:
    """Custom JWT authentication handler."""
    
    def __init__(self):
        """Initialize JWT auth."""
        self._settings = get_settings()
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a new access token."""
        try:
            to_encode = data.copy()
            expire = datetime.now(timezone.utc).timestamp() + (
                self._settings.jwt_access_token_expire_minutes * 60
            )
            to_encode.update({"exp": expire})
            
            encoded_jwt = jwt.encode(
                to_encode, 
                self._settings.jwt_secret_key, 
                algorithm=self._settings.jwt_algorithm
            )
            return encoded_jwt
            
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode custom JWT token."""
        try:
            payload = jwt.decode(
                token, 
                self._settings.jwt_secret_key, 
                algorithms=[self._settings.jwt_algorithm]
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.JWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")


# Global JWT auth instance
jwt_auth = JWTAuth()