import React from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
	children?: ReactNode;
	fallback?: ReactNode;
}

interface State {
	hasError: boolean;
	error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
	public state: State = {
		hasError: false,
	};

	public static getDerivedStateFromError(error: Error): State {
		// Update state so the next render will show the fallback UI
		return { hasError: true, error };
	}

	public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
		console.error('Error caught by boundary:', error, errorInfo);

		// You could also log the error to an error reporting service here
		// logErrorToService(error, errorInfo);
	}

	private handleRetry = () => {
		this.setState({ hasError: false, error: undefined });
	};

	public render() {
		if (this.state.hasError) {
			// Custom fallback UI
			if (this.props.fallback) {
				return this.props.fallback;
			}

			// Default error UI
			return (
				<Card className='w-full max-w-md mx-auto mt-8'>
					<CardHeader className='text-center'>
						<div className='mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10'>
							<AlertTriangle className='h-6 w-6 text-destructive' />
						</div>
						<CardTitle>Something went wrong</CardTitle>
						<CardDescription>
							An unexpected error occurred. Please try refreshing the page or
							contact support if the problem persists.
						</CardDescription>
					</CardHeader>
					<CardContent className='text-center space-y-4'>
						{process.env.NODE_ENV === 'development' && this.state.error && (
							<div className='text-left bg-muted p-3 rounded-md text-sm'>
								<strong>Error:</strong> {this.state.error.message}
								<br />
								<strong>Stack:</strong>
								<pre className='mt-2 text-xs overflow-auto'>
									{this.state.error.stack}
								</pre>
							</div>
						)}
						<div className='flex gap-2 justify-center'>
							<Button
								variant='outline'
								onClick={() => window.location.reload()}
								className='flex items-center gap-2'
							>
								<RefreshCw className='h-4 w-4' />
								Refresh Page
							</Button>
							<Button
								onClick={this.handleRetry}
								className='flex items-center gap-2'
							>
								Try Again
							</Button>
						</div>
					</CardContent>
				</Card>
			);
		}

		return this.props.children;
	}
}

// HOC wrapper for functional components
export function withErrorBoundary<P extends object>(
	Component: React.ComponentType<P>,
	fallback?: ReactNode
) {
	const WrappedComponent = (props: P) => (
		<ErrorBoundary fallback={fallback}>
			<Component {...props} />
		</ErrorBoundary>
	);

	WrappedComponent.displayName = `withErrorBoundary(${
		Component.displayName || Component.name
	})`;

	return WrappedComponent;
}
