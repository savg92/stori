// API service functions for Stori Expense Tracker
import { apiClient } from '../lib/api-client';
import { API_ENDPOINTS } from '../lib/config';
import type {
	Transaction,
	CreateTransactionRequest,
	UpdateTransactionRequest,
	TransactionQuery,
	TransactionListResponse,
	ExpenseSummary,
	TimelineData,
	AIAdviceRequest,
	AIAdviceResponse,
	ExpenseTrends,
	TopCategoriesResponse,
	MonthlyComparison,
	CategorySummary,
	CashFlowAnalysis,
	SpendingVelocity,
	AIAnalysisResponse,
	QuickInsights,
} from '../types/api';

// Transaction API functions
export const transactionApi = {
	// Get paginated list of transactions with optional filtering
	list: async (query?: TransactionQuery): Promise<TransactionListResponse> => {
		const searchParams = new URLSearchParams();

		if (query) {
			Object.entries(query).forEach(([key, value]) => {
				if (value !== undefined && value !== null) {
					searchParams.append(key, String(value));
				}
			});
		}

		const endpoint =
			query && Object.keys(query).length > 0
				? `${API_ENDPOINTS.transactions.list}?${searchParams.toString()}`
				: API_ENDPOINTS.transactions.list;

		return apiClient.get<TransactionListResponse>(endpoint);
	},

	// Get single transaction by ID
	get: async (id: string): Promise<Transaction> => {
		return apiClient.get<Transaction>(API_ENDPOINTS.transactions.get(id));
	},

	// Create new transaction
	create: async (data: CreateTransactionRequest): Promise<Transaction> => {
		return apiClient.post<Transaction>(API_ENDPOINTS.transactions.create, data);
	},

	// Update existing transaction
	update: async (
		id: string,
		data: UpdateTransactionRequest
	): Promise<Transaction> => {
		return apiClient.put<Transaction>(
			API_ENDPOINTS.transactions.update(id),
			data
		);
	},

	// Delete transaction
	delete: async (id: string): Promise<void> => {
		return apiClient.delete<void>(API_ENDPOINTS.transactions.delete(id));
	},
};

// Expense API functions
export const expenseApi = {
	// Get expense summary with category breakdown
	summary: async (
		startDate?: string,
		endDate?: string
	): Promise<ExpenseSummary> => {
		const searchParams = new URLSearchParams();
		if (startDate) searchParams.append('start_date', startDate);
		if (endDate) searchParams.append('end_date', endDate);

		const endpoint = searchParams.toString()
			? `${API_ENDPOINTS.expenses.summary}?${searchParams.toString()}`
			: API_ENDPOINTS.expenses.summary;

		return apiClient.get<ExpenseSummary>(endpoint);
	},

	// Get expense trends over time
	trends: async (
		period: 'monthly' | 'weekly' = 'monthly'
	): Promise<ExpenseTrends> => {
		return apiClient.get(`${API_ENDPOINTS.expenses.trends}?period=${period}`);
	},

	// Get top spending categories
	topCategories: async (limit: number = 5): Promise<TopCategoriesResponse> => {
		return apiClient.get(
			`${API_ENDPOINTS.expenses.topCategories}?limit=${limit}`
		);
	},

	// Get monthly comparison data
	monthlyComparison: async (): Promise<MonthlyComparison> => {
		return apiClient.get(API_ENDPOINTS.expenses.monthlyComparison);
	},

	// Get all categories with spending totals
	categories: async (): Promise<CategorySummary[]> => {
		return apiClient.get(API_ENDPOINTS.expenses.categories);
	},
};

