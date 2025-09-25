#!/usr/bin/env python3
"""Check hosted database content."""

import os
import asyncio
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

async def check_database():
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        return False
        
    supabase = create_client(supabase_url, service_key)
    
    print("🔍 Checking hosted Supabase database content...")
    print("=" * 50)
    
    # Check users
    users_result = supabase.table('users').select('*').execute()
    print(f'👥 Users in hosted database: {len(users_result.data)}')
    for user in users_result.data:
        print(f'  • {user["email"]} ({user["id"]})')
    
    print()
    
    # Check transactions
    transactions_result = supabase.table('transactions').select('*').execute()
    print(f'💳 Total transactions in hosted database: {len(transactions_result.data)}')
    
    print()
    
    # Check transactions per user
    print("📊 Transactions per user:")
    for user in users_result.data:
        user_tx = supabase.table('transactions').select('*').eq('user_id', user['id']).execute()
        print(f'  • {user["email"]}: {len(user_tx.data)} transactions')
    
    print()
    
    if len(users_result.data) > 0 and len(transactions_result.data) > 0:
        print("✅ Hosted database is populated with users and transactions!")
        print("🎉 Database migration completed successfully!")
    else:
        print("⚠️  Database appears to be empty or incomplete")
        
    return len(users_result.data) > 0 and len(transactions_result.data) > 0

if __name__ == "__main__":
    asyncio.run(check_database())