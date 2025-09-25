#!/usr/bin/env python3
"""
Create Supabase authentication users for the existing database profiles.
This script creates auth users that correspond to the profiles in the database.
"""

import asyncio
import os
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Test credentials for the mock users
TEST_USERS = [
    {
        "email": "alex.johnson.test123@gmail.com",
        "password": "testpassword123",
        "name": "Alex Johnson",
        "profile": "young_professional"
    },
    {
        "email": "maria.garcia.test123@gmail.com", 
        "password": "testpassword123",
        "name": "Maria Garcia",
        "profile": "family_household"
    },
    {
        "email": "sam.chen.test123@gmail.com",
        "password": "testpassword123", 
        "name": "Sam Chen",
        "profile": "freelancer"
    },
    {
        "email": "robert.smith.test123@gmail.com",
        "password": "testpassword123",
        "name": "Robert Smith", 
        "profile": "retiree"
    }
]

def get_user_by_email(email: str):
    """Get user by email using admin API."""
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_role_key:
        return None
    
    # Use the admin API to get user by email
    admin_url = f"{supabase_url}/auth/v1/admin/users"
    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json"
    }
    
    params = {"email": email}
    
    try:
        response = requests.get(admin_url, headers=headers, params=params)
        if response.status_code == 200:
            users = response.json().get("users", [])
            if users:
                return users[0]  # Return first user found
        return None
    except Exception as e:
        print(f"  ❌ Exception getting user {email}: {e}")
        return None

def confirm_user_email(user_id: str):
    """Confirm a user's email using the admin API."""
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_role_key:
        print("❌ Missing Supabase credentials!")
        return False
    
    # Use the admin API to confirm the email
    admin_url = f"{supabase_url}/auth/v1/admin/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json"
    }
    
    # Update user to mark email as confirmed
    data = {
        "email_confirm": True
    }
    
    try:
        response = requests.put(admin_url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"  ✅ Email confirmed for user {user_id}")
            return True
        else:
            print(f"  ❌ Failed to confirm email for user {user_id}: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Exception confirming email for user {user_id}: {e}")
        return False

def create_auth_users():
    """Create authentication users in Supabase."""
    
    # Get Supabase credentials - use local Supabase for development
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
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
        
        created_users = []
        
        for user_data in TEST_USERS:
            email = user_data["email"]
            password = user_data["password"]
            name = user_data["name"]
            
            print(f"\n🔐 Processing auth user: {email}")
            
            # Check if user already exists
            existing_user = get_user_by_email(email)
            
            if existing_user:
                user_id = existing_user["id"]
                print(f"  ✅ User already exists: {email}")
                print(f"     User ID: {user_id}")
                
                # Check if email is confirmed
                if existing_user.get("email_confirmed_at"):
                    print("     ✅ Email already confirmed")
                else:
                    # Confirm the email
                    if confirm_user_email(user_id):
                        print("     ✅ Email confirmed")
                    else:
                        print("     ⏳ Email confirmation failed")
                        
                created_users.append({"email": email, "user_id": user_id})
            else:
                # Create new user
                try:
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
                        user_id = result.user.id
                        print(f"  ✅ Successfully created auth user: {email}")
                        print(f"     User ID: {user_id}")
                        
                        # Confirm the email using admin API
                        if confirm_user_email(user_id):
                            print("     ✅ Email confirmed")
                        else:
                            print("     ⏳ Email confirmation failed - may need manual confirmation")
                        
                        created_users.append({"email": email, "user_id": user_id})
                    else:
                        print(f"  ❌ Failed to create user: {email}")
                        print(f"     Response: {result}")
                            
                except Exception as e:
                    print(f"  ❌ Exception creating user {email}: {str(e)}")
                
        print("\n🎉 Authentication user processing completed!")
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