"""Automated database schema setup for Stori."""

import os
import logging
import subprocess
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AutoSchemaSetup:
    """Automated schema setup for Stori database."""
    
    def __init__(self):
        """Initialize with Supabase connection info from environment."""
        self.schema_file = Path(__file__).parent / "schema.sql"
        
        # Load from environment variables
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        
        # PostgreSQL direct connection for schema setup (local Supabase)
        self.db_host = "127.0.0.1"
        self.db_port = "54322"  # Supabase local PostgreSQL port
        self.db_name = "postgres"
        self.db_user = "postgres"
        self.db_password = "postgres"
        
        # Initialize Supabase client for verification
        self.supabase: Client = create_client(
            self.supabase_url,
            self.supabase_anon_key
        )
        
        logger.info(f"🔧 Using Supabase URL: {self.supabase_url}")
    
    def check_supabase_status(self) -> bool:
        """Check if local Supabase is running."""
        try:
            # Try a simple health check by making a basic REST request
            import requests
            response = requests.get(f"{self.supabase_url}/rest/v1/", timeout=5)
            if response.status_code in [200, 400, 404]:  # These indicate Supabase is running
                logger.info("✅ Local Supabase is running and accessible")
                return True
            else:
                logger.error(f"❌ Unexpected response from Supabase: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to local Supabase: {e}")
            logger.error("Please make sure local Supabase is running with 'supabase start'")
            return False
    
    def run_sql_file(self, sql_file_path: Path) -> bool:
        """Run SQL commands from a file using psql."""
        try:
            if not sql_file_path.exists():
                logger.error(f"SQL file not found: {sql_file_path}")
                return False
            
            logger.info(f"📂 Executing SQL file: {sql_file_path}")
            
            # Build psql command
            psql_cmd = [
                "psql",
                "-h", self.db_host,
                "-p", self.db_port,
                "-U", self.db_user,
                "-d", self.db_name,
                "-f", str(sql_file_path),
                "-v", "ON_ERROR_STOP=1"  # Stop on first error
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_password
            
            # Execute the command
            result = subprocess.run(
                psql_cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ SQL file executed successfully!")
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"❌ SQL execution failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running SQL file: {e}")
            return False
    
    def setup_schema(self) -> bool:
        """Set up the database schema automatically."""
        try:
            logger.info("🗄️ Starting automated schema setup...")
            
            # First, check if Supabase is running
            if not self.check_supabase_status():
                return False
            
            # Check if schema file exists
            if not self.schema_file.exists():
                logger.error(f"Schema file not found: {self.schema_file}")
                return False
            
            logger.info(f"📂 Reading schema from: {self.schema_file}")
            
            # Execute the schema file
            success = self.run_sql_file(self.schema_file)
            
            if success:
                logger.info("✅ Schema setup completed successfully!")
                return True
            else:
                logger.error("❌ Schema setup failed!")
                return False
                
        except Exception as e:
            logger.error(f"Error in schema setup: {e}")
            return False
    
    def verify_tables(self) -> bool:
        """Verify that required tables were created using Supabase client."""
        try:
            import time
            
            # Wait a moment for schema cache to refresh
            logger.info("⏳ Waiting for schema cache to refresh...")
            time.sleep(2)
            
            required_tables = ['users', 'transactions']
            
            for table in required_tables:
                try:
                    # Try to query the table structure using Supabase client
                    result = self.supabase.table(table).select("*").limit(1).execute()
                    logger.info(f"✅ Table '{table}' exists and is accessible")
                except Exception as e:
                    # If Supabase client fails, try direct PostgreSQL query
                    logger.warning(f"⚠️ Supabase client verification failed for '{table}', trying direct query...")
                    if self._verify_table_directly(table):
                        logger.info(f"✅ Table '{table}' verified via direct query")
                    else:
                        logger.error(f"❌ Table '{table}' verification failed completely")
                        return False
            
            logger.info("🎉 All required tables verified successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying tables: {e}")
            return False
    
    def _verify_table_directly(self, table_name: str) -> bool:
        """Verify table exists using direct PostgreSQL query."""
        try:
            check_cmd = [
                "psql",
                "-h", self.db_host,
                "-p", self.db_port,
                "-U", self.db_user,
                "-d", self.db_name,
                "-c", f"SELECT 1 FROM {table_name} LIMIT 1;",
                "-t"
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_password
            
            result = subprocess.run(
                check_cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception:
            return False


def main():
    """Main function to run schema setup."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🗄️ Stori Automated Schema Setup")
    print("=" * 50)
    
    # Show environment info
    supabase_url = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
    is_local = "127.0.0.1" in supabase_url or "localhost" in supabase_url
    
    if is_local:
        print("🏠 Using LOCAL Supabase environment")
        print("   Make sure 'supabase start' is running!")
    else:
        print("☁️ Using HOSTED Supabase environment")
        print(f"   URL: {supabase_url}")
    
    print()
    
    schema_setup = AutoSchemaSetup()
    
    # Run schema setup
    if schema_setup.setup_schema():
        print("\n🔍 Verifying table creation...")
        if schema_setup.verify_tables():
            print("\n🎉 Database schema setup completed successfully!")
            print("   You can now run setup_database.py to populate data.")
            return True
        else:
            print("\n❌ Table verification failed!")
            return False
    else:
        print("\n❌ Schema setup failed!")
        return False


if __name__ == "__main__":
    main()