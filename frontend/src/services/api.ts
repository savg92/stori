// Complete API service functions for Stori Expense Tracker
import { apiClient } from '../lib/api-client';
import { API_ENDPOINTS } from '../lib/config';
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

// Transaction API
export const transactions = {
	list: async (query?: TransactionQuery): Promise<TransactionListResponse> => {
		const params = new URLSearchParams();
		if (query?.limit) params.append('limit', query.limit.toString());
		if (query?.offset) params.append('offset', query.offset.toString());
		if (query?.type) params.append('type', query.type);
		if (query?.category) params.append('category', query.category);
		if (query?.start_date) params.append('start_date', query.start_date);
		if (query?.end_date) params.append('end_date', query.end_date);

		const url = `${API_ENDPOINTS.transactions.list}${
			params.toString() ? `?${params.toString()}` : ''
		}`;
		return apiClient.get<TransactionListResponse>(url);
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
		const searchParams = new URLSearchParams();
		if (params?.startDate) searchParams.append('start_date', params.startDate);
		if (params?.endDate) searchParams.append('end_date', params.endDate);

		const url = `${API_ENDPOINTS.expenses.summary}${
			searchParams.toString() ? `?${searchParams.toString()}` : ''
		}`;
		return apiClient.get<ExpenseSummary>(url);
	},

	trends: async (
		period: 'monthly' | 'weekly' = 'monthly'
	): Promise<ExpenseTrends> => {
		const params = new URLSearchParams();
		params.append('period', period);

		const url = `${API_ENDPOINTS.expenses.trends}?${params.toString()}`;
		return apiClient.get<ExpenseTrends>(url);
	},

	categories: async (): Promise<TopCategoriesResponse> => {
		return apiClient.get<TopCategoriesResponse>(
			API_ENDPOINTS.expenses.topCategories
		);
	},
};

// Timeline API
export const timeline = {
	data: async (
		startDate?: string,
		endDate?: string,
		granularity: 'daily' | 'weekly' | 'monthly' = 'monthly'
	): Promise<TimelineData> => {
		const params = new URLSearchParams();
		if (startDate) params.append('start_date', startDate);
		if (endDate) params.append('end_date', endDate);
		params.append('granularity', granularity);

		const url = `${API_ENDPOINTS.timeline.data}?${params.toString()}`;
		return apiClient.get<TimelineData>(url);
	},

	summary: async (
		period: 'month' | 'quarter' | 'year' = 'month'
	): Promise<TimelineSummary> => {
		const params = new URLSearchParams();
		params.append('period', period);

		const url = `/api/timeline/summary?${params.toString()}`;
		return apiClient.get<TimelineSummary>(url);
	},
};

// AI API
export const ai = {
	advice: async (request: AIAdviceRequest): Promise<AIAdviceResponse> => {
		return apiClient.post<AIAdviceResponse>(API_ENDPOINTS.ai.advice, request);
	},

	chat: async (
		message: string,
		sessionId?: string
	): Promise<AIAdviceResponse> => {
		const requestData = {
			message,
			session_id: sessionId,
		};

		const response = await apiClient.post<AIAdviceResponse>(
			API_ENDPOINTS.ai.chat,
			requestData
		);

		return response;
	},

	health: async (): Promise<{ status: string; providers: string[] }> => {
		return apiClient.get(API_ENDPOINTS.ai.health);
	},

	quickInsights: async (): Promise<{
		insights: string[];
		generated_at: string;
	}> => {
		return apiClient.get(API_ENDPOINTS.ai.quickInsights);
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
