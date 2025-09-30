import { QueryClient } from '@tanstack/react-query';

// Optimized query client configuration for performance
export const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			// Increase stale time to reduce unnecessary refetches
			staleTime: 5 * 60 * 1000, // 5 minutes
			// Keep data in cache longer
			gcTime: 10 * 60 * 1000, // 10 minutes (was cacheTime)
			// Don't refetch on window focus for better UX
			refetchOnWindowFocus: false,
			// Don't refetch on mount if data is fresh
			refetchOnMount: false,
			// Retry failed requests with exponential backoff
			retry: (failureCount, error: unknown) => {
				// Don't retry 4xx errors (client errors)
				const httpError = error as { response?: { status?: number } };
				if (
					httpError?.response?.status &&
					httpError.response.status >= 400 &&
					httpError.response.status < 500
				) {
					return false;
				}
				// Retry up to 3 times for other errors
				return failureCount < 3;
			},
			retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
		},
		mutations: {
			// Show optimistic updates
			retry: false,
			// Network error handling - log only in development
			onError: (error: unknown) => {
				if (import.meta.env?.DEV) {
					console.error('Mutation error:', error);
				}
			},
		},
	},
});

// Prefetch commonly used data
export function prefetchCommonData() {
	// Prefetch expense summary
	queryClient.prefetchQuery({
		queryKey: ['expenses', 'summary'],
		queryFn: () => fetch('/api/expenses/summary').then((res) => res.json()),
		staleTime: 2 * 60 * 1000, // 2 minutes
	});

	// Prefetch recent transactions
	queryClient.prefetchQuery({
		queryKey: ['transactions', 'list', {}],
		queryFn: () => fetch('/api/transactions').then((res) => res.json()),
		staleTime: 1 * 60 * 1000, // 1 minute
	});
}
