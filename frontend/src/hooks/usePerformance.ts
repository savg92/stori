import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';

/**
 * Hook to cleanup unused query cache data to prevent memory leaks
 * Should be used in components that fetch large amounts of data
 */
export function useMemoryOptimization() {
	const queryClient = useQueryClient();
	const timeoutRef = useRef<NodeJS.Timeout | null>(null);

	useEffect(() => {
		// Cleanup old cache data every 10 minutes
		timeoutRef.current = setInterval(() => {
			queryClient.clear(); // Clear all cache
			// Or more selective cleanup:
			// queryClient.removeQueries({ stale: true });
		}, 10 * 60 * 1000);

		return () => {
			if (timeoutRef.current) {
				clearInterval(timeoutRef.current);
			}
		};
	}, [queryClient]);
}

/**
 * Hook to prefetch data based on user interaction
 */
export function usePrefetch() {
	const queryClient = useQueryClient();

	const prefetchTransactions = () => {
		queryClient.prefetchQuery({
			queryKey: ['transactions', 'list', {}],
			queryFn: () => fetch('/api/transactions').then((res) => res.json()),
			staleTime: 2 * 60 * 1000,
		});
	};

	const prefetchAnalytics = () => {
		queryClient.prefetchQuery({
			queryKey: ['expenses', 'summary'],
			queryFn: () => fetch('/api/expenses/summary').then((res) => res.json()),
			staleTime: 2 * 60 * 1000,
		});
	};

	return {
		prefetchTransactions,
		prefetchAnalytics,
	};
}

/**
 * Hook to handle image optimization
 */
export function useImageOptimization() {
	const preloadImage = (src: string) => {
		const img = new Image();
		img.src = src;
	};

	const lazyLoadImages = () => {
		if ('IntersectionObserver' in window) {
			const imageObserver = new IntersectionObserver((entries) => {
				entries.forEach((entry) => {
					if (entry.isIntersecting) {
						const img = entry.target as HTMLImageElement;
						img.src = img.dataset.src || '';
						img.classList.remove('lazy');
						imageObserver.unobserve(img);
					}
				});
			});

			document.querySelectorAll('img[data-src]').forEach((img) => {
				imageObserver.observe(img);
			});

			return () => imageObserver.disconnect();
		}
	};

	return {
		preloadImage,
		lazyLoadImages,
	};
}
