export const API_BASE_URL =
	import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Frontend now uses live API endpoints exclusively
export const isDevelopment = () => import.meta.env.DEV;

export const API_ENDPOINTS = {
	// Transactions - Live API endpoints
	transactions: {
		list: '/api/transactions',
		create: '/api/transactions',
		get: (id: string) => `/api/transactions/${id}`,
		update: (id: string) => `/api/transactions/${id}`,
		delete: (id: string) => `/api/transactions/${id}`,
	},

	// Expenses - Live API endpoints
	expenses: {
		summary: '/api/expenses/summary',
		trends: '/api/expenses/trends',
		topCategories: '/api/expenses/categories/top',
		monthlyComparison: '/api/expenses/comparison/monthly',
		categories: '/api/expenses/categories',
	},

	// Timeline - Live API endpoints
	timeline: {
		data: '/api/timeline',
		category: (category: string) => `/api/timeline/category/${category}`,
		cashFlow: '/api/timeline/cash-flow',
		velocity: '/api/timeline/velocity',
		summary: '/api/timeline/summary',
	},

	// AI
	ai: {
		advice: '/api/ai/advice',
		chat: '/api/ai/chat',
		analyze: '/api/ai/analyze',
		quickInsights: '/api/ai/insights/quick',
		health: '/api/ai/health',
	},
} as const;

export const DEFAULT_PAGINATION = {
	limit: 20,
	offset: 0,
} as const;

export const TRANSACTION_TYPES = ['income', 'expense'] as const;
export const DEFAULT_CATEGORIES = {
	income: ['Salary', 'Freelance', 'Investment', 'Gift', 'Other Income'],
	expense: [
		'Food',
		'Transportation',
		'Entertainment',
		'Shopping',
		'Bills',
		'Healthcare',
		'Other',
	],
} as const;