// Timeline API functions
export const timelineApi = {
	// Get timeline data for charts
	data: async (
		startDate?: string,
		endDate?: string,
		granularity: 'daily' | 'weekly' | 'monthly' = 'monthly'
	): Promise<TimelineData> => {
		const searchParams = new URLSearchParams();
		if (startDate) searchParams.append('start_date', startDate);
		if (endDate) searchParams.append('end_date', endDate);
		searchParams.append('granularity', granularity);

		return apiClient.get<TimelineData>(
			`${API_ENDPOINTS.timeline.data}?${searchParams.toString()}`
		);
	},

	// Get timeline for specific category
	category: async (
		category: string,
		startDate?: string,
		endDate?: string
	): Promise<TimelineData> => {
		const searchParams = new URLSearchParams();
		if (startDate) searchParams.append('start_date', startDate);
		if (endDate) searchParams.append('end_date', endDate);

		const endpoint = searchParams.toString()
			? `${API_ENDPOINTS.timeline.category(
					category
			  )}?${searchParams.toString()}`
			: API_ENDPOINTS.timeline.category(category);

		return apiClient.get<TimelineData>(endpoint);
	},

	// Get cash flow analysis
	cashFlow: async (): Promise<CashFlowAnalysis> => {
		return apiClient.get(API_ENDPOINTS.timeline.cashFlow);
	},

	// Get spending velocity
	velocity: async (): Promise<SpendingVelocity> => {
		return apiClient.get(API_ENDPOINTS.timeline.velocity);
	},

	// Get timeline summary
	summary: async (
		period: 'month' | 'quarter' | 'year' = 'month'
	): Promise<TimelineData> => {
		return apiClient.get(`${API_ENDPOINTS.timeline.summary}?period=${period}`);
	},
};

// AI API functions
export const aiApi = {
	// Get AI financial advice
	advice: async (request: AIAdviceRequest): Promise<AIAdviceResponse> => {
		return apiClient.post<AIAdviceResponse>(API_ENDPOINTS.ai.advice, request);
	},

	// Chat with AI advisor
	chat: async (
		message: string,
		sessionId?: string
	): Promise<AIAdviceResponse> => {
		const payload = {
			message,
			...(sessionId && { session_id: sessionId }),
		};
		return apiClient.post<AIAdviceResponse>(API_ENDPOINTS.ai.chat, payload);
	},

	// Analyze transaction patterns
	analyze: async (
		analysisType: 'spending' | 'income' | 'trends' = 'spending'
	): Promise<AIAnalysisResponse> => {
		return apiClient.post(`${API_ENDPOINTS.ai.analyze}?type=${analysisType}`);
	},

	// Get quick insights
	quickInsights: async (): Promise<QuickInsights> => {
		return apiClient.get(API_ENDPOINTS.ai.quickInsights);
	},

	// Check AI service health
	health: async (): Promise<{ status: string; providers: string[] }> => {
		return apiClient.get(API_ENDPOINTS.ai.health);
	},
};

// Utility functions for common operations
export const apiUtils = {
	// Format date for API calls
	formatDate: (date: Date): string => {
		return date.toISOString().split('T')[0];
	},

	// Get current month date range
	getCurrentMonthRange: () => {
		const now = new Date();
		const start = new Date(now.getFullYear(), now.getMonth(), 1);
		const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);

		return {
			start: apiUtils.formatDate(start),
			end: apiUtils.formatDate(end),
		};
	},

	// Get last N months date range
	getLastMonthsRange: (months: number) => {
		const now = new Date();
		const start = new Date(now.getFullYear(), now.getMonth() - months + 1, 1);
		const end = new Date(now.getFullYear(), now.getMonth() + 1, 0);

		return {
			start: apiUtils.formatDate(start),
			end: apiUtils.formatDate(end),
		};
	},

	// Convert form amount to number (handles commas, etc.)
	parseAmount: (amount: string): number => {
		return parseFloat(amount.replace(/[^\d.-]/g, ''));
	},

	// Format amount for display
	formatAmount: (amount: number, currency: string = 'USD'): string => {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency,
		}).format(amount);
	},
};

// Export all APIs as a single object for convenience
export const api = {
	transactions: transactionApi,
	expenses: expenseApi,
	timeline: timelineApi,
	ai: aiApi,
	utils: apiUtils,
};
