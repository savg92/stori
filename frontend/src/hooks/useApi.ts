// React Query hooks for Stori Expense Tracker API
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from '../lib/toast';
import { api } from '../services/api';
import type {
	Transaction,
	CreateTransactionRequest,
	UpdateTransactionRequest,
	TransactionQuery,
	TransactionFilters,
	AIAdviceRequest,
	TransactionListResponse,
} from '../types/api';

// Query keys for React Query cache management
export const queryKeys = {
	transactions: {
		all: ['transactions'] as const,
		lists: () => [...queryKeys.transactions.all, 'list'] as const,
		list: (filters: TransactionQuery) =>
			[...queryKeys.transactions.lists(), filters] as const,
		details: () => [...queryKeys.transactions.all, 'detail'] as const,
		detail: (id: string) => [...queryKeys.transactions.details(), id] as const,
	},
	expenses: {
		all: ['expenses'] as const,
		summary: (dateRange?: { start?: string; end?: string }) =>
			[...queryKeys.expenses.all, 'summary', dateRange] as const,
		trends: (period: 'monthly' | 'weekly') =>
			[...queryKeys.expenses.all, 'trends', period] as const,
		categories: () => [...queryKeys.expenses.all, 'categories'] as const,
	},
	timeline: {
		all: ['timeline'] as const,
		data: (params: {
			startDate?: string;
			endDate?: string;
			granularity?: string;
		}) => [...queryKeys.timeline.all, 'data', params] as const,
		summary: (period: string) =>
			[...queryKeys.timeline.all, 'summary', period] as const,
	},
	ai: {
		all: ['ai'] as const,
		health: () => [...queryKeys.ai.all, 'health'] as const,
		insights: () => [...queryKeys.ai.all, 'insights'] as const,
	},
} as const;

// Transaction hooks
export const useTransactions = (query?: TransactionQuery) => {
	return useQuery({
		queryKey: queryKeys.transactions.list(query || {}),
		queryFn: () => api.transactions.list(query),
		staleTime: 5 * 60 * 1000, // 5 minutes
		refetchOnWindowFocus: false,
	});
};

export const useTransaction = (id: string) => {
	return useQuery({
		queryKey: queryKeys.transactions.detail(id),
		queryFn: () => api.transactions.get(id),
		enabled: !!id,
		staleTime: 5 * 60 * 1000,
	});
};

export const useCreateTransaction = () => {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (data: CreateTransactionRequest) =>
			api.transactions.create(data),
		onSuccess: () => {
			// Invalidate and refetch transaction lists
			queryClient.invalidateQueries({
				queryKey: queryKeys.transactions.lists(),
			});
			// Invalidate expense and timeline data as well
			queryClient.invalidateQueries({ queryKey: queryKeys.expenses.all });
			queryClient.invalidateQueries({ queryKey: queryKeys.timeline.all });

			toast.success('Transaction created successfully!');
		},
		onError: (error: Error) => {
			toast.error(error.message || 'Failed to create transaction');
		},
	});
};

export const useUpdateTransaction = () => {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({
			id,
			data,
		}: {
			id: string;
			data: UpdateTransactionRequest;
		}) => api.transactions.update(id, data),
		onSuccess: (updatedTransaction) => {
			// Update the specific transaction in cache
			queryClient.setQueryData(
				queryKeys.transactions.detail(updatedTransaction.id),
				updatedTransaction
			);
			// Invalidate lists to reflect changes
			queryClient.invalidateQueries({
				queryKey: queryKeys.transactions.lists(),
			});
			queryClient.invalidateQueries({ queryKey: queryKeys.expenses.all });
			queryClient.invalidateQueries({ queryKey: queryKeys.timeline.all });

			toast.success('Transaction updated successfully!');
		},
		onError: (error: Error) => {
			toast.error(error.message || 'Failed to update transaction');
		},
	});
};

export const useDeleteTransaction = () => {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (id: string) => api.transactions.delete(id),
		onSuccess: (_, deletedId) => {
			// Remove from cache
			queryClient.removeQueries({
				queryKey: queryKeys.transactions.detail(deletedId),
			});
			// Invalidate lists
			queryClient.invalidateQueries({
				queryKey: queryKeys.transactions.lists(),
			});
			queryClient.invalidateQueries({ queryKey: queryKeys.expenses.all });
			queryClient.invalidateQueries({ queryKey: queryKeys.timeline.all });

			toast.success('Transaction deleted successfully!');
		},
		onError: (error: Error) => {
			toast.error(error.message || 'Failed to delete transaction');
		},
	});
};

// Expense hooks
export const useExpenseSummary = (startDate?: string, endDate?: string) => {
	return useQuery({
		queryKey: queryKeys.expenses.summary({ start: startDate, end: endDate }),
		queryFn: () => api.expenses.summary(startDate, endDate),
		staleTime: 5 * 60 * 1000,
		refetchOnWindowFocus: false,
	});
};

