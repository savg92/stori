// API service functions for Stori Expense Tracker
import { apiClient } from '../lib/api-client';
import { API_ENDPOINTS, isDevelopment } from '../lib/config';
import type {
	Transaction,
	CreateTransactionRequest,
	TransactionListResponse,
	ExpenseSummary,
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
		income_categories: [], // Mock data doesn't provide income categories
		period_start: new Date().toISOString().split('T')[0], // Current month start
		period_end: new Date().toISOString().split('T')[0], // Current date
	};
};

// Transaction API
export const transactionApi = {
	list: async (): Promise<TransactionListResponse> => {
		const endpoint = API_ENDPOINTS.transactions.list;
		return apiClient.get<TransactionListResponse>(endpoint);
	},

	get: async (id: string): Promise<Transaction> => {
		return apiClient.get<Transaction>(API_ENDPOINTS.transactions.get(id));
	},

	create: async (data: CreateTransactionRequest): Promise<Transaction> => {
		return apiClient.post<Transaction>(API_ENDPOINTS.transactions.create, data);
	},
};

// Expense API
export const expenseApi = {
	summary: async (filters?: {
		startDate?: string;
		endDate?: string;
		category?: string;
		limit?: number;
	}): Promise<ExpenseSummary> => {
		const searchParams = new URLSearchParams();
		if (filters?.startDate)
			searchParams.append('start_date', filters.startDate);
		if (filters?.endDate) searchParams.append('end_date', filters.endDate);
		if (filters?.category) searchParams.append('category', filters.category);
		if (filters?.limit) searchParams.append('limit', filters.limit.toString());

		const endpoint = searchParams.toString()
			? `${API_ENDPOINTS.expenses.summary}?${searchParams.toString()}`
			: API_ENDPOINTS.expenses.summary;

		// In development, use mock data with transformation
		if (isDevelopment()) {
			const mockData = await apiClient.get<MockSummaryResponse>(endpoint);
			return transformMockSummary(mockData);
		}

		return apiClient.get<ExpenseSummary>(endpoint);
	},
};

// Utility functions
export const apiUtils = {
	getCurrentMonthRange: () => {
		const now = new Date();
		const start = new Date(now.getFullYear(), now.getMonth(), 1)
			.toISOString()
			.split('T')[0];
		const end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
			.toISOString()
			.split('T')[0];
		return { start, end };
	},
};

// Export all APIs
export const api = {
	transactions: transactionApi,
	expenses: expenseApi,
	utils: apiUtils,
};

export default api;
