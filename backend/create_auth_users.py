#!/usr/bin/env python3
"""
Create Supabase authentication users for the existing database profiles.
This script creates auth users that correspond to the profiles in the database.
"""

import asyncio
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Test credentials for the mock users
TEST_USERS = [
    {
        "email": "alex.johnson@email.com",
        "password": "testpassword123",
        "name": "Alex Johnson",
        "profile": "young_professional"
    },
    {
        "email": "maria.garcia@email.com", 
        "password": "testpassword123",
        "name": "Maria Garcia",
        "profile": "family_household"
    },
    {
        "email": "sam.chen@email.com",
        "password": "testpassword123", 
        "name": "Sam Chen",
        "profile": "freelancer"
    },
    {
        "email": "robert.smith@email.com",
        "password": "testpassword123",
        "name": "Robert Smith", 
        "profile": "retiree"
    }
]

def create_auth_users():
    """Create authentication users in Supabase."""
    
    # Get Supabase credentials - use local Supabase for development
    supabase_url = os.getenv("SUPABASE_URL", "http://127.0.0.1:54321")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "sb_secret_N7UND0UgjKTVK-Uodkm0Hg_xSvEMPvz")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        print("Required environment variables:")
        print("  - SUPABASE_URL or VITE_SUPABASE_URL")
        print("  - SUPABASE_SERVICE_ROLE_KEY or VITE_SUPABASE_PUBLISHABLE_KEY")
        return False
        
    print(f"🔧 Connecting to Supabase: {supabase_url}")
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        print("👥 Creating authentication users...")
        
        for user_data in TEST_USERS:
            email = user_data["email"]
            password = user_data["password"]
            name = user_data["name"]
            
            print(f"\n🔐 Creating auth user: {email}")
            
            try:
                # Try to sign up the user
                result = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "full_name": name
                        }
                    }
                })
                
                if result.user:
                    print(f"  ✅ Successfully created auth user: {email}")
                    print(f"     User ID: {result.user.id}")
                    if result.user.email_confirmed_at:
                        print("     ✅ Email confirmed")
                    else:
                        print("     ⏳ Email confirmation pending")
                else:
                    print(f"  ❌ Failed to create user: {email}")
                    if result.error:
                        print(f"     Error: {result.error.message}")
                        
            except Exception as e:
                print(f"  ❌ Exception creating user {email}: {str(e)}")
                
        print("\n🎉 Authentication user creation completed!")
        print("\n📋 Test Credentials:")
        print("=" * 50)
        for user_data in TEST_USERS:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Profile: {user_data['profile']}")
            print("-" * 30)
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {str(e)}")
        return False

def main():
    """Main function."""
    print("🚀 Stori Authentication User Setup")
    print("=" * 50)
    
    success = create_auth_users()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("\n📖 Next Steps:")
        print("1. Users can now sign in with the credentials above")
        print("2. Run the frontend and test authentication")
        print("3. Check the E2E tests with real authentication")
        
    else:
        print("\n❌ Setup failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file has the correct Supabase credentials")
        print("2. Verify you have the SERVICE_ROLE_KEY (not just the publishable key)")
        print("3. Make sure the Supabase project is active and accessible")

if __name__ == "__main__":
    main()