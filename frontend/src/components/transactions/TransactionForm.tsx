import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from '../ui/select';
import { Textarea } from '../ui/textarea';
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from '../ui/dialog';
import { Plus, Loader2 } from 'lucide-react';
import { useCreateTransaction, useUpdateTransaction } from '../../hooks/useApi';
import type {
	TransactionType,
	IncomeCategory,
	ExpenseCategory,
} from '../../types/api';

// Enhanced category mappings matching backend enums
const INCOME_CATEGORIES: { value: IncomeCategory; label: string }[] = [
	{ value: 'salary', label: 'Salary' },
	{ value: 'freelance', label: 'Freelance' },
	{ value: 'investment', label: 'Investment' },
	{ value: 'business', label: 'Business' },
	{ value: 'gift', label: 'Gift' },
	{ value: 'rental', label: 'Rental Income' },
	{ value: 'dividend', label: 'Dividend' },
	{ value: 'bonus', label: 'Bonus' },
	{ value: 'refund', label: 'Refund' },
	{ value: 'other_income', label: 'Other Income' },
];

const EXPENSE_CATEGORIES: { value: ExpenseCategory; label: string }[] = [
	{ value: 'food_dining', label: 'Food & Dining' },
	{ value: 'transportation', label: 'Transportation' },
	{ value: 'entertainment', label: 'Entertainment' },
	{ value: 'shopping', label: 'Shopping' },
	{ value: 'bills_utilities', label: 'Bills & Utilities' },
	{ value: 'healthcare', label: 'Healthcare' },
	{ value: 'education', label: 'Education' },
	{ value: 'travel', label: 'Travel' },
	{ value: 'groceries', label: 'Groceries' },
	{ value: 'fitness', label: 'Fitness' },
	{ value: 'subscriptions', label: 'Subscriptions' },
	{ value: 'insurance', label: 'Insurance' },
	{ value: 'childcare', label: 'Childcare' },
	{ value: 'other_expense', label: 'Other Expense' },
];

const transactionSchema = z.object({
	type: z.enum(['income', 'expense']),
	amount: z.string().min(1, 'Amount is required'),
	category: z.string().min(1, 'Category is required'),
	description: z.string().optional(),
	date: z.string().min(1, 'Date is required'),
});

type TransactionFormData = z.infer<typeof transactionSchema>;

interface TransactionFormProps {
	initialData?: {
		id?: string;
		type?: TransactionType;
		amount?: number;
		category?: IncomeCategory | ExpenseCategory;
		description?: string;
		date?: string;
	};
	trigger?: React.ReactNode;
	mode?: 'create' | 'edit';
}