export const useExpenseTrends = (period: 'monthly' | 'weekly' = 'monthly') => {
	return useQuery({
		queryKey: queryKeys.expenses.trends(period),
		queryFn: () => api.expenses.trends(period),
		staleTime: 10 * 60 * 1000, // 10 minutes for trends
	});
};

export const useExpenseCategories = () => {
	return useQuery({
		queryKey: queryKeys.expenses.categories(),
		queryFn: () => api.expenses.categories(),
		staleTime: 15 * 60 * 1000, // 15 minutes for categories
	});
};

// Timeline hooks
export const useTimelineData = (
	startDate?: string,
	endDate?: string,
	granularity: 'daily' | 'weekly' | 'monthly' = 'monthly'
) => {
	return useQuery({
		queryKey: queryKeys.timeline.data({ startDate, endDate, granularity }),
		queryFn: () => api.timeline.data(startDate, endDate, granularity),
		staleTime: 5 * 60 * 1000,
		refetchOnWindowFocus: false,
	});
};

export const useTimelineSummary = (
	period: 'month' | 'quarter' | 'year' = 'month'
) => {
	return useQuery({
		queryKey: queryKeys.timeline.summary(period),
		queryFn: () => api.timeline.summary(period),
		staleTime: 10 * 60 * 1000,
	});
};

// AI hooks
export const useAIAdvice = () => {
	return useMutation({
		mutationFn: (request: AIAdviceRequest) => api.ai.advice(request),
		onError: (error: Error) => {
			toast.error(error.message || 'Failed to get AI advice');
		},
	});
};

export const useAIChat = () => {
	return useMutation({
		mutationFn: ({
			message,
			sessionId,
		}: {
			message: string;
			sessionId?: string;
		}) => api.ai.chat(message, sessionId),
		onError: (error: Error) => {
			toast.error(error.message || 'Failed to send message');
		},
	});
};

export const useAIHealth = () => {
	return useQuery({
		queryKey: queryKeys.ai.health(),
		queryFn: () => api.ai.health(),
		staleTime: 2 * 60 * 1000, // 2 minutes
		retry: 1, // Only retry once for health checks
	});
};

export const useQuickInsights = () => {
	return useQuery({
		queryKey: queryKeys.ai.insights(),
		queryFn: () => api.ai.quickInsights(),
		staleTime: 15 * 60 * 1000, // 15 minutes for insights
		refetchOnWindowFocus: false,
	});
};

// Utility hooks for common patterns
export const useCurrentMonthSummary = () => {
	const { start, end } = api.utils.getCurrentMonthRange();
	return useExpenseSummary(start, end);
};

export const useCurrentMonthTimeline = () => {
	const { start, end } = api.utils.getCurrentMonthRange();
	return useTimelineData(start, end, 'daily');
};

// Hook for recent transactions (common dashboard need)
export const useRecentTransactions = (limit = 10) => {
	return useTransactions({ limit, offset: 0 });
};

// Hook for transaction filters (for transaction list page)
export const useTransactionFilters = (filters: TransactionFilters) => {
	const query: TransactionQuery = {
		type: filters.type,
		category: filters.category,
		start_date: filters.dateRange?.start,
		end_date: filters.dateRange?.end,
		min_amount: filters.amountRange?.min,
		max_amount: filters.amountRange?.max,
		search: filters.search,
	};

	return useTransactions(query);
};

// Optimistic update utilities
export const useOptimisticTransactionUpdate = () => {
	const queryClient = useQueryClient();

	const updateOptimistically = (
		transactionId: string,
		updatedData: Partial<Transaction>
	) => {
		// Update the specific transaction in cache optimistically
		queryClient.setQueryData(
			queryKeys.transactions.detail(transactionId),
			(old: Transaction | undefined) => {
				if (!old) return undefined;
				return { ...old, ...updatedData };
			}
		);

		// Update in transaction lists as well
		queryClient.setQueriesData(
			{ queryKey: queryKeys.transactions.lists() },
			(old: TransactionListResponse | undefined) => {
				if (!old?.items) return old;
				return {
					...old,
					items: old.items.map((transaction: Transaction) =>
						transaction.id === transactionId
							? { ...transaction, ...updatedData }
							: transaction
					),
				};
			}
		);
	};

	return { updateOptimistically };
};

// Prefetch utilities for better UX
export const usePrefetchTransaction = () => {
	const queryClient = useQueryClient();

	return (id: string) => {
		queryClient.prefetchQuery({
			queryKey: queryKeys.transactions.detail(id),
			queryFn: () => api.transactions.get(id),
			staleTime: 5 * 60 * 1000,
		});
	};
};
