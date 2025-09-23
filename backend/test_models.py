"""Test script to validate that our models work with the mock JSON data."""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

# Add the parent directory to the path so we can import our models
import sys
sys.path.append('/Users/savg/Desktop/stori/backend')

from core.models import TransactionCreate, TransactionType


def test_models_with_mock_data():
    """Test that our Pydantic models can parse the mock JSON data."""
    
    # Load the mock data
    mock_file_path = Path('/Users/savg/Desktop/stori/mock_expense_and_income.json')
    with open(mock_file_path, 'r') as f:
        mock_transactions = json.load(f)
    
    print(f"Testing {len(mock_transactions)} transactions from mock data...")
    
    successful_parses = 0
    errors = []
    
    for i, transaction_data in enumerate(mock_transactions):  # Test all transactions
        try:
            # Convert the JSON data to match our model structure
            model_data = {
                "amount": Decimal(str(transaction_data["amount"])),
                "description": transaction_data["description"],
                "category": transaction_data["category"],
                "type": transaction_data["type"],
                "date": transaction_data["date"]
            }
            
            # Try to create a TransactionCreate instance
            transaction = TransactionCreate(**model_data)
            print(f"✅ Transaction {i+1}: {transaction.type.value} ${abs(transaction.amount)} - {transaction.category}")
            successful_parses += 1
            
        except Exception as e:
            errors.append(f"❌ Transaction {i+1}: {str(e)}")
            print(f"❌ Transaction {i+1}: {str(e)}")
    
    print(f"\nResults: {successful_parses}/{len(mock_transactions)} transactions parsed successfully")
    
    if errors:
        print("\nErrors found:")
        for error in errors:
            print(error)
        return False
    
    return True


if __name__ == "__main__":
    success = test_models_with_mock_data()
    if success:
        print("\n🎉 All models are compatible with the mock JSON data!")
    else:
        print("\n⚠️  Some models need adjustments to work with the mock data.")