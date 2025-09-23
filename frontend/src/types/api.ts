// API Response and Request Types for Stori Expense Tracker

// Base types matching backend models
export type TransactionType = 'income' | 'expense';

export type IncomeCategory =
	| 'salary'
	| 'freelance'
	| 'investment'
	| 'business'
	| 'gift'
	| 'rental'
	| 'dividend'
	| 'bonus'
	| 'refund'
	| 'other_income';

export type ExpenseCategory =
	| 'food_dining'
	| 'transportation'
	| 'entertainment'
	| 'shopping'
	| 'bills_utilities'
	| 'healthcare'
	| 'education'
	| 'travel'
	| 'groceries'
	| 'fitness'
	| 'subscriptions'
	| 'insurance'
	| 'childcare'
	| 'other_expense';

// Transaction entity from backend
export interface Transaction {
	id: string;
	user_id: string;
	type: TransactionType;
	category: IncomeCategory | ExpenseCategory;
	amount: number;
	description: string;
	date: string; // ISO date string
	created_at: string;
	updated_at: string;
}

// Transaction creation request
export interface CreateTransactionRequest {
	type: TransactionType;
	category: IncomeCategory | ExpenseCategory;
	amount: number;
	description: string;
	date: string; // ISO date string
}

// Transaction update request
export interface UpdateTransactionRequest {
	type?: TransactionType;
	category?: IncomeCategory | ExpenseCategory;
	amount?: number;
	description?: string;
	date?: string;
}

// Transaction query parameters
export interface TransactionQuery {
	limit?: number;
	offset?: number;
	type?: TransactionType;
	category?: string;
	start_date?: string;
	end_date?: string;
	min_amount?: number;
	max_amount?: number;
	search?: string;
}

// Paginated response wrapper
export interface PaginatedResponse<T> {
	items: T[];
	total: number;
	limit: number;
	offset: number;
	has_next: boolean;
	has_previous: boolean;
}

// Transaction list response
export type TransactionListResponse = PaginatedResponse<Transaction>;

// Expense Summary Response
export interface ExpenseSummary {
	total_expenses: number;
	total_income: number;
	net_income: number;
	expense_categories: CategorySummary[];
	income_categories: CategorySummary[];
	period_start: string;
	period_end: string;
}

export interface CategorySummary {
	category: string;
	total_amount: number;
	transaction_count: number;
	percentage: number;
	avg_amount: number;
}

// Timeline Response
export interface TimelineData {
	data_points: TimelinePoint[];
	summary: TimelineSummary;
	period_start: string;
	period_end: string;
}

export interface TimelinePoint {
	date: string;
	income: number;
	expenses: number;
	net_income: number;
	transaction_count: number;
}

export interface TimelineSummary {
	total_income: number;
	total_expenses: number;
	net_income: number;
	avg_monthly_income: number;
	avg_monthly_expenses: number;
	best_month: string;
	worst_month: string;
}

// AI Advice Types
export interface AIAdviceRequest {
	message: string;
	context?: 'general' | 'specific' | 'planning';
	include_transaction_data?: boolean;
}

export interface AIAdviceResponse {
	response: string;
	confidence: number;
	context_used: {
		transaction_count: number;
		date_range: string;
		categories_analyzed: string[];
	};
	suggestions: string[];
	session_id: string;
}

// Error response from backend
export interface APIError {
	detail: string;
	status_code: number;
	error_type?: string;
}

// API response wrapper for better error handling
export type APIResponse<T> =
	| {
			success: true;
			data: T;
	  }
	| {
			success: false;
			error: APIError;
	  };

// Query filter types for frontend components
export interface TransactionFilters {
	type?: TransactionType;
	category?: string;
	dateRange?: {
		start: string;
		end: string;
	};
	amountRange?: {
		min: number;
		max: number;
	};
	search?: string;
}

// Form data types for components
export interface TransactionFormData {
	type: TransactionType;
	category: IncomeCategory | ExpenseCategory;
	amount: string; // String for form input, converted to number
	description: string;
	date: string;
}

// Category options for dropdowns
export interface CategoryOption {
	value: IncomeCategory | ExpenseCategory;
	label: string;
	type: TransactionType;
}

// Chart data types for visualization
export interface ChartDataPoint {
	name: string;
	value: number;
	color?: string;
}

export interface TimelineChartData {
	date: string;
	income: number;
	expenses: number;
	net: number;
}

// Additional API response types
export interface ExpenseTrends {
	trends: TrendPoint[];
	period: 'monthly' | 'weekly';
	growth_rate: number;
	trend_direction: 'up' | 'down' | 'stable';
}

export interface TrendPoint {
	period: string;
	amount: number;
	transaction_count: number;
	change_percentage: number;
}

export interface TopCategoriesResponse {
	categories: CategoryRanking[];
	total_analyzed: number;
	period_start: string;
	period_end: string;
}

export interface CategoryRanking {
	category: string;
	total_amount: number;
	percentage: number;
	transaction_count: number;
	rank: number;
}

export interface MonthlyComparison {
	current_month: MonthData;
	previous_month: MonthData;
	year_over_year: MonthData;
	comparison: {
		month_over_month_change: number;
		year_over_year_change: number;
		trend: 'improving' | 'declining' | 'stable';
	};
}

export interface MonthData {
	total_income: number;
	total_expenses: number;
	net_income: number;
	transaction_count: number;
	top_category: string;
}

export interface CashFlowAnalysis {
	cash_flow: CashFlowPoint[];
	summary: {
		total_inflow: number;
		total_outflow: number;
		net_flow: number;
		average_monthly_flow: number;
	};
}

export interface CashFlowPoint {
	date: string;
	inflow: number;
	outflow: number;
	net_flow: number;
	running_balance: number;
}

export interface SpendingVelocity {
	velocity_data: VelocityPoint[];
	metrics: {
		average_daily_spend: number;
		peak_spending_day: string;
		lowest_spending_day: string;
		velocity_trend: 'accelerating' | 'decelerating' | 'stable';
	};
}

export interface VelocityPoint {
	date: string;
	daily_amount: number;
	cumulative_amount: number;
	velocity_score: number;
}

export interface AIAnalysisResponse {
	analysis_type: 'spending' | 'income' | 'trends';
	insights: string[];
	recommendations: string[];
	patterns: PatternInsight[];
	confidence_score: number;
}

export interface PatternInsight {
	pattern_type: string;
	description: string;
	significance: 'high' | 'medium' | 'low';
	data_points: number;
}

export interface QuickInsights {
	insights: InsightItem[];
	generated_at: string;
	data_freshness: string;
}

export interface InsightItem {
	title: string;
	description: string;
	category: 'spending' | 'income' | 'trends' | 'opportunities';
	priority: 'high' | 'medium' | 'low';
	actionable: boolean;
}

// Loading and error states for React Query
export interface LoadingState {
	isLoading: boolean;
	error: string | null;
}
