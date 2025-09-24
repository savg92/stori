// Complete API service functions for Stori Expense Tracker
import { apiClient } from '../lib/api-client';
import { API_ENDPOINTS, isDevelopment } from '../lib/config';
import type {
	Transaction,
	CreateTransactionRequest,
	UpdateTransactionRequest,
	TransactionQuery,
	TransactionListResponse,
	ExpenseSummary,
	AIAdviceRequest,
	AIAdviceResponse,
	TimelineData,
	ExpenseTrends,
	TimelineSummary,
	TopCategoriesResponse,
} from '../types/api';

// Mock API response interfaces
interface MockSummaryResponse {
	success: boolean;
	user: {
		id: string;
		email: string;
		full_name: string;
		created_at: string;
		preferences: {
			financial_goals: string[];
			spending_habits: string;
			income_level: string;
		};
	};
	total_income: number;
	total_expenses: number;
	net_income: number;
	transaction_count: number;
	expense_categories: Record<string, number>;
	profile_type: string;
}

// Transform mock summary data to frontend ExpenseSummary format
const transformMockSummary = (
	mockData: MockSummaryResponse
): ExpenseSummary => {
	// Convert expense_categories object to CategorySummary array
	const expense_categories = Object.entries(mockData.expense_categories).map(
		([category, amount]) => ({
			category,
			total_amount: Math.abs(amount), // Convert negative amounts to positive
			transaction_count: 1, // We don't have this data from mock, so use default
			percentage: (Math.abs(amount) / Math.abs(mockData.total_expenses)) * 100,
			avg_amount: Math.abs(amount), // Simplified - would need transaction counts for accurate avg
		})
	);

	return {
		total_expenses: Math.abs(mockData.total_expenses),
		total_income: mockData.total_income,
		net_income: mockData.net_income,
		expense_categories,
		income_categories: [], // Mock doesn't provide income breakdown
		period_start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
		period_end: new Date().toISOString(),
	};
};

// Transaction API
export const transactions = {
	list: async (query?: TransactionQuery): Promise<TransactionListResponse> => {
		if (isDevelopment()) {
			// In development, return mock data structure
			return {
				items: [],
				total: 0,
				limit: query?.limit || 50,
				offset: query?.offset || 0,
				has_next: false,
				has_previous: false,
			};
		}
		return apiClient.get<TransactionListResponse>(
			API_ENDPOINTS.transactions.list
		);
	},

	get: async (id: string): Promise<Transaction> => {
		return apiClient.get<Transaction>(API_ENDPOINTS.transactions.get(id));
	},

	create: async (data: CreateTransactionRequest): Promise<Transaction> => {
		return apiClient.post<Transaction>(API_ENDPOINTS.transactions.create, data);
	},

	update: async (
		id: string,
		data: UpdateTransactionRequest
	): Promise<Transaction> => {
		return apiClient.put<Transaction>(API_ENDPOINTS.transactions.get(id), data);
	},

	delete: async (id: string): Promise<void> => {
		return apiClient.delete(API_ENDPOINTS.transactions.get(id));
	},
};

// Expense API
export const expenses = {
	summary: async (params?: {
		startDate?: string;
		endDate?: string;
	}): Promise<ExpenseSummary> => {
		if (isDevelopment()) {
			// Use mock API endpoint for development
			const mockResponse = await apiClient.get<MockSummaryResponse>(
				'/api/mock/users/user_1_young_professional/summary'
			);
			return transformMockSummary(mockResponse);
		}
		return apiClient.get<ExpenseSummary>(API_ENDPOINTS.expenses.summary);
	},

	trends: async (
		period: 'monthly' | 'weekly' = 'monthly'
	): Promise<ExpenseTrends> => {
		if (isDevelopment()) {
			// Mock trends data
			return {
				trends: [
					{
						period: '2024-01',
						amount: 2500,
						transaction_count: 25,
						change_percentage: -5.2,
					},
					{
						period: '2024-02',
						amount: 2750,
						transaction_count: 28,
						change_percentage: 10.0,
					},
					{
						period: '2024-03',
						amount: 2300,
						transaction_count: 22,
						change_percentage: -16.4,
					},
				],
				period,
				growth_rate: -3.9,
				trend_direction: 'down',
			};
		}
		return apiClient.get<ExpenseTrends>('/api/expenses/trends');
	},

	categories: async (): Promise<TopCategoriesResponse> => {
		if (isDevelopment()) {
			// Mock categories data
			return {
				categories: [
					{
						category: 'food_dining',
						total_amount: 800,
						percentage: 35.2,
						transaction_count: 15,
						rank: 1,
					},
					{
						category: 'transportation',
						total_amount: 450,
						percentage: 19.8,
						transaction_count: 8,
						rank: 2,
					},
					{
						category: 'entertainment',
						total_amount: 320,
						percentage: 14.1,
						transaction_count: 6,
						rank: 3,
					},
					{
						category: 'shopping',
						total_amount: 280,
						percentage: 12.3,
						transaction_count: 9,
						rank: 4,
					},
					{
						category: 'bills_utilities',
						total_amount: 420,
						percentage: 18.5,
						transaction_count: 4,
						rank: 5,
					},
				],
				total_analyzed: 2270,
				period_start: new Date(
					Date.now() - 30 * 24 * 60 * 60 * 1000
				).toISOString(),
				period_end: new Date().toISOString(),
			};
		}
		return apiClient.get<TopCategoriesResponse>('/api/expenses/categories');
	},
};

