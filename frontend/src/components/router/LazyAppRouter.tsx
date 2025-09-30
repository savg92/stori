import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from '../layout/DashboardLayout';
import { PageLoadingSpinner } from '../ui/loading-spinner';

// Lazy load heavy components
const DashboardOverview = lazy(() =>
	import('../dashboard/DashboardOverview').then((module) => ({
		default: module.DashboardOverview,
	}))
);

const TransactionList = lazy(() =>
	import('../transactions/TransactionList').then((module) => ({
		default: module.TransactionList,
	}))
);

const AIChatPage = lazy(() =>
	import('../../pages/AIChatPage').then((module) => ({
		default: module.AIChatPage,
	}))
);

const APIDataTest = lazy(() =>
	import('../debug/APIDataTest').then((module) => ({
		default: module.APIDataTest,
	}))
);

const MobileTestPage = lazy(() =>
	import('../debug/MobileTestPage').then((module) => ({
		default: module.MobileTestPage,
	}))
);

// Placeholder components for future implementation (kept as regular components since they're small)
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
				<Suspense fallback={<PageLoadingSpinner />}>
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
							element={<AIChatPage />}
						/>
						<Route
							path='/debug'
							element={<APIDataTest />}
						/>
						<Route
							path='/mobile-test'
							element={<MobileTestPage />}
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
				</Suspense>
			</DashboardLayout>
		</BrowserRouter>
	);
}
