#!/usr/bin/env python3
"""Test script to create a test user and get tokens for development."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client
from config.settings import get_settings
import json

def main():
    settings = get_settings()
    
    # Create Supabase client
    client = create_client(settings.supabase_url, settings.supabase_key)
    
    print("Testing Supabase Auth Integration")
    print("=" * 40)
    
    # Try to create a test user
    test_email = "devtest@stori-app.com"
    test_password = "DevTest123!"
    
    print(f"\n1. Attempting to register user: {test_email}")
    try:
        response = client.auth.sign_up({
            "email": test_email,
            "password": test_password,
            "options": {
                "data": {
                    "full_name": "Dev Test User"
                }
            }
        })
        
        print(f"   Registration successful: {response.user is not None}")
        print(f"   Session created: {response.session is not None}")
        
        if response.user:
            print(f"   User ID: {response.user.id}")
            print(f"   Email: {response.user.email}")
            print(f"   Email confirmed: {response.user.email_confirmed_at is not None}")
        
        if response.session:
            print(f"   Access Token: {response.session.access_token[:50]}...")
            print(f"   Token Type: {response.session.token_type}")
            print(f"   Expires In: {response.session.expires_in}")
            
            # Save token for testing
            with open('test_token.json', 'w') as f:
                json.dump({
                    "access_token": response.session.access_token,
                    "token_type": response.session.token_type,
                    "user_id": response.user.id,
                    "email": response.user.email
                }, f, indent=2)
            print("   Token saved to test_token.json")
    
    except Exception as e:
        print(f"   Registration failed: {e}")
        
    print(f"\n2. Attempting to login user: {test_email}")
    try:
        response = client.auth.sign_in_with_password({
            "email": test_email,
            "password": test_password
        })
        
        print(f"   Login successful: {response.session is not None}")
        if response.session:
            print(f"   Access Token: {response.session.access_token[:50]}...")
            
            # Save login token
            with open('login_token.json', 'w') as f:
                json.dump({
                    "access_token": response.session.access_token,
                    "token_type": response.session.token_type,
                    "user_id": response.user.id,
                    "email": response.user.email
                }, f, indent=2)
            print("   Login token saved to login_token.json")
    
    except Exception as e:
        print(f"   Login failed: {e}")

if __name__ == "__main__":
    main()