export function TransactionForm({
	initialData,
	trigger,
	mode = 'create',
}: TransactionFormProps) {
	const [open, setOpen] = useState(false);
	const [transactionType, setTransactionType] = useState<'income' | 'expense'>(
		initialData?.type || 'expense'
	);

	// API hooks
	const createTransaction = useCreateTransaction();
	const updateTransaction = useUpdateTransaction();

	const {
		register,
		handleSubmit,
		formState: { errors },
		setValue,
		watch,
		reset,
	} = useForm<TransactionFormData>({
		resolver: zodResolver(transactionSchema),
		defaultValues: {
			type: transactionType,
			date: new Date().toISOString().split('T')[0],
			amount: initialData?.amount?.toString() || '',
			category: initialData?.category || '',
			description: initialData?.description || '',
		},
	});

	const watchedType = watch('type');
	const isLoading = createTransaction.isPending || updateTransaction.isPending;

	const handleFormSubmit = async (data: TransactionFormData) => {
		try {
			const amount = parseFloat(data.amount);

			if (mode === 'edit' && initialData?.id) {
				await updateTransaction.mutateAsync({
					id: initialData.id,
					data: {
						type: data.type,
						amount,
						category: data.category as IncomeCategory | ExpenseCategory,
						description: data.description,
						date: data.date,
					},
				});
			} else {
				await createTransaction.mutateAsync({
					type: data.type,
					amount,
					category: data.category as IncomeCategory | ExpenseCategory,
					description: data.description || '',
					date: data.date,
				});
			}
			setOpen(false);
			reset();
		} catch (error) {
			console.error('Failed to submit transaction:', error);
		}
	};

	const handleTypeChange = (value: 'income' | 'expense') => {
		setTransactionType(value);
		setValue('type', value);
		setValue('category', ''); // Reset category when type changes
	};

	const availableCategories =
		watchedType === 'income' || transactionType === 'income'
			? INCOME_CATEGORIES
			: EXPENSE_CATEGORIES;

	return (
		<Dialog
			open={open}
			onOpenChange={setOpen}
		>
			<DialogTrigger asChild>
				{trigger || (
					<Button>
						<Plus className='mr-2 h-4 w-4' />
						Add Transaction
					</Button>
				)}
			</DialogTrigger>
			<DialogContent className='sm:max-w-[425px]'>
				<DialogHeader>
					<DialogTitle>
						{initialData ? 'Edit Transaction' : 'Add New Transaction'}
					</DialogTitle>
					<DialogDescription>
						{initialData
							? 'Update the transaction details below.'
							: 'Fill in the details for your new transaction.'}
					</DialogDescription>
				</DialogHeader>
				<form
					onSubmit={handleSubmit(handleFormSubmit)}
					className='space-y-4'
				>
					<div className='grid grid-cols-2 gap-4'>
						<div className='space-y-2'>
							<Label htmlFor='type'>Type</Label>
							<Select
								value={watchedType}
								onValueChange={handleTypeChange}
							>
								<SelectTrigger>
									<SelectValue placeholder='Select type' />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value='income'>Income</SelectItem>
									<SelectItem value='expense'>Expense</SelectItem>
								</SelectContent>
							</Select>
							{errors.type && (
								<p className='text-sm text-destructive'>
									{errors.type.message}
								</p>
							)}
						</div>

						<div className='space-y-2'>
							<Label htmlFor='amount'>Amount</Label>
							<Input
								id='amount'
								type='number'
								step='0.01'
								placeholder='0.00'
								{...register('amount', { valueAsNumber: true })}
							/>
							{errors.amount && (
								<p className='text-sm text-destructive'>
									{errors.amount.message}
								</p>
							)}
						</div>
					</div>

					<div className='space-y-2'>
						<Label htmlFor='category'>Category</Label>
						<Select
							value={watch('category')}
							onValueChange={(value: string) => setValue('category', value)}
						>
							<SelectTrigger>
								<SelectValue placeholder='Select category' />
							</SelectTrigger>
							<SelectContent>
								{availableCategories.map((category) => (
									<SelectItem
										key={category.value}
										value={category.value}
									>
										{category.label}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
						{errors.category && (
							<p className='text-sm text-destructive'>
								{errors.category.message}
							</p>
						)}
					</div>

					<div className='space-y-2'>
						<Label htmlFor='date'>Date</Label>
						<Input
							id='date'
							type='date'
							{...register('date')}
						/>
						{errors.date && (
							<p className='text-sm text-destructive'>{errors.date.message}</p>
						)}
					</div>

					<div className='space-y-2'>
						<Label htmlFor='description'>Description (Optional)</Label>
						<Textarea
							id='description'
							placeholder='Add a description...'
							{...register('description')}
						/>
						{errors.description && (
							<p className='text-sm text-destructive'>
								{errors.description.message}
							</p>
						)}
					</div>

					<DialogFooter>
						<Button
							type='button'
							variant='outline'
							onClick={() => setOpen(false)}
							disabled={isLoading}
						>
							Cancel
						</Button>
						<Button
							type='submit'
							disabled={isLoading}
						>
							{isLoading && <Loader2 className='mr-2 h-4 w-4 animate-spin' />}
							{initialData ? 'Update' : 'Add'} Transaction
						</Button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}
