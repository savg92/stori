import { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/auth-context';
import { Button } from '../ui/button';
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { ModeToggle } from '../mode-toggle';
import {
	Home,
	CreditCard,
	TrendingUp,
	MessageSquare,
	Settings,
	LogOut,
	User,
	Menu,
	X,
} from 'lucide-react';

interface DashboardLayoutProps {
	children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
	const { user, signOut } = useAuth();
	const [sidebarOpen, setSidebarOpen] = useState(false);
	const location = useLocation();

	const navigation = [
		{ name: 'Dashboard', href: '/', icon: Home },
		{ name: 'Transactions', href: '/transactions', icon: CreditCard },
		{ name: 'Analytics', href: '/analytics', icon: TrendingUp },
		{ name: 'AI Advisor', href: '/ai', icon: MessageSquare },
		{ name: 'Settings', href: '/settings', icon: Settings },
	];

	const handleSignOut = async () => {
		await signOut();
	};

	const isCurrentPath = (path: string) => {
		return location.pathname === path;
	};

	return (
		<div className='min-h-screen bg-background w-full'>
			{/* Mobile sidebar */}
			<div className={`lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
				<div className='fixed inset-0 z-50 flex'>
					<div
						className='fixed inset-0 bg-black/50'
						onClick={() => setSidebarOpen(false)}
					/>
					<div className='relative flex w-full max-w-xs flex-col bg-card border-r'>
						<div className='flex h-16 items-center justify-between px-3 border-b'>
							<span className='text-xl font-bold'>Stori</span>
							<Button
								variant='ghost'
								size='icon'
								onClick={() => setSidebarOpen(false)}
								className='h-10 w-10'
								aria-label='Close navigation menu'
							>
								<X
									className='h-5 w-5'
									aria-hidden='true'
								/>
							</Button>
						</div>
						<nav
							className='flex-1 space-y-1 px-3 py-4 overflow-y-auto'
							aria-label='Main navigation'
							role='navigation'
						>
							{navigation.map((item) => (
								<Link
									key={item.name}
									to={item.href}
									className={`flex items-center rounded-md px-3 py-3 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground ${
										isCurrentPath(item.href)
											? 'bg-accent text-accent-foreground'
											: 'text-muted-foreground'
									}`}
									onClick={() => setSidebarOpen(false)}
								>
									<item.icon className='mr-3 h-5 w-5 flex-shrink-0' />
									{item.name}
								</Link>
							))}
						</nav>
					</div>
				</div>
			</div>

			{/* Desktop sidebar */}
			<div className='hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col'>
				<div className='flex min-h-0 flex-1 flex-col bg-card border-r'>
					<div className='flex h-16 items-center px-4'>
						<span className='text-xl font-bold'>Stori</span>
					</div>
					<nav
						className='flex-1 space-y-1 px-2 py-4'
						aria-label='Main navigation'
						role='navigation'
					>
						{navigation.map((item) => (
							<Link
								key={item.name}
								to={item.href}
								className={`flex items-center rounded-md px-2 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground ${
									isCurrentPath(item.href)
										? 'bg-accent text-accent-foreground'
										: 'text-muted-foreground'
								}`}
							>
								<item.icon className='mr-3 h-5 w-5' />
								{item.name}
							</Link>
						))}
					</nav>
				</div>
			</div>

			{/* Main content */}
			<div className='w-full lg:pl-64'>
				{/* Top navigation */}
				<div className='sticky top-0 z-40 flex h-16 w-full shrink-0 items-center gap-x-2 border-b bg-background px-3 shadow-sm sm:gap-x-4 sm:px-4 lg:gap-x-6 lg:px-6'>
					<Button
						variant='ghost'
						size='icon'
						className='lg:hidden h-10 w-10'
						onClick={() => setSidebarOpen(true)}
						aria-label='Open navigation menu'
						aria-expanded={sidebarOpen}
					>
						<Menu
							className='h-5 w-5'
							aria-hidden='true'
						/>
					</Button>

					<div className='flex flex-1 gap-x-2 self-stretch sm:gap-x-4 lg:gap-x-6'>
						<div className='flex flex-1'></div>
						<div className='flex items-center gap-x-2 sm:gap-x-4 lg:gap-x-6'>
							<ModeToggle />

							<DropdownMenu>
								<DropdownMenuTrigger asChild>
									<Button
										variant='ghost'
										size='icon'
										className='h-10 w-10'
									>
										<User className='h-5 w-5' />
									</Button>
								</DropdownMenuTrigger>
								<DropdownMenuContent align='end'>
									<DropdownMenuItem>
										<User className='mr-2 h-4 w-4' />
										<span>{user?.email}</span>
									</DropdownMenuItem>
									<DropdownMenuItem onClick={handleSignOut}>
										<LogOut className='mr-2 h-4 w-4' />
										<span>Sign out</span>
									</DropdownMenuItem>
								</DropdownMenuContent>
							</DropdownMenu>
						</div>
					</div>
				</div>

				{/* Page content */}
				<main className='w-full'>
					<div className='w-full px-3 py-4 sm:px-4 sm:py-6 lg:px-6 lg:py-8'>
						{children}
					</div>
				</main>
			</div>
		</div>
	);
}
