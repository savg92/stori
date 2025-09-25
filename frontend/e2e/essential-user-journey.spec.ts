import { test, expect } from '@playwright/test';

test.describe('Essential User Journey - Alex Johnson', () => {
  
  test.beforeEach(async ({ page }) => {
    // Start fresh on login page
    await page.goto('http://localhost:5173');
  });

  test('complete user authentication and dashboard access with API test', async ({ page }) => {
    console.log('🧪 Testing complete user flow with API authentication...');

    // Test login
    await page.goto('http://localhost:5173/login');
    await page.fill('input[type="email"]', 'alex.johnson+test@example.com');
    await page.fill('input[type="password"]', 'securepass123');
    await page.click('button[type="submit"]');

    // Wait for navigation to dashboard
    await page.waitForURL('http://localhost:5173/', { timeout: 10000 });
    console.log('✅ Successfully navigated to dashboard');

    // Verify we're on the dashboard
    await expect(page.locator('text=Dashboard')).toBeVisible();
    console.log('✅ Dashboard page loaded');

    // Extract JWT token from localStorage and test API
    const apiTestResult = await page.evaluate(async () => {
      // Get the auth token from localStorage
      const keys = Object.keys(localStorage);
      const authKey = keys.find(key => key.includes('auth-token'));
      
      if (!authKey) {
        return { error: 'No auth token found in localStorage', keys: keys };
      }
      
      const auth = JSON.parse(localStorage.getItem(authKey) || '{}');
      const token = auth.access_token;
      
      if (!token) {
        return { error: 'No access token found in auth object', auth: auth };
      }
      
      // Test API call
      try {
        const response = await fetch('http://localhost:8000/api/transactions/', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        let responseData;
        try {
          responseData = await response.json();
        } catch {
          responseData = await response.text();
        }
        
        return {
          success: true,
          token: token ? 'Token found' : 'No token',
          status: response.status,
          statusText: response.statusText,
          data: responseData
        };
      } catch (error) {
        return { error: error.message };
      }
    });

    console.log('� API Test Result:', apiTestResult);

    // Verify that we have a token and it's working
    expect(apiTestResult.success).toBe(true);
    expect(apiTestResult.status).not.toBe(401);
    
    if (apiTestResult.status === 200) {
      console.log('✅ API authentication working correctly!');
    } else {
      console.log(`⚠️ API returned status ${apiTestResult.status}:`, apiTestResult.data);
    }
  });
  
  test('Quick Authentication Test', async ({ page }) => {
    console.log('🔑 Quick authentication verification...');
    
    await page.fill('input[type="email"]', 'alex.johnson@email.com');
    await page.fill('input[type="password"]', 'testpassword123');
    await page.click('button[type="submit"]');
    
    // Verify successful login
    const loginToast = page.getByText('Successfully signed in!');
    await expect(loginToast).toBeVisible({ timeout: 5000 });
    
    // Verify form disappears (user logged in)
    await expect(page.locator('form')).not.toBeVisible({ timeout: 5000 });
    
    console.log('✅ Quick authentication verified');
  });
  
  test('Error Handling Test', async ({ page }) => {
    console.log('❌ Testing error handling...');
    
    // Test wrong password
    await page.fill('input[type="email"]', 'alex.johnson@email.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    const errorToast = page.getByText('Invalid login credentials');
    await expect(errorToast).toBeVisible({ timeout: 5000 });
    
    console.log('✅ Error handling verified');
  });
  
});