import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display login form when not authenticated', async ({ page }) => {
    // Check for login form elements
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible()
  })

  test('should show validation errors for empty form submission', async ({ page }) => {
    // Try to submit empty form
    await page.getByRole('button', { name: /sign in/i }).click()
    
    // Check for validation errors
    await expect(page.getByText(/email is required/i)).toBeVisible()
    await expect(page.getByText(/password is required/i)).toBeVisible()
  })

  test('should show error for invalid email format', async ({ page }) => {
    // Fill in invalid email
    await page.fill('input[type="email"]', 'invalid-email')
    await page.fill('input[type="password"]', 'password123')
    await page.getByRole('button', { name: /sign in/i }).click()
    
    // Check for email validation error
    await expect(page.getByText(/please enter a valid email/i)).toBeVisible()
  })

  test('should successfully login with valid credentials', async ({ page }) => {
    // Fill in valid test credentials
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'Test123!')
    
    // Submit the form
    await page.getByRole('button', { name: /sign in/i }).click()
    
    // Wait for navigation or success indicator
    // This test might need adjustment based on actual app behavior
    await page.waitForURL('**', { timeout: 10000 })
    
    // Check that we're no longer on login screen
    await expect(page.locator('input[type="email"]')).not.toBeVisible({ timeout: 5000 })
  })

  test('should handle login failure gracefully', async ({ page }) => {
    // Fill in invalid credentials
    await page.fill('input[type="email"]', 'wrong@example.com')
    await page.fill('input[type="password"]', 'wrongpassword')
    
    // Submit the form
    await page.getByRole('button', { name: /sign in/i }).click()
    
    // Check for error message
    await expect(page.getByText(/invalid/i)).toBeVisible({ timeout: 5000 })
  })

  test('should toggle password visibility', async ({ page }) => {
    const passwordInput = page.locator('input[type="password"]')
    const toggleButton = page.getByRole('button', { name: /toggle password/i })
    
    // Initially password should be hidden
    await expect(passwordInput).toHaveAttribute('type', 'password')
    
    // Click toggle to show password
    await toggleButton.click()
    await expect(passwordInput).toHaveAttribute('type', 'text')
    
    // Click toggle to hide password again
    await toggleButton.click()
    await expect(passwordInput).toHaveAttribute('type', 'password')
  })
})