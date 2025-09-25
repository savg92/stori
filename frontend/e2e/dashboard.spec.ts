import { test, expect } from '@playwright/test'

test.describe('Expense Summary Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.addInitScript(() => {
      window.localStorage.setItem('sb-auth-token', JSON.stringify({
        access_token: 'mock-token',
        user: { id: 'user-123', email: 'test@example.com' }
      }))
    })

    // Mock expense summary API
    await page.route('**/api/expenses/summary*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_expenses: 1250.50,
          total_income: 5000.00,
          net_amount: 3749.50,
          categories: [
            { category: 'Food', amount: -450.25, count: 15 },
            { category: 'Transportation', amount: -200.00, count: 8 },
            { category: 'Entertainment', amount: -150.75, count: 5 },
            { category: 'Shopping', amount: -449.50, count: 12 }
          ],
          monthly_trend: [
            { month: '2024-01', income: 5000.00, expenses: -1100.50 },
            { month: '2024-02', income: 5000.00, expenses: -1250.50 }
          ]
        })
      })
    })

    await page.goto('/')
    await page.waitForSelector('[data-testid="dashboard"]', { timeout: 10000 })
  })

  test('should display expense summary cards', async ({ page }) => {
    // Check total expenses card
    await expect(page.getByTestId('total-expenses')).toBeVisible()
    await expect(page.getByText('$1,250.50')).toBeVisible()
    
    // Check total income card
    await expect(page.getByTestId('total-income')).toBeVisible()
    await expect(page.getByText('$5,000.00')).toBeVisible()
    
    // Check net amount card
    await expect(page.getByTestId('net-amount')).toBeVisible()
    await expect(page.getByText('$3,749.50')).toBeVisible()
  })

  test('should display category breakdown chart', async ({ page }) => {
    // Check chart container is visible
    await expect(page.getByTestId('category-chart')).toBeVisible()
    
    // Check chart has data
    await expect(page.getByText('Food')).toBeVisible()
    await expect(page.getByText('Transportation')).toBeVisible()
    await expect(page.getByText('Entertainment')).toBeVisible()
    await expect(page.getByText('Shopping')).toBeVisible()
  })

  test('should display monthly trend chart', async ({ page }) => {
    // Check monthly trend chart
    await expect(page.getByTestId('monthly-trend')).toBeVisible()
    
    // Chart should contain income and expense lines
    await expect(page.locator('.recharts-line')).toHaveCount(2)
  })

  test('should filter by date range', async ({ page }) => {
    // Mock filtered API response
    await page.route('**/api/expenses/summary*', async route => {
      const url = new URL(route.request().url())
      if (url.searchParams.get('start_date')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            total_expenses: 650.25,
            total_income: 2500.00,
            net_amount: 1849.75,
            categories: [
              { category: 'Food', amount: -250.25, count: 8 },
              { category: 'Transportation', amount: -400.00, count: 4 }
            ],
            monthly_trend: [
              { month: '2024-02', income: 2500.00, expenses: -650.25 }
            ]
          })
        })
      } else {
        await route.continue()
      }
    })

    // Open date filter
    await page.getByRole('button', { name: /filter by date/i }).click()
    
    // Set date range
    await page.fill('input[name="start-date"]', '2024-02-01')
    await page.fill('input[name="end-date"]', '2024-02-29')
    await page.getByRole('button', { name: /apply filter/i }).click()
    
    // Check updated totals
    await expect(page.getByText('$650.25')).toBeVisible()
    await expect(page.getByText('$2,500.00')).toBeVisible()
  })

  test('should filter by category', async ({ page }) => {
    // Mock filtered API response
    await page.route('**/api/expenses/summary*', async route => {
      const url = new URL(route.request().url())
      if (url.searchParams.get('category')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            total_expenses: 450.25,
            total_income: 0.00,
            net_amount: -450.25,
            categories: [
              { category: 'Food', amount: -450.25, count: 15 }
            ],
            monthly_trend: [
              { month: '2024-01', income: 0.00, expenses: -200.25 },
              { month: '2024-02', income: 0.00, expenses: -250.00 }
            ]
          })
        })
      } else {
        await route.continue()
      }
    })

    // Open category filter
    await page.getByRole('button', { name: /filter by category/i }).click()
    
    // Select Food category
    await page.selectOption('select[name="category"]', 'Food')
    await page.getByRole('button', { name: /apply filter/i }).click()
    
    // Check filtered results
    await expect(page.getByText('$450.25')).toBeVisible()
    await expect(page.getByText('Food')).toBeVisible()
  })

  test('should export data', async ({ page }) => {
    // Start waiting for download before clicking the button
    const downloadPromise = page.waitForEvent('download')
    
    await page.getByRole('button', { name: /export/i }).click()
    
    const download = await downloadPromise
    
    // Check download started
    expect(download.suggestedFilename()).toMatch(/expenses.*\.csv/)
  })

  test('should refresh data', async ({ page }) => {
    // Mock refreshed data
    let callCount = 0
    await page.route('**/api/expenses/summary*', async route => {
      callCount++
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_expenses: callCount === 1 ? 1250.50 : 1350.75,
          total_income: 5000.00,
          net_amount: callCount === 1 ? 3749.50 : 3649.25,
          categories: [
            { category: 'Food', amount: callCount === 1 ? -450.25 : -550.50, count: 15 }
          ],
          monthly_trend: []
        })
      })
    })

    // Wait for initial load
    await expect(page.getByText('$1,250.50')).toBeVisible()
    
    // Click refresh
    await page.getByRole('button', { name: /refresh/i }).click()
    
    // Check updated data
    await expect(page.getByText('$1,350.75')).toBeVisible()
  })

  test('should handle loading states', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/expenses/summary*', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000))
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_expenses: 0,
          total_income: 0,
          net_amount: 0,
          categories: [],
          monthly_trend: []
        })
      })
    })

    await page.goto('/')
    
    // Check loading state
    await expect(page.getByTestId('loading-spinner')).toBeVisible()
    
    // Wait for data to load
    await expect(page.getByTestId('loading-spinner')).not.toBeVisible({ timeout: 2000 })
  })

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/expenses/summary*', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      })
    })

    await page.goto('/')
    
    // Check error message
    await expect(page.getByText(/error loading data/i)).toBeVisible()
    
    // Check retry button
    await expect(page.getByRole('button', { name: /retry/i })).toBeVisible()
  })
})