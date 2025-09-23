"""Session management service for financial advice conversations."""

import logging
import threading
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta


class SessionService:
    """Service for managing user sessions and chat histories."""
    
    def __init__(self, max_history_length: int = 10, session_timeout_hours: int = 24):
        self.chat_histories: Dict[str, List[Tuple[str, str]]] = {}
        self.session_timestamps: Dict[str, datetime] = {}
        self.session_lock = threading.Lock()
        self.max_history_length = max_history_length
        self.session_timeout = timedelta(hours=session_timeout_hours)
    
    def get_chat_history(self, session_id: str) -> List[Tuple[str, str]]:
        """Get chat history for a session."""
        with self.session_lock:
            self._cleanup_expired_sessions()
            return self.chat_histories.get(session_id, [])
    
    def add_to_history(self, session_id: str, question: str, answer: str) -> None:
        """Add a question-answer pair to session history."""
        with self.session_lock:
            if session_id not in self.chat_histories:
                self.chat_histories[session_id] = []
            
            # Add new conversation
            self.chat_histories[session_id].append((question, answer))
            
            # Trim history if too long
            if len(self.chat_histories[session_id]) > self.max_history_length:
                self.chat_histories[session_id] = self.chat_histories[session_id][-self.max_history_length:]
            
            # Update session timestamp
            self.session_timestamps[session_id] = datetime.now()
            
            logging.info(f"Updated chat history for session {session_id}. Length: {len(self.chat_histories[session_id])}")
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session's history."""
        with self.session_lock:
            if session_id in self.chat_histories:
                del self.chat_histories[session_id]
                if session_id in self.session_timestamps:
                    del self.session_timestamps[session_id]
                logging.info(f"Cleared session: {session_id}")
                return True
            return False
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        with self.session_lock:
            self._cleanup_expired_sessions()
            return list(self.chat_histories.keys())
    
    def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions (internal method, should be called with lock)."""
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, timestamp in self.session_timestamps.items()
            if current_time - timestamp > self.session_timeout
        ]
        
        for session_id in expired_sessions:
            if session_id in self.chat_histories:
                del self.chat_histories[session_id]
            if session_id in self.session_timestamps:
                del self.session_timestamps[session_id]
            logging.info(f"Cleaned up expired session: {session_id}")
    
    def get_session_stats(self) -> Dict[str, int]:
        """Get session statistics."""
        with self.session_lock:
            self._cleanup_expired_sessions()
            total_conversations = sum(len(history) for history in self.chat_histories.values())
            return {
                "active_sessions": len(self.chat_histories),
                "total_conversations": total_conversations,
                "max_history_length": self.max_history_length
            }