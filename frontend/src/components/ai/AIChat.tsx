import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useAIChat } from '@/hooks/useApi';
import { Loader2, Send, Bot, User } from 'lucide-react';

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

	const { mutate: sendMessage, isPending } = useAIChat();

	const handleSendMessage = () => {
		if (!inputMessage.trim() || isPending) return;

		const userMessage: Message = {
			id: Date.now().toString(),
			content: inputMessage.trim(),
			isUser: true,
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);

		sendMessage(
			{
				message: inputMessage.trim(),
			},
			{
				onSuccess: (response) => {
					const aiMessage: Message = {
						id: (Date.now() + 1).toString(),
						content: response.response,
						isUser: false,
						timestamp: new Date(),
					};
					setMessages((prev) => [...prev, aiMessage]);
				},
				onError: (error) => {
					const errorMessage: Message = {
						id: (Date.now() + 1).toString(),
						content:
							"I'm sorry, I'm having trouble connecting right now. Please try again later.",
						isUser: false,
						timestamp: new Date(),
					};
					setMessages((prev) => [...prev, errorMessage]);
					console.error('AI Chat error:', error);
				},
			}
		);

		setInputMessage('');
	};

	const handleKeyPress = (e: React.KeyboardEvent) => {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSendMessage();
		}
	};

	return (
		<Card className='h-[600px] flex flex-col'>
			<CardHeader>
				<CardTitle className='flex items-center space-x-2'>
					<Bot className='h-5 w-5 text-primary' />
					<span>AI Financial Advisor</span>
				</CardTitle>
			</CardHeader>
			<CardContent className='flex-1 flex flex-col space-y-4 p-4'>
				<ScrollArea className='flex-1 pr-4'>
					<div className='space-y-4'>
						{messages.map((message) => (
							<div
								key={message.id}
								className={`flex items-start space-x-3 ${
									message.isUser ? 'justify-end' : 'justify-start'
								}`}
							>
								{!message.isUser && (
									<div className='w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0'>
										<Bot className='h-4 w-4 text-primary' />
									</div>
								)}
								<div
									className={`max-w-[80%] rounded-lg p-3 ${
										message.isUser
											? 'bg-primary text-primary-foreground'
											: 'bg-muted'
									}`}
								>
									<p className='text-sm whitespace-pre-wrap'>
										{message.content}
									</p>
									<p className='text-xs opacity-70 mt-2'>
										{message.timestamp.toLocaleTimeString([], {
											hour: '2-digit',
											minute: '2-digit',
										})}
									</p>
								</div>
								{message.isUser && (
									<div className='w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0'>
										<User className='h-4 w-4 text-primary' />
									</div>
								)}
							</div>
						))}
						{isPending && (
							<div className='flex items-start space-x-3'>
								<div className='w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0'>
									<Bot className='h-4 w-4 text-primary' />
								</div>
								<div className='bg-muted rounded-lg p-3'>
									<div className='flex items-center space-x-2'>
										<Loader2 className='h-4 w-4 animate-spin' />
										<span className='text-sm text-muted-foreground'>
											Thinking...
										</span>
									</div>
								</div>
							</div>
						)}
					</div>
				</ScrollArea>

				<div className='flex space-x-2'>
					<Input
						placeholder='Ask me about your finances...'
						value={inputMessage}
						onChange={(e) => setInputMessage(e.target.value)}
						onKeyPress={handleKeyPress}
						disabled={isPending}
						className='flex-1'
					/>
					<Button
						onClick={handleSendMessage}
						disabled={!inputMessage.trim() || isPending}
						size='icon'
					>
						{isPending ? (
							<Loader2 className='h-4 w-4 animate-spin' />
						) : (
							<Send className='h-4 w-4' />
						)}
					</Button>
				</div>
			</CardContent>
		</Card>
	);
}
