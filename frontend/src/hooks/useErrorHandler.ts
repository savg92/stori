import { useCallback } from 'react';
import { toast } from 'sonner';

interface ErrorDetails {
	message: string;
	code?: string;
	statusCode?: number;
	retryable?: boolean;
}

interface ErrorHandlerOptions {
	showToast?: boolean;
	logError?: boolean;
	retryable?: boolean;
	customMessage?: string;
}

export function useErrorHandler() {
	const handleError = useCallback(
		(error: unknown, options: ErrorHandlerOptions = {}): ErrorDetails => {
			const {
				showToast = true,
				logError = true,
				retryable = false,
				customMessage,
			} = options;

			// Parse error into structured format
			const errorDetails = parseError(error);

			// Add retryable flag from options
			errorDetails.retryable = retryable || isRetryableError(errorDetails);

			// Log error in development
			if (logError && import.meta.env.DEV) {
				console.error('Error handled:', {
					original: error,
					parsed: errorDetails,
					options,
				});
			}

			// Show user-friendly toast notification
			if (showToast) {
				const displayMessage =
					customMessage || getUserFriendlyMessage(errorDetails);
				toast.error(displayMessage, {
					description: errorDetails.retryable
						? 'Please try again in a moment.'
						: undefined,
					action: errorDetails.retryable
						? {
								label: 'Retry',
								onClick: () => {
									// The retry action should be handled by the calling component
									toast.dismiss();
								},
						  }
						: undefined,
				});
			}

			return errorDetails;
		},
		[]
	);

	const handleApiError = useCallback(
		(error: unknown, endpoint?: string) => {
			return handleError(error, {
				showToast: true,
				logError: true,
				retryable: true,
				customMessage: endpoint
					? `Failed to ${getActionFromEndpoint(endpoint)}`
					: undefined,
			});
		},
		[handleError]
	);

	const handleFormError = useCallback(
		(error: unknown, formName?: string) => {
			return handleError(error, {
				showToast: true,
				logError: true,
				retryable: false,
				customMessage: formName
					? `Failed to submit ${formName}`
					: 'Form submission failed',
			});
		},
		[handleError]
	);

	const handleAuthError = useCallback(
		(error: unknown) => {
			return handleError(error, {
				showToast: true,
				logError: true,
				retryable: false,
				customMessage: getAuthErrorMessage(error),
			});
		},
		[handleError]
	);

	return {
		handleError,
		handleApiError,
		handleFormError,
		handleAuthError,
	};
}

interface ErrorWithCode extends Error {
	code?: string;
	status?: number;
	statusCode?: number;
}

interface HttpError {
	response?: {
		data?: { message?: string; code?: string };
		status?: number;
	};
	message?: string;
	code?: string;
	status?: number;
	statusCode?: number;
}

function parseError(error: unknown): ErrorDetails {
	// Handle different error types
	if (error instanceof Error) {
		const errorWithCode = error as ErrorWithCode;
		return {
			message: error.message,
			code: errorWithCode.code,
			statusCode: errorWithCode.status || errorWithCode.statusCode,
		};
	}

	// Handle HTTP response errors
	if (typeof error === 'object' && error !== null) {
		const errorObj = error as HttpError;

		if (errorObj.response) {
			// Axios-style error
			return {
				message:
					errorObj.response.data?.message ||
					errorObj.message ||
					'Request failed',
				code: errorObj.response.data?.code || errorObj.code,
				statusCode: errorObj.response.status,
			};
		}

		if (errorObj.status || errorObj.statusCode) {
			// Fetch-style error
			return {
				message:
					errorObj.message || `HTTP ${errorObj.status || errorObj.statusCode}`,
				statusCode: errorObj.status || errorObj.statusCode,
			};
		}

		if (errorObj.message) {
			return {
				message: errorObj.message,
				code: errorObj.code,
			};
		}
	}

	// Handle string errors
	if (typeof error === 'string') {
		return { message: error };
	}

	// Fallback for unknown error types
	return { message: 'An unexpected error occurred' };
}

function isRetryableError(errorDetails: ErrorDetails): boolean {
	const { statusCode, code } = errorDetails;

	// Network errors are typically retryable
	if (code === 'NETWORK_ERROR' || code === 'TIMEOUT') {
		return true;
	}

	// HTTP status codes that are retryable
	if (statusCode) {
		// 5xx server errors are retryable
		if (statusCode >= 500) return true;

		// Some 4xx errors are retryable
		if (statusCode === 408 || statusCode === 429) return true;

		// Rate limiting
		if (statusCode === 429) return true;
	}

	return false;
}

function getUserFriendlyMessage(errorDetails: ErrorDetails): string {
	const { message, statusCode } = errorDetails;

	// Handle common HTTP status codes
	switch (statusCode) {
		case 400:
			return 'Invalid request. Please check your input and try again.';
		case 401:
			return 'Please log in to continue.';
		case 403:
			return "You don't have permission to perform this action.";
		case 404:
			return 'The requested resource was not found.';
		case 408:
			return 'Request timed out. Please try again.';
		case 429:
			return 'Too many requests. Please wait a moment and try again.';
		case 500:
			return 'Server error. Please try again later.';
		case 502:
		case 503:
		case 504:
			return 'Service temporarily unavailable. Please try again later.';
		default:
			// Return the original message if it's user-friendly, otherwise a generic message
			return isUserFriendlyMessage(message)
				? message
				: 'Something went wrong. Please try again.';
	}
}

function isUserFriendlyMessage(message: string): boolean {
	// Check if the message contains technical jargon or is too generic
	const technicalTerms = [
		'undefined is not a function',
		'cannot read property',
		'null is not an object',
		'network error',
		'cors',
		'xhr',
		'fetch',
		'promise',
		'async',
	];

	const lowerMessage = message.toLowerCase();
	return (
		!technicalTerms.some((term) => lowerMessage.includes(term)) &&
		message.length > 5 &&
		message.length < 200
	);
}

function getActionFromEndpoint(endpoint: string): string {
	if (endpoint.includes('/transactions')) {
		if (endpoint.includes('POST')) return 'create transaction';
		if (endpoint.includes('PUT') || endpoint.includes('PATCH'))
			return 'update transaction';
		if (endpoint.includes('DELETE')) return 'delete transaction';
		return 'load transactions';
	}

	if (endpoint.includes('/auth')) {
		if (endpoint.includes('login')) return 'log in';
		if (endpoint.includes('signup')) return 'sign up';
		if (endpoint.includes('logout')) return 'log out';
		return 'authenticate';
	}

	if (endpoint.includes('/ai')) {
		return 'get AI advice';
	}

	return 'complete request';
}

function getAuthErrorMessage(error: unknown): string {
	const errorDetails = parseError(error);
	const message = errorDetails.message.toLowerCase();

	if (message.includes('email') && message.includes('already')) {
		return 'An account with this email already exists. Try logging in instead.';
	}

	if (
		message.includes('invalid') &&
		(message.includes('email') || message.includes('password'))
	) {
		return 'Invalid email or password. Please check your credentials and try again.';
	}

	if (message.includes('weak') && message.includes('password')) {
		return 'Password is too weak. Please use at least 8 characters with a mix of letters and numbers.';
	}

	if (
		message.includes('email') &&
		message.includes('not') &&
		message.includes('confirmed')
	) {
		return 'Please check your email and click the confirmation link to activate your account.';
	}

	if (message.includes('rate') && message.includes('limit')) {
		return 'Too many login attempts. Please wait a few minutes and try again.';
	}

	return 'Authentication failed. Please check your credentials and try again.';
}