// Timeline API
export const timeline = {
	data: async (
		startDate?: string,
		endDate?: string,
		granularity: 'daily' | 'weekly' | 'monthly' = 'monthly'
	): Promise<TimelineData> => {
		if (isDevelopment()) {
			// Mock timeline data
			const mockData: TimelineData = {
				data_points: [
					{
						date: '2024-01',
						income: 5500,
						expenses: -2500,
						net_income: 3000,
						transaction_count: 35,
					},
					{
						date: '2024-02',
						income: 5500,
						expenses: -2750,
						net_income: 2750,
						transaction_count: 38,
					},
					{
						date: '2024-03',
						income: 6000,
						expenses: -2300,
						net_income: 3700,
						transaction_count: 32,
					},
				],
				summary: {
					total_income: 17000,
					total_expenses: -7550,
					net_income: 9450,
					avg_monthly_income: 5667,
					avg_monthly_expenses: -2517,
					best_month: '2024-03',
					worst_month: '2024-02',
				},
				period_start:
					startDate ||
					new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
				period_end: endDate || new Date().toISOString(),
			};
			return mockData;
		}
		return apiClient.get<TimelineData>('/api/timeline/data');
	},

	summary: async (
		period: 'month' | 'quarter' | 'year' = 'month'
	): Promise<TimelineSummary> => {
		if (isDevelopment()) {
			// Mock summary data
			return {
				total_income: 17000,
				total_expenses: -7550,
				net_income: 9450,
				avg_monthly_income: 5667,
				avg_monthly_expenses: -2517,
				best_month: '2024-03',
				worst_month: '2024-02',
			};
		}
		return apiClient.get<TimelineSummary>('/api/timeline/summary');
	},
};

// AI API
export const ai = {
	advice: async (request: AIAdviceRequest): Promise<AIAdviceResponse> => {
		if (isDevelopment()) {
			// Mock AI advice response
			return {
				response:
					"Based on your spending patterns, I notice you're doing well with keeping expenses under control. Your biggest expense category is dining at $800/month. Consider setting a budget limit and exploring meal prep options to reduce this by 15-20%.",
				confidence: 0.85,
				context_used: {
					transaction_count: 42,
					date_range: '2024-01 to 2024-03',
					categories_analyzed: [
						'food_dining',
						'transportation',
						'entertainment',
					],
				},
				suggestions: [
					'Set a $650 monthly budget for dining expenses',
					'Try meal prepping 2-3 times per week',
					'Look for dining deals and happy hours',
					'Consider cooking more meals at home',
				],
				session_id: 'mock_session_' + Date.now(),
			};
		}
		return apiClient.post<AIAdviceResponse>('/api/ai/advice', request);
	},

	chat: async (
		message: string,
		sessionId?: string
	): Promise<AIAdviceResponse> => {
		if (isDevelopment()) {
			// Mock chat response
			return {
				response: `I understand you're asking: "${message}". Based on your financial profile, here's my advice...`,
				confidence: 0.8,
				context_used: {
					transaction_count: 42,
					date_range: '2024-01 to 2024-03',
					categories_analyzed: ['food_dining', 'transportation'],
				},
				suggestions: [
					'Review your monthly spending patterns',
					'Consider setting up automatic savings',
				],
				session_id: sessionId || 'mock_session_' + Date.now(),
			};
		}
		return apiClient.post<AIAdviceResponse>('/api/ai/chat', {
			message,
			session_id: sessionId,
		});
	},

	health: async (): Promise<{ status: string; providers: string[] }> => {
		if (isDevelopment()) {
			return { status: 'healthy', providers: ['openai', 'anthropic'] };
		}
		return apiClient.get('/api/ai/health');
	},

	quickInsights: async (): Promise<{
		insights: string[];
		generated_at: string;
	}> => {
		if (isDevelopment()) {
			return {
				insights: [
					'Your spending decreased 16.4% this month compared to last month',
					'Dining expenses represent 35% of your total spending',
					'You saved $200 more than your target this month',
				],
				generated_at: new Date().toISOString(),
			};
		}
		return apiClient.get('/api/ai/insights');
	},
};

// Utility functions
export const utils = {
	getCurrentMonthRange: (): { start: string; end: string } => {
		const now = new Date();
		const start = new Date(now.getFullYear(), now.getMonth(), 1);
		const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);

		return {
			start: start.toISOString().split('T')[0],
			end: end.toISOString().split('T')[0],
		};
	},
};

// Export combined API object for use in hooks
export const api = {
	transactions,
	expenses,
	timeline,
	ai,
	utils,
};

// Export individual APIs for backward compatibility
export { transactions as transactionApi, expenses as expenseApi };

// Default export
export default api;
