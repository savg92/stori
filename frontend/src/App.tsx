import './App.css';
import { QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './components/theme-provider';
import { AuthProvider } from './hooks/useAuth';
import { useAuth } from './contexts/auth-context';
import { LoginForm } from './components/auth/LoginForm';
import { AppRouter } from './components/router/LazyAppRouter';
import { Toaster } from 'sonner';
import { queryClient } from './lib/queryClient';
import { ErrorBoundary } from './components/ErrorBoundary';

function AppContent() {
	const { user, loading } = useAuth();

	if (loading) {
		return (
			<div className='w-full min-h-screen flex items-center justify-center bg-background'>
				<div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary'></div>
			</div>
		);
	}

	if (!user) {
		return <LoginForm />;
	}

	return <AppRouter />;
}

function App() {
	return (
		<QueryClientProvider client={queryClient}>
			<ThemeProvider
				defaultTheme='dark'
				storageKey='vite-ui-theme'
			>
				<ErrorBoundary>
					<AuthProvider>
						<AppContent />
					</AuthProvider>
				</ErrorBoundary>
				<Toaster />
			</ThemeProvider>
		</QueryClientProvider>
	);
}

export default App;
