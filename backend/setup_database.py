#!/usr/bin/env python3
"""
Complete database setup script.
Creates schema and populates with mock data in one step.
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import List
from dotenv import load_dotenv

from supabase import create_client, Client
from services.mock_data_service import MockDataService
from core.models import UserProfile, Transaction

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseSetup:
    """Complete database setup including schema creation and data population."""
    
    def __init__(self):
        """Initialize database setup."""
        # Get environment variables
        supabase_url = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
        
        # Use service role key for data seeding to bypass RLS
        # For local development, this is the default service role key
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        self.supabase: Client = create_client(
            supabase_url=supabase_url,
            supabase_key=service_role_key  # Use service role instead of anon key
        )
        self.mock_service = MockDataService()
        
        logger.info(f"🔧 Using Supabase URL: {supabase_url}")
        logger.info("🔑 Using SERVICE ROLE key for data seeding (bypasses RLS)")

    def create_schema(self) -> bool:
        """Create the database schema using SQL commands."""
        logger.info("🗄️ Creating database schema...")
        
        # Schema SQL commands
        schema_commands = [
            # Drop existing tables if they exist
            "DROP TABLE IF EXISTS public.transactions CASCADE;",
            "DROP TABLE IF EXISTS public.users CASCADE;",
            
            # Create users table
            """
            CREATE TABLE public.users (
                id TEXT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                preferences JSONB DEFAULT '{}'::jsonb
            );
            """,
            
            # Create transactions table
            """
            CREATE TABLE public.transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
                amount DECIMAL(15,2) NOT NULL,
                description TEXT NOT NULL,
                category VARCHAR(100) NOT NULL,
                type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
                date DATE NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            """,
            
            # Create indexes for better performance
            "CREATE INDEX idx_transactions_user_id ON public.transactions(user_id);",
            "CREATE INDEX idx_transactions_date ON public.transactions(date);",
            "CREATE INDEX idx_transactions_type ON public.transactions(type);",
            "CREATE INDEX idx_transactions_category ON public.transactions(category);",
            
            # Create updated_at trigger function
            """
            CREATE OR REPLACE FUNCTION public.update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """,
            
            # Create triggers
            """
            CREATE TRIGGER update_users_updated_at
                BEFORE UPDATE ON public.users
                FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
            """,
            
            """
            CREATE TRIGGER update_transactions_updated_at
                BEFORE UPDATE ON public.transactions
                FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
            """
        ]
        
        try:
            for i, command in enumerate(schema_commands, 1):
                logger.info(f"  Executing schema command {i}/{len(schema_commands)}...")
                result = self.supabase.rpc('exec_sql', {'sql': command}).execute()
                if hasattr(result, 'data') and result.data:
                    logger.info(f"    ✅ Command {i} executed successfully")
                    
            logger.info("✅ Database schema created successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create database schema: {e}")
            return False

    def populate_users(self) -> bool:
        """Populate users table with mock data."""
        logger.info("👥 Populating users table...")
        
        try:
            users = self.mock_service.get_mock_users()
            users_data = []
            
            for user in users:
                user_dict = {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'created_at': user.created_at.isoformat(),
                    'preferences': user.preferences
                }
                users_data.append(user_dict)
            
            # Insert users
            result = self.supabase.table('users').insert(users_data).execute()
            
            if result.data:
                logger.info(f"✅ Inserted {len(result.data)} users successfully!")
                for user in result.data:
                    logger.info(f"  • {user['email']} ({user['id']})")
                return True
            else:
                logger.error("❌ No users were inserted")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to populate users: {e}")
            return False

    def populate_transactions(self) -> bool:
        """Populate transactions table with mock data."""
        logger.info("💳 Populating transactions table...")
        
        try:
            users = self.mock_service.get_mock_users()
            all_transactions = []
            
            for user in users:
                transactions = self.mock_service.get_mock_transactions(user.id)
                logger.info(f"  Loading {len(transactions)} transactions for {user.email}")
                
                for tx in transactions:
                    tx_dict = {
                        'id': tx.id,
                        'user_id': tx.user_id,
                        'amount': float(tx.amount),
                        'description': tx.description,
                        'category': tx.category,
                        'type': tx.type,
                        'date': tx.transaction_date.isoformat(),
                        'created_at': tx.created_at.isoformat()
                    }
                    all_transactions.append(tx_dict)
            
            # Insert all transactions in batches (Supabase has limits)
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(all_transactions), batch_size):
                batch = all_transactions[i:i + batch_size]
                result = self.supabase.table('transactions').insert(batch).execute()
                
                if result.data:
                    total_inserted += len(result.data)
                    logger.info(f"  ✅ Inserted batch {i//batch_size + 1}: {len(result.data)} transactions")
                else:
                    logger.error(f"  ❌ Failed to insert batch {i//batch_size + 1}")
                    
            logger.info(f"✅ Total transactions inserted: {total_inserted}")
            return total_inserted > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to populate transactions: {e}")
            return False

    def verify_data(self) -> bool:
        """Verify that data was inserted correctly."""
        logger.info("🔍 Verifying database data...")
        
        try:
            # Check users count
            users_result = self.supabase.table('users').select('count').execute()
            users_count = len(users_result.data) if users_result.data else 0
            logger.info(f"  Users in database: {users_count}")
            
            # Check transactions count
            transactions_result = self.supabase.table('transactions').select('count').execute()
            transactions_count = len(transactions_result.data) if transactions_result.data else 0
            logger.info(f"  Transactions in database: {transactions_count}")
            
            # Check specific user data
            user1_result = self.supabase.table('users').select('*').eq('id', 'user_1_young_professional').execute()
            if user1_result.data:
                user1 = user1_result.data[0]
                logger.info(f"  User 1: {user1['email']} - {user1['full_name']}")
                
                # Check user 1 transactions (should have your mock_expense_and_income.json data)
                user1_tx_result = self.supabase.table('transactions').select('*').eq('user_id', 'user_1_young_professional').execute()
                user1_tx_count = len(user1_tx_result.data) if user1_tx_result.data else 0
                logger.info(f"  User 1 transactions: {user1_tx_count}")
                
                if user1_tx_result.data:
                    # Show a few sample transactions
                    for tx in user1_tx_result.data[:3]:
                        logger.info(f"    • {tx['date']}: ${tx['amount']} - {tx['description']} ({tx['type']})")
            
            success = users_count > 0 and transactions_count > 0
            if success:
                logger.info("✅ Database verification successful!")
            else:
                logger.error("❌ Database verification failed!")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to verify data: {e}")
            return False

    async def setup_complete_database(self) -> bool:
        """Complete database setup process."""
        logger.info("🚀 Starting complete database setup...")
        
        # Step 1: Create schema (skip for now due to RPC limitations)
        logger.info("⚠️  Schema creation skipped - please run schema.sql manually in Supabase SQL Editor")
        
        # Step 2: Populate users
        if not self.populate_users():
            logger.error("❌ Failed to populate users - stopping setup")
            return False
            
        # Step 3: Populate transactions
        if not self.populate_transactions():
            logger.error("❌ Failed to populate transactions - stopping setup")
            return False
            
        # Step 4: Verify data
        if not self.verify_data():
            logger.error("❌ Data verification failed - setup incomplete")
            return False
            
        logger.info("🎉 Complete database setup finished successfully!")
        logger.info(f"📊 Database now contains mock users and transactions")
        logger.info(f"🧪 User 1 now uses your mock_expense_and_income.json data")
        return True


async def main():
    """Main setup function."""
    setup = DatabaseSetup()
    
    print("🗄️ Stori Database Setup")
    print("=" * 50)
    print()
    print("⚠️  IMPORTANT: Before running this script:")
    print("   1. Open your Supabase project SQL Editor")
    print("   2. Run the schema.sql file to create tables")
    print("   3. Then run this script to populate data")
    print()
    
    response = input("Have you run the schema.sql file in Supabase? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Please run schema.sql in Supabase first, then re-run this script")
        return False
        
    success = await setup.setup_complete_database()
    
    if success:
        print()
        print("🎉 SUCCESS! Your database is now populated with mock data")
        print("📱 You can now test your FastAPI endpoints")
        print("🔍 Check your Supabase dashboard to see the data")
    else:
        print()
        print("❌ Setup failed. Check the logs above for details.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())