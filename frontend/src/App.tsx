import './App.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './components/theme-provider';
import { AuthProvider } from './hooks/useAuth';
import { useAuth } from './contexts/auth-context';
import { LoginForm } from './components/auth/LoginForm';
import { AppRouter } from './components/router/AppRouter';
import { Toaster } from 'sonner';

const queryClient = new QueryClient({
	defaultOptions: {
		queries: {
			staleTime: 5 * 60 * 1000, // 5 minutes
			gcTime: 10 * 60 * 1000, // 10 minutes
		},
	},
});

function AppContent() {
	const { user, loading } = useAuth();

	if (loading) {
		return (
			<div className='min-h-screen flex items-center justify-center'>
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
				<AuthProvider>
					<AppContent />
				</AuthProvider>
				<Toaster />
			</ThemeProvider>
		</QueryClientProvider>
	);
}

export default App;
