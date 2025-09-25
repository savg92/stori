#!/usr/bin/env python3
"""
Confirm email addresses for Supabase auth users using admin API.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# User IDs from previous creation
USER_IDS = [
    "3eb6cccd-2201-4015-abd5-2ec816157ec3",  # alex.johnson.test123@gmail.com
    "f329e9f1-bd27-468b-b493-6b5ba191e9a0",  # maria.garcia.test123@gmail.com  
    "87eb0f80-2b11-4c98-bb79-2b58e93b5aef",  # sam.chen.test123@gmail.com
    "2ffd9fb5-00bc-4b67-ba8d-e4c873080937",  # robert.smith.test123@gmail.com
]

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
        "apikey": service_role_key,
        "Content-Type": "application/json"
    }
    
    # Update user to mark email as confirmed
    data = {
        "email_confirm": True
    }
    
    try:
        response = requests.put(admin_url, headers=headers, json=data)
        if response.status_code == 200:
            user_data = response.json()
            print(f"  ✅ Email confirmed for user {user_id}")
            print(f"     Email: {user_data.get('email', 'unknown')}")
            return True
        else:
            print(f"  ❌ Failed to confirm email for user {user_id}")
            print(f"     Status: {response.status_code}")
            print(f"     Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Exception confirming email for user {user_id}: {e}")
        return False

def main():
    """Confirm all test user emails."""
    print("🚀 Stori Email Confirmation")
    print("=" * 50)
    
    success_count = 0
    
    for user_id in USER_IDS:
        print(f"\n🔐 Confirming email for user: {user_id}")
        if confirm_user_email(user_id):
            success_count += 1
    
    print(f"\n🎉 Email confirmation completed!")
    print(f"✅ Successfully confirmed: {success_count}/{len(USER_IDS)} users")
    
    if success_count == len(USER_IDS):
        print("\n📖 Next Steps:")
        print("1. Test user sign-in with the credentials")
        print("2. Run the frontend and verify authentication works")
    else:
        print("\n⚠️  Some emails could not be confirmed programmatically.")
        print("   Consider disabling 'Confirm Email' in Supabase Auth settings.")

if __name__ == "__main__":
    main()