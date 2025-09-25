// Mobile responsive test page
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DashboardOverview } from '@/components/dashboard/DashboardOverview';
import { ExpenseChart } from '@/components/charts/ExpenseChart';
import { TimelineChart } from '@/components/charts/TimelineChart';
import { AIChat } from '@/components/ai/AIChat';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { Smartphone, Tablet, Monitor } from 'lucide-react';

export function MobileTestPage() {
	const [viewMode, setViewMode] = useState<'mobile' | 'tablet' | 'desktop'>(
		'mobile'
	);

	const viewportClasses = {
		mobile: 'max-w-[375px]', // iPhone SE width
		tablet: 'max-w-[768px]', // iPad width
		desktop: 'max-w-[1200px]', // Desktop width
	};

	return (
		<div className='container mx-auto p-4'>
			<div className='mb-6'>
				<h1 className='text-3xl font-bold tracking-tight mb-2'>
					Mobile Responsive Test
				</h1>
				<p className='text-muted-foreground mb-4'>
					Test how components look and function across different device sizes.
				</p>

				{/* Viewport selector */}
				<div className='flex gap-2 mb-6'>
					<Button
						variant={viewMode === 'mobile' ? 'default' : 'outline'}
						size='sm'
						onClick={() => setViewMode('mobile')}
						className='flex items-center gap-2'
					>
						<Smartphone className='h-4 w-4' />
						Mobile (375px)
					</Button>
					<Button
						variant={viewMode === 'tablet' ? 'default' : 'outline'}
						size='sm'
						onClick={() => setViewMode('tablet')}
						className='flex items-center gap-2'
					>
						<Tablet className='h-4 w-4' />
						Tablet (768px)
					</Button>
					<Button
						variant={viewMode === 'desktop' ? 'default' : 'outline'}
						size='sm'
						onClick={() => setViewMode('desktop')}
						className='flex items-center gap-2'
					>
						<Monitor className='h-4 w-4' />
						Desktop (1200px)
					</Button>
				</div>
			</div>

			{/* Test viewport */}
			<div
				className={`mx-auto border rounded-lg ${viewportClasses[viewMode]} transition-all duration-300`}
			>
				<Card>
					<CardHeader>
						<CardTitle className='flex items-center justify-between'>
							<span>Component Test - {viewMode}</span>
							<span className='text-sm text-muted-foreground'>
								{viewMode === 'mobile' && '375px'}
								{viewMode === 'tablet' && '768px'}
								{viewMode === 'desktop' && '1200px'}
							</span>
						</CardTitle>
					</CardHeader>
					<CardContent>
						<div className='space-y-6'>
							{/* Dashboard Overview */}
							<div>
								<h3 className='text-lg font-semibold mb-3'>
									Dashboard Overview
								</h3>
								<DashboardOverview />
							</div>

							{/* Individual Charts */}
							<div>
								<h3 className='text-lg font-semibold mb-3'>Expense Chart</h3>
								<ExpenseChart />
							</div>

							<div>
								<h3 className='text-lg font-semibold mb-3'>Timeline Chart</h3>
								<TimelineChart />
							</div>

							{/* AI Chat */}
							<div>
								<h3 className='text-lg font-semibold mb-3'>
									AI Chat Interface
								</h3>
								<div className='max-h-[400px]'>
									<AIChat />
								</div>
							</div>
						</div>
					</CardContent>
				</Card>
			</div>

			{/* Testing notes */}
			<div className='mt-6 max-w-4xl mx-auto'>
				<Card>
					<CardHeader>
						<CardTitle>Mobile Testing Checklist</CardTitle>
					</CardHeader>
					<CardContent>
						<div className='space-y-4'>
							<div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
								<div>
									<h4 className='font-medium mb-2'>📱 Mobile (375px)</h4>
									<ul className='text-sm text-muted-foreground space-y-1'>
										<li>✓ Charts resize properly</li>
										<li>✓ Text remains readable</li>
										<li>✓ Buttons are touch-friendly</li>
										<li>✓ Navigation is accessible</li>
									</ul>
								</div>
								<div>
									<h4 className='font-medium mb-2'>📱 Tablet (768px)</h4>
									<ul className='text-sm text-muted-foreground space-y-1'>
										<li>✓ Layout adapts smoothly</li>
										<li>✓ Charts show more detail</li>
										<li>✓ Two-column layouts work</li>
										<li>✓ Touch interactions work</li>
									</ul>
								</div>
								<div>
									<h4 className='font-medium mb-2'>🖥️ Desktop (1200px)</h4>
									<ul className='text-sm text-muted-foreground space-y-1'>
										<li>✓ Full feature display</li>
										<li>✓ Optimal chart sizing</li>
										<li>✓ Multi-column layouts</li>
										<li>✓ Hover interactions</li>
									</ul>
								</div>
							</div>
						</div>
					</CardContent>
				</Card>
			</div>
		</div>
	);
}
