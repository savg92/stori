import { useState, useEffect } from 'react';
import { toast } from 'sonner';

export interface NetworkStatus {
	isOnline: boolean;
	isSlowConnection: boolean;
	connectionType: string | null;
	downlink: number | null;
}

interface NetworkConnection {
	effectiveType?: string;
	downlink?: number;
	addEventListener?: (type: string, listener: EventListener) => void;
	removeEventListener?: (type: string, listener: EventListener) => void;
}

interface NavigatorWithConnection extends Navigator {
	connection?: NetworkConnection;
	mozConnection?: NetworkConnection;
	webkitConnection?: NetworkConnection;
}

export function useNetworkStatus() {
	const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
		isOnline: navigator.onLine,
		isSlowConnection: false,
		connectionType: null,
		downlink: null,
	});

	const [wasOffline, setWasOffline] = useState(false);

	useEffect(() => {
		function updateNetworkStatus() {
			const nav = navigator as NavigatorWithConnection;
			const connection =
				nav.connection || nav.mozConnection || nav.webkitConnection;

			const isOnline = navigator.onLine;
			const connectionType = connection?.effectiveType || null;
			const downlink = connection?.downlink || null;

			// Consider connection slow if effective type is 'slow-2g' or '2g'
			// or if downlink is less than 1.5 Mbps
			const isSlowConnection =
				connectionType === 'slow-2g' ||
				connectionType === '2g' ||
				(downlink && downlink < 1.5);

			setNetworkStatus({
				isOnline,
				isSlowConnection: isSlowConnection || false,
				connectionType,
				downlink,
			});

			// Show toast notifications for network status changes
			if (!isOnline) {
				setWasOffline(true);
				toast.error('You are offline', {
					description: 'Some features may not work properly.',
					duration: 5000,
					id: 'offline-status',
				});
			} else if (wasOffline) {
				setWasOffline(false);
				toast.success('You are back online', {
					description: 'All features are now available.',
					duration: 3000,
					id: 'online-status',
				});
			} else if (isSlowConnection) {
				toast.warning('Slow connection detected', {
					description: 'Some features may take longer to load.',
					duration: 3000,
					id: 'slow-connection',
				});
			}
		}

		// Update status immediately
		updateNetworkStatus();

		// Listen for network status changes
		window.addEventListener('online', updateNetworkStatus);
		window.addEventListener('offline', updateNetworkStatus);

		// Listen for connection changes (if supported)
		const nav = navigator as NavigatorWithConnection;
		const connection =
			nav.connection || nav.mozConnection || nav.webkitConnection;

		if (connection && connection.addEventListener) {
			connection.addEventListener('change', updateNetworkStatus);
		}

		return () => {
			window.removeEventListener('online', updateNetworkStatus);
			window.removeEventListener('offline', updateNetworkStatus);
			if (connection && connection.removeEventListener) {
				connection.removeEventListener('change', updateNetworkStatus);
			}
		};
	}, [wasOffline]);

	return networkStatus;
}

export function useOfflineQueue() {
	const [queuedActions, setQueuedActions] = useState<
		Array<{
			id: string;
			action: () => Promise<void>;
			description: string;
			timestamp: number;
		}>
	>([]);

	const { isOnline } = useNetworkStatus();

	const addToQueue = (action: () => Promise<void>, description: string) => {
		const id = `${Date.now()}-${Math.random()}`;
		setQueuedActions((prev) => [
			...prev,
			{
				id,
				action,
				description,
				timestamp: Date.now(),
			},
		]);

		toast.info("Action queued for when you're back online", {
			description,
			duration: 3000,
		});

		return id;
	};

	const removeFromQueue = (id: string) => {
		setQueuedActions((prev) => prev.filter((item) => item.id !== id));
	};

	const clearQueue = () => {
		setQueuedActions([]);
	};

	// Process queued actions when coming back online
	useEffect(() => {
		if (isOnline && queuedActions.length > 0) {
			toast.info(`Processing ${queuedActions.length} queued actions...`);

			const processQueue = async () => {
				const results = await Promise.allSettled(
					queuedActions.map(async (item) => {
						try {
							await item.action();
							return { success: true, description: item.description };
						} catch (error) {
							return {
								success: false,
								description: item.description,
								error,
							};
						}
					})
				);

				const successful = results.filter(
					(r) => r.status === 'fulfilled' && r.value.success
				).length;
				const failed = results.length - successful;

				if (successful > 0) {
					toast.success(`${successful} queued actions completed successfully`);
				}

				if (failed > 0) {
					toast.error(`${failed} queued actions failed`, {
						description: 'You may need to retry these actions manually.',
					});
				}

				clearQueue();
			};

			processQueue();
		}
	}, [isOnline, queuedActions]);

	return {
		queuedActions,
		addToQueue,
		removeFromQueue,
		clearQueue,
		hasQueuedActions: queuedActions.length > 0,
	};
}
