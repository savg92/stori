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

    def _validate_user_data(self, user_dict: dict) -> bool:
        """Validate user data for required fields and formats."""
        required_fields = ['id', 'email', 'full_name']
        
        # Check for missing required fields
        for field in required_fields:
            if field not in user_dict or not user_dict[field]:
                logger.warning(f"  ⚠️  Missing required field '{field}' in user data")
                return False
        
        # Validate email format
        email = str(user_dict['email']).strip().lower()
        if '@' not in email or '.' not in email.split('@')[1]:
            logger.warning(f"  ⚠️  Invalid email format: {email}")
            return False
        user_dict['email'] = email
        
        # Validate full name
        full_name = str(user_dict['full_name']).strip()
        if len(full_name) < 2 or len(full_name) > 255:
            logger.warning(f"  ⚠️  Invalid full_name length: '{full_name}'")
            return False
        user_dict['full_name'] = full_name
        
        # Validate ID format
        user_id = str(user_dict['id']).strip()
        if len(user_id) < 3 or ' ' in user_id:
            logger.warning(f"  ⚠️  Invalid user ID format: '{user_id}'")
            return False
        
        # Ensure preferences is a dict
        if 'preferences' not in user_dict:
            user_dict['preferences'] = {}
        elif not isinstance(user_dict['preferences'], dict):
            logger.warning(f"  ⚠️  Invalid preferences format for {email}, setting to empty dict")
            user_dict['preferences'] = {}
        
        return True
    
    def populate_users(self) -> bool:
        """Populate users table with mock data."""
        logger.info("👥 Populating users table...")
        
        try:
            users = self.mock_service.get_mock_users()
            users_data = []
            skipped_users = 0
            
            for user in users:
                try:
                    user_dict = {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'created_at': user.created_at.isoformat(),
                        'preferences': user.preferences
                    }
                    
                    # Validate user data
                    if self._validate_user_data(user_dict):
                        users_data.append(user_dict)
                    else:
                        skipped_users += 1
                        
                except (AttributeError, ValueError, TypeError) as e:
                    logger.warning(f"  ⚠️  Skipping invalid user {getattr(user, 'email', 'unknown')}: {e}")
                    skipped_users += 1
                    continue
            
            if skipped_users > 0:
                logger.warning(f"⚠️  Skipped {skipped_users} invalid users")
            
            if not users_data:
                logger.error("❌ No valid users to insert")
                return False
            
            # Insert users with retry mechanism
            inserted_count = self._safe_batch_insert('users', users_data, 1)
            
            if inserted_count > 0:
                logger.info(f"✅ Inserted {inserted_count} users successfully!")
                if skipped_users > 0:
                    logger.info(f"📊 Process completed successfully despite {skipped_users} invalid users")
                return True
            else:
                logger.error("❌ No users were inserted")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to populate users: {e}")
            return False

    def _safe_format_date(self, date_obj, field_name: str = "date") -> str:
        """Safely format a date object to ISO format string."""
        if date_obj is None:
            raise ValueError(f"{field_name} is None")
        
        if hasattr(date_obj, 'isoformat'):
            return date_obj.isoformat()
        elif isinstance(date_obj, str):
            # Try to parse string date and convert to ISO format
            try:
                if 'T' in date_obj:  # Already in ISO format or datetime
                    return date_obj.split('T')[0]  # Extract date part
                else:
                    # Assume it's already in YYYY-MM-DD format
                    datetime.strptime(date_obj, "%Y-%m-%d")  # Validate format
                    return date_obj
            except ValueError:
                raise ValueError(f"Invalid {field_name} format: {date_obj}")
        else:
            raise ValueError(f"Invalid {field_name} type: {type(date_obj)}")
    
    def _validate_transaction_data(self, tx_dict: dict, user_email: str) -> bool:
        """Validate transaction data for required fields and data integrity."""
        required_fields = ['id', 'user_id', 'amount', 'description', 'category', 'type', 'date']
        
        # Check for missing required fields
        for field in required_fields:
            if field not in tx_dict or tx_dict[field] is None:
                logger.warning(f"  ⚠️  Missing required field '{field}' for {user_email}")
                return False
        
        # Validate field types and values
        try:
            # Check amount is a valid number
            amount = float(tx_dict['amount'])
            if not isinstance(amount, (int, float)):
                logger.warning(f"  ⚠️  Invalid amount type '{tx_dict['amount']}' for {user_email}")
                return False
            
            # Warn about zero amounts but allow them
            if amount == 0:
                logger.info(f"  ℹ️  Zero amount transaction for {user_email}: {tx_dict.get('description', 'No description')}")
            
            # Check description is not empty
            description = str(tx_dict['description']).strip()
            if not description or len(description) > 255:
                logger.warning(f"  ⚠️  Invalid description length for {user_email}: '{description[:50]}...'")
                return False
            tx_dict['description'] = description
            
            # Check category is not empty
            category = str(tx_dict['category']).strip().lower()
            if not category:
                logger.warning(f"  ⚠️  Empty category for {user_email}")
                return False
            tx_dict['category'] = category
            
            # Check transaction type is valid (handle enum serialization)
            tx_type = str(tx_dict['type']).strip().lower()
            # Handle enum format like 'transactiontype.expense' -> 'expense'
            if '.' in tx_type:
                tx_type = tx_type.split('.')[-1]
            
            if tx_type not in ['income', 'expense']:
                logger.warning(f"  ⚠️  Invalid transaction type '{tx_dict['type']}' -> '{tx_type}' for {user_email}")
                return False
            tx_dict['type'] = tx_type
            
            # Validate amount sign matches type
            if tx_type == 'expense' and amount > 0:
                tx_dict['amount'] = -abs(amount)  # Auto-correct negative expenses
            elif tx_type == 'income' and amount < 0:
                tx_dict['amount'] = abs(amount)   # Auto-correct positive income
            
            # Check ID is not empty
            if not str(tx_dict['id']).strip():
                logger.warning(f"  ⚠️  Empty transaction ID for {user_email}")
                return False
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.warning(f"  ⚠️  Data validation error for {user_email}: {e}")
            return False
    
    def _safe_batch_insert(self, table_name: str, batch: list, batch_num: int) -> int:
        """Safely insert a batch with retry mechanism and partial recovery."""
        max_retries = 3
        inserted_count = 0
        
        for attempt in range(max_retries):
            try:
                result = self.supabase.table(table_name).insert(batch).execute()
                if result.data:
                    inserted_count = len(result.data)
                    logger.info(f"  ✅ Inserted batch {batch_num}: {inserted_count} records")
                    return inserted_count
                else:
                    logger.warning(f"  ⚠️  Batch {batch_num} attempt {attempt + 1}: No data returned")
                    
            except Exception as e:
                logger.warning(f"  ⚠️  Batch {batch_num} attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    # Last attempt - try individual inserts to recover what we can
                    logger.info(f"  🔄 Attempting individual inserts for batch {batch_num}...")
                    individual_success = 0
                    
                    for i, record in enumerate(batch):
                        try:
                            single_result = self.supabase.table(table_name).insert([record]).execute()
                            if single_result.data:
                                individual_success += 1
                        except Exception as single_e:
                            logger.warning(f"    ⚠️  Failed to insert record {i}: {single_e}")
                    
                    if individual_success > 0:
                        logger.info(f"  ✅ Recovered {individual_success}/{len(batch)} records from batch {batch_num}")
                        return individual_success
                else:
                    # Wait before retry
                    import time
                    time.sleep(1 * (attempt + 1))
        
        logger.error(f"  ❌ Failed to insert batch {batch_num} after {max_retries} attempts")
        return 0

    def populate_transactions(self) -> bool:
        """Populate transactions table with mock data."""
        logger.info("💳 Populating transactions table...")
        
        try:
            users = self.mock_service.get_mock_users()
            all_transactions = []
            skipped_transactions = 0
            
            for user in users:
                try:
                    transactions = self.mock_service.get_mock_transactions(user.id)
                    logger.info(f"  Loading {len(transactions)} transactions for {user.email}")
                    
                    user_valid_transactions = 0
                    user_skipped_transactions = 0
                    
                    for tx in transactions:
                        try:
                            # Safely format transaction date
                            transaction_date = self._safe_format_date(tx.transaction_date, "transaction_date")
                            created_at = self._safe_format_date(tx.created_at, "created_at")
                            
                            tx_dict = {
                                'id': tx.id,
                                'user_id': tx.user_id,
                                'amount': float(tx.amount),
                                'description': tx.description,
                                'category': tx.category,
                                'type': tx.type,
                                'date': transaction_date,
                                'created_at': created_at
                            }
                            
                            # Validate transaction data
                            if self._validate_transaction_data(tx_dict, user.email):
                                all_transactions.append(tx_dict)
                                user_valid_transactions += 1
                            else:
                                user_skipped_transactions += 1
                                skipped_transactions += 1
                            
                        except (AttributeError, ValueError, TypeError) as e:
                            logger.warning(f"  ⚠️  Skipping invalid transaction for {user.email}: {e}")
                            user_skipped_transactions += 1
                            skipped_transactions += 1
                            continue
                    
                    logger.info(f"    ✅ {user_valid_transactions} valid, ⚠️  {user_skipped_transactions} skipped")
                    
                except Exception as e:
                    logger.warning(f"  ⚠️  Failed to load transactions for {user.email}: {e}")
                    continue
            
            # Log skipped transactions if any
            if skipped_transactions > 0:
                logger.warning(f"⚠️  Skipped {skipped_transactions} invalid transactions due to formatting issues")
            
            if not all_transactions:
                logger.error("❌ No valid transactions to insert")
                return False
            
            # Insert all transactions in batches with improved error handling
            batch_size = 50  # Reduced batch size for better reliability
            total_inserted = 0
            total_batches = (len(all_transactions) + batch_size - 1) // batch_size
            
            logger.info(f"  📦 Inserting {len(all_transactions)} transactions in {total_batches} batches...")
            
            for i in range(0, len(all_transactions), batch_size):
                batch = all_transactions[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                inserted_count = self._safe_batch_insert('transactions', batch, batch_num)
                total_inserted += inserted_count
                    
            logger.info(f"✅ Total transactions inserted: {total_inserted}")
            if skipped_transactions > 0:
                logger.info(f"📊 Process completed successfully despite {skipped_transactions} invalid transactions")
            
            # Verify we have reasonable success rate
            if total_inserted == 0:
                logger.error("❌ No transactions were successfully inserted")
                return False
            elif total_inserted < len(all_transactions) * 0.5:  # Less than 50% success
                logger.warning(f"⚠️  Low success rate: {total_inserted}/{len(all_transactions)} ({total_inserted/len(all_transactions)*100:.1f}%)")
            
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