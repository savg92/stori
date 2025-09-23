"""Services package for the expense tracker backend."""

from .ai_config_service import AIConfigService
from .session_service import SessionService
from .supabase_service import SupabaseClient, get_supabase_client
from .auth_middleware import (
    AuthMiddleware, 
    get_current_user, 
    get_optional_user,
    require_auth,
    get_user_id,
    jwt_auth
)

__all__ = [
    "AIConfigService",
    "SessionService", 
    "SupabaseClient",
    "get_supabase_client",
    "AuthMiddleware",
    "get_current_user",
    "get_optional_user", 
    "require_auth",
    "get_user_id",
    "jwt_auth"
]