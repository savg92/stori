import { AIChat } from '@/components/ai/AIChat';

export function AIChatPage() {
	return (
		<div className='container mx-auto p-6'>
			<div className='max-w-4xl mx-auto'>
				<div className='mb-6'>
					<h1 className='text-3xl font-bold tracking-tight'>
						AI Financial Advisor
					</h1>
					<p className='text-muted-foreground'>
						Get personalized financial insights and advice based on your
						spending patterns.
					</p>
				</div>
				<AIChat />
			</div>
		</div>
	);
}
