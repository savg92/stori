import { useEffect, useRef } from 'react';

/**
 * Hook for managing modal/dialog focus
 */
export function useModalFocus(
	isOpen: boolean,
	containerRef: React.RefObject<HTMLElement | null>
) {
	useEffect(() => {
		if (isOpen && containerRef.current) {
			const container = containerRef.current;
			const focusableElements = container.querySelectorAll(
				'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
			);
			const firstElement = focusableElements[0] as HTMLElement;
			const lastElement = focusableElements[
				focusableElements.length - 1
			] as HTMLElement;

			const handleKeyDown = (e: KeyboardEvent) => {
				if (e.key === 'Tab') {
					if (e.shiftKey) {
						if (document.activeElement === firstElement) {
							lastElement.focus();
							e.preventDefault();
						}
					} else {
						if (document.activeElement === lastElement) {
							firstElement.focus();
							e.preventDefault();
						}
					}
				}
			};

			container.addEventListener('keydown', handleKeyDown);

			// Focus first element
			if (firstElement) {
				setTimeout(() => firstElement.focus(), 100);
			}

			return () => {
				container.removeEventListener('keydown', handleKeyDown);
			};
		}
	}, [isOpen, containerRef]);
}

/**
 * Hook for screen reader announcements
 */
export function useScreenReader() {
	const announceRef = useRef<HTMLDivElement>(null);

	const announce = (
		message: string,
		priority: 'polite' | 'assertive' = 'polite'
	) => {
		if (announceRef.current) {
			announceRef.current.setAttribute('aria-live', priority);
			announceRef.current.textContent = message;

			// Clear after announcement to avoid repetition
			setTimeout(() => {
				if (announceRef.current) {
					announceRef.current.textContent = '';
				}
			}, 1000);
		}
	};

	return { announce, announceRef };
}

/**
 * Hook for keyboard navigation in lists/grids
 */
export function useKeyboardNavigation(
	itemCount: number,
	onSelect?: (index: number) => void
) {
	const currentIndex = useRef(0);

	const handleKeyDown = (e: KeyboardEvent) => {
		switch (e.key) {
			case 'ArrowDown':
				e.preventDefault();
				currentIndex.current = Math.min(
					currentIndex.current + 1,
					itemCount - 1
				);
				break;
			case 'ArrowUp':
				e.preventDefault();
				currentIndex.current = Math.max(currentIndex.current - 1, 0);
				break;
			case 'Home':
				e.preventDefault();
				currentIndex.current = 0;
				break;
			case 'End':
				e.preventDefault();
				currentIndex.current = itemCount - 1;
				break;
			case 'Enter':
			case ' ':
				e.preventDefault();
				if (onSelect) {
					onSelect(currentIndex.current);
				}
				break;
		}
	};

	return { currentIndex: currentIndex.current, handleKeyDown };
}

/**
 * Hook for focus trap utility functions
 */
export function useFocusTrap() {
	const trapFocus = (element: HTMLElement) => {
		const focusableElements = element.querySelectorAll(
			'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
		);
		const firstElement = focusableElements[0] as HTMLElement;
		const lastElement = focusableElements[
			focusableElements.length - 1
		] as HTMLElement;

		const handleKeyDown = (e: KeyboardEvent) => {
			if (e.key === 'Tab') {
				if (e.shiftKey) {
					if (document.activeElement === firstElement) {
						lastElement.focus();
						e.preventDefault();
					}
				} else {
					if (document.activeElement === lastElement) {
						firstElement.focus();
						e.preventDefault();
					}
				}
			}

			if (e.key === 'Escape') {
				// Let parent component handle escape
				element.dispatchEvent(new CustomEvent('escape-key'));
			}
		};

		element.addEventListener('keydown', handleKeyDown);
		return () => element.removeEventListener('keydown', handleKeyDown);
	};

	return { trapFocus };
}
