#!/usr/bin/env python3
"""
Manual Supabase authentication test script.
This script uses the Supabase client to get a real JWT token and test API endpoints.
"""

import requests
import json
from supabase import create_client, Client

# Configuration
API_BASE_URL = "http://localhost:8000"
SUPABASE_URL = "http://127.0.0.1:54321"
SUPABASE_KEY = "sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH"

# Test credentials
TEST_EMAIL = "alex.johnson@email.com"
TEST_PASSWORD = "testpassword123"

def get_supabase_token():
    """Get a real JWT token from Supabase by signing in."""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Sign in with test user
        response = supabase.auth.sign_in_with_password({"email": TEST_EMAIL, "password": TEST_PASSWORD})
        
        if response.user and response.session:
            return response.session.access_token
        else:
            print(f"❌ Login failed - no session or user returned")
            return None
    except Exception as e:
        print(f"❌ Failed to get Supabase token: {e}")
        return None

def test_api_endpoint(endpoint, token):
    """Test a single API endpoint with the JWT token."""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return {
            "url": url,
            "status": response.status_code,
            "status_text": response.reason,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e)
        }

def main():
    print("🧪 Testing Backend Supabase Authentication")
    print("=" * 50)
    
    # Get real Supabase token
    print("Getting Supabase JWT token...")
    token = get_supabase_token()
    
    if not token:
        print("❌ Could not get authentication token - exiting")
        return
    
    print(f"✅ JWT Token obtained successfully")
    print(f"Token preview: {token[:50]}...")
    
    print("\n" + "=" * 50)
    print("Testing API Endpoints")
    print("=" * 50)
    
    # Test endpoints
    endpoints_to_test = [
        "/api/health",  # Should work without auth
        "/api/transactions/",
        "/api/expenses/summary",
        "/api/timeline",
        "/api/ai/health"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\nTesting: {endpoint}")
        
        if endpoint == "/api/health":
            # Test health endpoint without auth first
            result = test_api_endpoint(endpoint, "")  # No token
            print(f"  Without Auth: {result['status']} - {result.get('data', result.get('error'))}")
        
        # Test with auth token
        result = test_api_endpoint(endpoint, token)
        if 'error' in result:
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  Status: {result['status']} ({result['status_text']})")
            if result['status'] == 200:
                print(f"  ✅ Success: {type(result['data']).__name__} response")
                if isinstance(result['data'], dict) and len(result['data']) <= 3:
                    print(f"  Data Preview: {json.dumps(result['data'], indent=4)[:200]}...")
                elif isinstance(result['data'], list) and len(result['data']) == 0:
                    print(f"  Data: Empty list (no data yet)")
                elif isinstance(result['data'], list):
                    print(f"  Data: List with {len(result['data'])} items")
            elif result['status'] == 401:
                print(f"  ❌ Authentication failed: {result['data']}")
            elif result['status'] == 500:
                print(f"  ❌ Server error: {result['data']}")
            else:
                print(f"  ⚠️  Unexpected status: {result['data']}")
    
    print("\n" + "=" * 50)
    print("Authentication Test Complete")
    print("=" * 50)

if __name__ == "__main__":
    main()