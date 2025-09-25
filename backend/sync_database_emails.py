#!/usr/bin/env python3
"""
Update database user emails to match authentication emails and repopulate transaction data.
"""

import os
import json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Email mapping from old to new
EMAIL_MAPPING = {
    "alex.johnson@email.com": "alex.johnson.test123@gmail.com",
    "maria.garcia@email.com": "maria.garcia.test123@gmail.com", 
    "sam.chen@email.com": "sam.chen.test123@gmail.com",
    "robert.smith@email.com": "robert.smith.test123@gmail.com",
    "emma.wilson@email.com": "emma.wilson@email.com"  # Keep as is since no auth user created
}

def update_user_emails():
    """Update user emails in database to match authentication emails."""
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_role_key:
        print("❌ Missing Supabase credentials!")
        return False
        
    supabase = create_client(supabase_url, service_role_key)
    
    print("🔄 Updating user emails in database...")
    
    try:
        # Get all current users
        result = supabase.table('users').select('*').execute()
        current_users = result.data
        
        for user in current_users:
            old_email = user['email']
            if old_email in EMAIL_MAPPING:
                new_email = EMAIL_MAPPING[old_email]
                if old_email != new_email:
                    print(f"  📧 Updating {user['id']}: {old_email} → {new_email}")
                    
                    # Update the user email
                    update_result = supabase.table('users').update({
                        'email': new_email
                    }).eq('id', user['id']).execute()
                    
                    if update_result.data:
                        print(f"     ✅ Successfully updated {user['id']}")
                    else:
                        print(f"     ❌ Failed to update {user['id']}")
                else:
                    print(f"  ✅ {user['id']}: Email already correct ({new_email})")
            else:
                print(f"  ⚠️  {user['id']}: No mapping found for {old_email}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error updating user emails: {e}")
        return False

def update_transaction_user_ids():
    """Update transaction user_id references to match updated emails."""
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not service_role_key:
        print("❌ Missing Supabase credentials!")
        return False
        
    supabase = create_client(supabase_url, service_role_key)
    
    print("\n🔄 Updating transaction references...")
    
    try:
        # Get all transactions
        result = supabase.table('transactions').select('*').execute()
        transactions = result.data
        
        updated_count = 0
        
        # Get updated users with new emails
        users_result = supabase.table('users').select('*').execute()
        users = {user['id']: user for user in users_result.data}
        
        print(f"  📊 Found {len(transactions)} transactions to verify")
        
        for transaction in transactions:
            user_id = transaction['user_id']
            if user_id in users:
                print(f"  ✅ Transaction {transaction['id']}: user_id {user_id} is valid")
                updated_count += 1
            else:
                print(f"  ⚠️  Transaction {transaction['id']}: user_id {user_id} not found in users")
        
        print(f"  📈 {updated_count}/{len(transactions)} transactions have valid user references")
        return True
        
    except Exception as e:
        print(f"❌ Error checking transaction references: {e}")
        return False

def main():
    """Update database to match authentication emails."""
    print("🚀 Database Email Sync")
    print("=" * 50)
    
    # Update user emails
    if update_user_emails():
        print("✅ User emails updated successfully")
    else:
        print("❌ Failed to update user emails")
        return
    
    # Update transaction references  
    if update_transaction_user_ids():
        print("✅ Transaction references verified")
    else:
        print("❌ Failed to verify transaction references")
        return
    
    print("\n🎉 Database sync completed!")
    print("\n📖 Next Steps:")
    print("1. Test sign-in again with: alex.johnson.test123@gmail.com")
    print("2. Dashboard should now show data for the signed-in user")
    print("3. Verify all transaction data appears correctly")

if __name__ == "__main__":
    main()