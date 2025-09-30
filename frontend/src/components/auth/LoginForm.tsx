import { useState } from 'react';
import { useAuth } from '../../contexts/auth-context';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '../ui/card';
import { Label } from '../ui/label';
import { Alert, AlertDescription } from '../ui/alert';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export function LoginForm() {
	const { signIn, signUp, loading } = useAuth();
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [isSignUp, setIsSignUp] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [success, setSuccess] = useState<string | null>(null);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setError(null);
		setSuccess(null);

		if (!email || !password) {
			const errorMessage = 'Please fill in all fields';
			setError(errorMessage);
			toast.error(errorMessage);
			return;
		}

		try {
			const { error } = isSignUp
				? await signUp(email, password)
				: await signIn(email, password);

			if (error) {
				const errorMessage = error.message || 'Authentication failed';
				setError(errorMessage);
				toast.error(errorMessage);
			} else if (isSignUp) {
				const successMessage =
					'Account created! Please check your email to verify your account.';
				setSuccess(successMessage);
				toast.success(successMessage);
			} else {
				// Successful sign in
				toast.success('Successfully signed in!');
			}
		} catch {
			const errorMessage = 'An unexpected error occurred';
			setError(errorMessage);
			toast.error(errorMessage);
		}
	};

	return (
		<div className='min-h-screen flex items-center justify-center bg-background p-4'>
			<Card className='w-full max-w-md'>
				<CardHeader className='space-y-1'>
					<CardTitle className='text-2xl text-center'>
						{isSignUp ? 'Create account' : 'Sign in'}
					</CardTitle>
					<CardDescription className='text-center'>
						{isSignUp
							? 'Enter your details to create your account'
							: 'Enter your credentials to access your account'}
					</CardDescription>
				</CardHeader>
				<CardContent>
					<form
						onSubmit={handleSubmit}
						className='space-y-4'
					>
						<div className='space-y-2'>
							<Label htmlFor='email'>Email</Label>
							<Input
								id='email'
								type='email'
								placeholder='m@example.com'
								value={email}
								onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
									setEmail(e.target.value)
								}
								disabled={loading}
								required
							/>
						</div>
						<div className='space-y-2'>
							<Label htmlFor='password'>Password</Label>
							<Input
								id='password'
								type='password'
								value={password}
								onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
									setPassword(e.target.value)
								}
								disabled={loading}
								required
								minLength={6}
							/>
						</div>

						{error && (
							<Alert variant='destructive'>
								<AlertDescription>{error}</AlertDescription>
							</Alert>
						)}

						{success && (
							<Alert>
								<AlertDescription>{success}</AlertDescription>
							</Alert>
						)}

						<Button
							type='submit'
							className='w-full'
							disabled={loading}
						>
							{loading && <Loader2 className='mr-2 h-4 w-4 animate-spin' />}
							{isSignUp ? 'Create account' : 'Sign in'}
						</Button>

						<div className='text-center'>
							<Button
								type='button'
								variant='link'
								onClick={() => {
									setIsSignUp(!isSignUp);
									setError(null);
									setSuccess(null);
								}}
								disabled={loading}
							>
								{isSignUp
									? 'Already have an account? Sign in'
									: "Don't have an account? Sign up"}
							</Button>
						</div>
					</form>
				</CardContent>
			</Card>
		</div>
	);
}
