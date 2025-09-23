import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../layout/DashboardLayout';
import { DashboardOverview } from '../dashboard/DashboardOverview';
import { TransactionList } from '../transactions/TransactionList';

// Placeholder components for future implementation
function AnalyticsPage() {
	return (
		<div className='space-y-6'>
			<h1 className='text-3xl font-bold tracking-tight'>Analytics</h1>
			<p className='text-muted-foreground'>
				Comprehensive financial analytics and insights coming soon...
			</p>
		</div>
	);
}

function AIAdvisorPage() {
	return (
		<div className='space-y-6'>
			<h1 className='text-3xl font-bold tracking-tight'>AI Advisor</h1>
			<p className='text-muted-foreground'>
				AI-powered financial advice and chat interface coming soon...
			</p>
		</div>
	);
}

function SettingsPage() {
	return (
		<div className='space-y-6'>
			<h1 className='text-3xl font-bold tracking-tight'>Settings</h1>
			<p className='text-muted-foreground'>
				Account settings and preferences coming soon...
			</p>
		</div>
	);
}

export function AppRouter() {
	return (
		<BrowserRouter>
			<DashboardLayout>
				<Routes>
					<Route
						path='/'
						element={<DashboardOverview />}
					/>
					<Route
						path='/transactions'
						element={<TransactionList />}
					/>
					<Route
						path='/analytics'
						element={<AnalyticsPage />}
					/>
					<Route
						path='/ai'
						element={<AIAdvisorPage />}
					/>
					<Route
						path='/settings'
						element={<SettingsPage />}
					/>
					{/* Redirect any unknown routes to dashboard */}
					<Route
						path='*'
						element={
							<Navigate
								to='/'
								replace
							/>
						}
					/>
				</Routes>
			</DashboardLayout>
		</BrowserRouter>
	);
}
