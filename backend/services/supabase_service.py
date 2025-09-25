"""Supabase client configuration and database operations."""

import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from postgrest.exceptions import APIError

from config.settings import get_settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase client wrapper for database operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self._client: Optional[Client] = None
        self._settings = get_settings()
        
    @property
    def client(self) -> Client:
        """Get or create Supabase client instance."""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    def _create_client(self) -> Client:
        """Create a new Supabase client."""
        try:
            options = ClientOptions(
                auto_refresh_token=True,
                persist_session=True,
            )
            
            client = create_client(
                supabase_url=self._settings.supabase_url,
                supabase_key=self._settings.supabase_key,
                options=options
            )
            
            logger.info("Supabase client initialized successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check Supabase connection health."""
        try:
            # Simple query to test connection
            response = self.client.table('users').select('count').execute()
            return {
                "status": "healthy",
                "connection": "active",
                "response_time": "fast"
            }
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return {
                "status": "unhealthy",
                "connection": "failed", 
                "error": str(e)
            }
    
    # Transaction operations
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new transaction."""
        try:
            response = await self.client.table('transactions').insert(transaction_data).execute()
            return response.data[0] if response.data else {}
        except APIError as e:
            logger.error(f"Failed to create transaction: {e}")
            raise
    
    async def get_transactions(
        self, 
        user_id: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get transactions for a user with optional filters and pagination."""
        try:
            query = self.client.table('transactions').select('*').eq('user_id', user_id)
            
            if filters:
                if 'start_date' in filters:
                    query = query.gte('transaction_date', filters['start_date'])
                if 'end_date' in filters:
                    query = query.lte('transaction_date', filters['end_date'])
                if 'transaction_type' in filters:
                    query = query.eq('type', filters['transaction_type'])
                if 'category' in filters:
                    query = query.eq('category', filters['category'])
            
            # Add pagination
            if limit is not None:
                query = query.limit(limit)
            if offset is not None:
                query = query.offset(offset)
            
            # Order by transaction_date desc for consistent pagination
            query = query.order('transaction_date', desc=True)
            
            response = await query.execute()
            return response.data or []
            
        except APIError as e:
            logger.error(f"Failed to get transactions: {e}")
            raise
    
    async def update_transaction(
        self, 
        transaction_id: str, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing transaction."""
        try:
            response = await self.client.table('transactions')\
                .update(update_data)\
                .eq('id', transaction_id)\
                .execute()
            return response.data[0] if response.data else {}
        except APIError as e:
            logger.error(f"Failed to update transaction: {e}")
            raise
    
    async def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction."""
        try:
            await self.client.table('transactions')\
                .delete()\
                .eq('id', transaction_id)\
                .execute()
            return True
        except APIError as e:
            logger.error(f"Failed to delete transaction: {e}")
            raise
    
    # Expense summary operations
    async def get_expense_summary(
        self, 
        user_id: str, 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """Get expense summary for a date range."""
        try:
            # Get transactions in date range
            transactions = await self.get_transactions(
                user_id, 
                {'start_date': start_date, 'end_date': end_date}
            )
            
            # Calculate summaries (this could be moved to a dedicated service)
            total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
            total_expenses = sum(abs(t['amount']) for t in transactions if t['type'] == 'expense')
            
            return {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_income': total_income - total_expenses,
                'period_start': start_date,
                'period_end': end_date,
                'transaction_count': len(transactions)
            }
            
        except Exception as e:
            logger.error(f"Failed to get expense summary: {e}")
            raise
    
    # User operations
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information."""
        try:
            response = await self.client.table('users')\
                .select('*')\
                .eq('id', user_id)\
                .execute()
            return response.data[0] if response.data else None
        except APIError as e:
            logger.error(f"Failed to get user profile: {e}")
            raise
    
    async def create_user_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user profile."""
        try:
            response = await self.client.table('users').insert(user_data).execute()
            return response.data[0] if response.data else {}
        except APIError as e:
            logger.error(f"Failed to create user profile: {e}")
            raise


# Global instance
_supabase_client: Optional[SupabaseClient] = None

def get_supabase_client() -> SupabaseClient:
    """Get global Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client