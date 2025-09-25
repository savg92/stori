#!/usr/bin/env python3
"""
Analyze transaction data distribution across users.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def analyze_user_transactions():
    """Check transaction counts and data for each user."""
    
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
    
    print('📊 Transaction Analysis per User')
    print('=' * 50)
    
    # Get all users
    users = supabase.table('users').select('*').execute().data
    
    for user in users:
        user_id = user['id']
        email = user['email']
        name = user['full_name']
        
        print(f'{user_id}: {name} ({email})')
        
        # Count transactions for this user
        transactions_result = supabase.table('transactions').select('*', count='exact').eq('user_id', user_id).execute()
        count = transactions_result.count
        
        print(f'  📈 Transaction count: {count}')
        
        if count > 0:
            # Get sample transactions
            sample = supabase.table('transactions').select('*').eq('user_id', user_id).limit(3).execute().data
            print(f'  💰 Sample transactions:')
            for t in sample:
                print(f'    - {t["date"]}: {t["type"]} ${t["amount"]} ({t["category"]})')
                
            # Get balance summary
            income_result = supabase.table('transactions').select('amount').eq('user_id', user_id).eq('type', 'income').execute()
            expense_result = supabase.table('transactions').select('amount').eq('user_id', user_id).eq('type', 'expense').execute()
            
            total_income = sum(float(t['amount']) for t in income_result.data)
            total_expenses = sum(float(t['amount']) for t in expense_result.data)
            balance = total_income - total_expenses
            
            print(f'  💵 Total Income: ${total_income:,.2f}')
            print(f'  💸 Total Expenses: ${total_expenses:,.2f}')
            print(f'  🏦 Balance: ${balance:,.2f}')
        else:
            print(f'  ⚠️  No transactions found')
        print()

if __name__ == "__main__":
    analyze_user_transactions()