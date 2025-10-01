import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useLocation } from 'react-router-dom';
import { queryKeys } from './useApi';

/**
 * Hook to invalidate dashboard-related queries when navigating to ensure fresh data
 */
export function useDashboardDataRefresh() {
	const queryClient = useQueryClient();
	const location = useLocation();

	useEffect(() => {
		// Only invalidate when navigating to the dashboard (root path)
		if (location.pathname === '/') {
			// Invalidate key dashboard queries to ensure fresh data
			queryClient.invalidateQueries({
				queryKey: queryKeys.expenses.all,
				exact: false, // This will invalidate all expense-related queries
			});
			
			queryClient.invalidateQueries({
				queryKey: queryKeys.timeline.all,
				exact: false, // This will invalidate all timeline-related queries
			});

			queryClient.invalidateQueries({
				queryKey: queryKeys.transactions.lists(),
				exact: false, // This will invalidate transaction lists
			});
		}
	}, [location.pathname, queryClient]);
}

/**
 * Hook to ensure dashboard queries are refreshed when needed
 * Can be used in components that show financial data
 */
export function useEnsureFreshData() {
	const queryClient = useQueryClient();

	const refreshDashboardData = () => {
		// Force refetch of critical dashboard data
		queryClient.refetchQueries({
			queryKey: queryKeys.expenses.all,
			exact: false,
		});
		
		queryClient.refetchQueries({
			queryKey: queryKeys.timeline.all,
			exact: false,
		});
	};

	return { refreshDashboardData };
}