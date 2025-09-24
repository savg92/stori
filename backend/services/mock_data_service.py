"""Mock data service for loading and managing demo users and transactions."""

import json
import os
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

from core.models import UserProfile, Transaction, TransactionCreate


class MockDataService:
    """Service for loading and managing mock user data."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self._users_cache: Optional[List[UserProfile]] = None
        self._transactions_cache: Optional[Dict[str, List[Transaction]]] = None
    
    def _load_json_file(self, filename: str) -> List[Dict]:
        """Load and parse a JSON file from the data directory."""
        file_path = self.data_dir / filename
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Mock data file {filename} not found")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename}: {e}")
            return []
    
    def get_mock_users(self) -> List[UserProfile]:
        """Get all mock users."""
        if self._users_cache is None:
            users_data = self._load_json_file("mock_users.json")
            self._users_cache = []
            
            for user_data in users_data:
                user = UserProfile(
                    id=user_data["id"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    created_at=datetime.now(),
                    preferences=user_data.get("preferences", {})
                )
                self._users_cache.append(user)
        
        return self._users_cache
    
    def get_mock_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Get a specific mock user by ID."""
        users = self.get_mock_users()
        return next((user for user in users if user.id == user_id), None)
    
    def get_mock_transactions(self, user_id: str) -> List[Transaction]:
        """Get all mock transactions for a specific user."""
        if self._transactions_cache is None:
            self._transactions_cache = {}
            
            # Load transactions for each user
            users = self.get_mock_users()
            for user in users:
                # Map user ID to simplified transaction filename
                # user_1_young_professional -> user_1_transactions.json
                if user.id.startswith('user_'):
                    user_number = user.id.split('_')[1]  # Extract number
                    filename = f"user_{user_number}_transactions.json"
                else:
                    filename = f"{user.id}_transactions.json"
                
                transactions_data = self._load_json_file(filename)
                
                transactions = []
                for tx_data in transactions_data:
                    try:
                        # Convert date string to date object
                        tx_date = datetime.strptime(tx_data["date"], "%Y-%m-%d").date()
                        
                        # Handle amount based on type - expenses should be negative, income positive
                        amount_value = Decimal(str(tx_data["amount"]))
                        if tx_data["type"] == "expense" and amount_value > 0:
                            amount_value = -amount_value
                        elif tx_data["type"] == "income" and amount_value < 0:
                            amount_value = abs(amount_value)
                        
                        # Create transaction object
                        transaction = Transaction(
                            id=f"{user.id}_{tx_data['date']}_{len(transactions)}",
                            user_id=user.id,
                            amount=amount_value,
                            description=tx_data["description"],
                            category=tx_data["category"],
                            type=tx_data["type"],
                            date=tx_date,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                        transactions.append(transaction)
                    except (ValueError, KeyError) as e:
                        print(f"Error processing transaction for {user.id}: {e}")
                        continue
                
                self._transactions_cache[user.id] = transactions
        
        return self._transactions_cache.get(user_id, [])
    
    def get_all_mock_transactions(self) -> Dict[str, List[Transaction]]:
        """Get all transactions for all mock users."""
        users = self.get_mock_users()
        all_transactions = {}
        
        for user in users:
            all_transactions[user.id] = self.get_mock_transactions(user.id)
        
        return all_transactions
    
    def get_mock_user_summary(self, user_id: str) -> Dict:
        """Get a summary of a mock user's financial data."""
        user = self.get_mock_user_by_id(user_id)
        if not user:
            return {}
        
        transactions = self.get_mock_transactions(user_id)
        
        total_income = sum(tx.amount for tx in transactions if tx.type == "income")
        total_expenses = sum(tx.amount for tx in transactions if tx.type == "expense")
        net_income = total_income - total_expenses
        
        # Category breakdown for expenses
        expense_categories = {}
        for tx in transactions:
            if tx.type == "expense":
                if tx.category not in expense_categories:
                    expense_categories[tx.category] = Decimal('0')
                expense_categories[tx.category] += tx.amount
        
        return {
            "user": user,
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "net_income": float(net_income),
            "transaction_count": len(transactions),
            "expense_categories": {k: float(v) for k, v in expense_categories.items()},
            "profile_type": user.preferences.get("profile_type", "unknown")
        }
    
    def get_all_mock_summaries(self) -> List[Dict]:
        """Get financial summaries for all mock users."""
        users = self.get_mock_users()
        return [self.get_mock_user_summary(user.id) for user in users]
    
    def clear_cache(self):
        """Clear the cached data to force reload."""
        self._users_cache = None
        self._transactions_cache = None
    
    def is_mock_user(self, user_id: str) -> bool:
        """Check if a given user ID is a mock user."""
        users = self.get_mock_users()
        return any(user.id == user_id for user in users)


# Global instance for easy access
mock_data_service = MockDataService()


def get_mock_data_service() -> MockDataService:
    """Get the global mock data service instance."""
    return mock_data_service