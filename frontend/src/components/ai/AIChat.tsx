import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAIChat } from '@/hooks/useApi';
import {
	Loader2,
	Send,
	Bot,
	User,
	Lightbulb,
	MessageCircle,
} from 'lucide-react';

interface Message {
	id: string;
	content: string;
	isUser: boolean;
	timestamp: Date;
}

export function AIChat() {
	const [messages, setMessages] = useState<Message[]>([
		{
			id: '1',
			content:
				"Hello! I'm your AI financial advisor. I can help you analyze your spending patterns, suggest budgeting strategies, and answer questions about your financial data. What would you like to know?",
			isUser: false,
			timestamp: new Date(),
		},
	]);
	const [inputMessage, setInputMessage] = useState('');
	const scrollAreaRef = useRef<HTMLDivElement>(null);

	const { mutate: sendMessage, isPending } = useAIChat({
		onSuccess: (response) => {
			// Debug log to see what we're getting
			console.log('AI Response received:', response);

			// Add AI response to messages
			const aiMessage: Message = {
				id: crypto.randomUUID(),
				content: response.response || response.message || 'Empty response', // Handle both possible field names
				isUser: false,
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, aiMessage]);
		},
		onError: (error) => {
			// Debug log to see errors
			console.error('AI Chat error:', error);

			// Add error message to chat
			const errorMessage: Message = {
				id: crypto.randomUUID(),
				content:
					"Sorry, I'm having trouble processing your request right now. Please try again later.",
				isUser: false,
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, errorMessage]);
		},
	});

	const suggestedPrompts = [
		'How can I reduce my monthly expenses?',
		"What's my biggest spending category?",
		'Am I saving enough money each month?',
		'Show me my spending trends',
		'Give me a financial health summary',
		'What are my top expense categories this month?',
	];

	// Auto-scroll to bottom when new messages arrive
	useEffect(() => {
		if (scrollAreaRef.current) {
			const scrollElement = scrollAreaRef.current.querySelector(
				'[data-radix-scroll-area-viewport]'
			);
			if (scrollElement) {
				scrollElement.scrollTop = scrollElement.scrollHeight;
			}
		}
	}, [messages, isPending]);

	const handleSendMessage = () => {
		if (!inputMessage.trim()) return;

		const userMessage: Message = {
			id: crypto.randomUUID(),
			content: inputMessage,
			isUser: true,
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		sendMessage({ message: inputMessage });
		setInputMessage('');
	};

	const handleSuggestedPrompt = (prompt: string) => {
		const userMessage: Message = {
			id: crypto.randomUUID(),
			content: prompt,
			isUser: true,
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		sendMessage({ message: prompt });
	};

	const handleKeyPress = (e: React.KeyboardEvent) => {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSendMessage();
		}
	};

	// Auto-scroll to bottom when new messages are added
	useEffect(() => {
		if (scrollAreaRef.current) {
			const scrollContainer = scrollAreaRef.current.querySelector(
				'[data-radix-scroll-area-viewport]'
			);
			if (scrollContainer) {
				scrollContainer.scrollTo({
					top: scrollContainer.scrollHeight,
					behavior: 'smooth',
				});
			}
		}
	}, [messages, isPending]);

	return (
		<Card className='h-[600px] sm:h-[700px] flex flex-col shadow-lg border-0 bg-gradient-to-b from-background to-muted/20'>
			<CardHeader className='border-b bg-gradient-to-r from-primary/5 to-primary/10'>
				<CardTitle className='flex items-center space-x-3'>
					<div className='relative'>
						<Bot className='h-6 w-6 text-primary' />
						<div className='absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse' />
					</div>
					<div>
						<span className='text-lg'>AI Financial Advisor</span>
						<p className='text-sm font-normal text-muted-foreground mt-1'>
							Powered by advanced financial analysis
						</p>
					</div>
				</CardTitle>
			</CardHeader>
			<CardContent className='flex-1 flex flex-col space-y-4 p-4 sm:p-6 min-h-0'>
				<ScrollArea
					ref={scrollAreaRef}
					className='flex-1 pr-4 min-h-0'
				>
					<div className='space-y-4 pb-4'>
						{messages.map((message) => (
							<div
								key={message.id}
								className={`flex items-start space-x-3 animate-in fade-in-0 slide-in-from-bottom-2 duration-300 ${
									message.isUser ? 'justify-end' : 'justify-start'
								}`}
							>
								{!message.isUser && (
									<div className='w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-primary/20 to-primary/10 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm'>
										<Bot className='h-4 w-4 sm:h-5 sm:w-5 text-primary' />
									</div>
								)}
								<div
									className={`max-w-[85%] sm:max-w-[80%] rounded-xl p-3 sm:p-4 shadow-sm ${
										message.isUser
											? 'bg-gradient-to-br from-primary to-primary/90 text-primary-foreground'
											: 'bg-gradient-to-br from-muted/80 to-muted border'
									}`}
								>
									<p className='text-sm sm:text-base whitespace-pre-wrap leading-relaxed'>
										{message.content}
									</p>
									<p className='text-xs opacity-70 mt-2 flex items-center gap-1'>
										<MessageCircle className='h-3 w-3' />
										{message.timestamp.toLocaleTimeString([], {
											hour: '2-digit',
											minute: '2-digit',
										})}
									</p>
								</div>
								{message.isUser && (
									<div className='w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-secondary/20 to-secondary/10 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm'>
										<User className='h-4 w-4 sm:h-5 sm:w-5 text-secondary-foreground' />
									</div>
								)}
							</div>
						))}
						{isPending && (
							<div className='flex items-start space-x-3 animate-in fade-in-0 slide-in-from-bottom-2 duration-300'>
								<div className='w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-primary/20 to-primary/10 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm'>
									<Bot className='h-4 w-4 sm:h-5 sm:w-5 text-primary' />
								</div>
								<div className='bg-gradient-to-br from-muted/80 to-muted border rounded-xl p-3 sm:p-4 shadow-sm'>
									<div className='flex items-center space-x-2'>
										<Loader2 className='h-4 w-4 animate-spin text-primary' />
										<span className='text-sm text-muted-foreground'>
											Analyzing your financial data...
										</span>
									</div>
								</div>
							</div>
						)}
					</div>
				</ScrollArea>

				<div className='space-y-3 sm:space-y-4 border-t pt-4 flex-shrink-0'>
					<div className='w-full'>
						<p className='text-xs sm:text-sm text-muted-foreground mb-2 sm:mb-3 font-medium flex items-center gap-2'>
							<Lightbulb className='h-4 w-4' />
							💡 Try asking about:
						</p>
						<div className='flex flex-wrap gap-2'>
							{suggestedPrompts.map((prompt, index) => (
								<Button
									key={index}
									variant='outline'
									size='sm'
									onClick={() => handleSuggestedPrompt(prompt)}
									disabled={isPending}
									className='text-xs sm:text-sm h-8 sm:h-9 px-2 sm:px-3 rounded-full hover:bg-primary/10 hover:border-primary/30 transition-all duration-200 hover:shadow-sm'
								>
									{prompt}
								</Button>
							))}
						</div>
					</div>
					<div className='flex space-x-2 sm:space-x-3'>
						<div className='flex-1'>
							<Input
								value={inputMessage}
								onChange={(e) => setInputMessage(e.target.value)}
								placeholder='Ask about your finances... (e.g., "How can I reduce my expenses?")'
								onKeyPress={handleKeyPress}
								disabled={isPending}
								className='text-sm sm:text-base h-10 sm:h-11 rounded-full border-2 focus:border-primary/50 bg-background/80 backdrop-blur-sm'
							/>
						</div>
						<Button
							onClick={handleSendMessage}
							disabled={isPending || !inputMessage.trim()}
							size='sm'
							className='h-10 w-10 sm:h-11 sm:w-11 rounded-full p-0 shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105 disabled:hover:scale-100'
						>
							{isPending ? (
								<Loader2 className='h-4 w-4 sm:h-5 sm:w-5 animate-spin' />
							) : (
								<Send className='h-4 w-4 sm:h-5 sm:w-5' />
							)}
						</Button>
					</div>
				</div>
			</CardContent>
		</Card>
	);
}
