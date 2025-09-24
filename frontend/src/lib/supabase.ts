import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabasePublishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabasePublishableKey) {
	throw new Error('Missing Supabase environment variables');
}

export const supabase = createClient(supabaseUrl, supabasePublishableKey, {
	auth: {
		autoRefreshToken: true,
		persistSession: true,
		detectSessionInUrl: true,
	},
});

export type Database = {
	public: {
		Tables: {
			transactions: {
				Row: {
					id: string;
					user_id: string;
					type: 'income' | 'expense';
					amount: number;
					category: string;
					description: string | null;
					date: string;
					created_at: string;
					updated_at: string;
				};
				Insert: {
					id?: string;
					user_id: string;
					type: 'income' | 'expense';
					amount: number;
					category: string;
					description?: string | null;
					date: string;
					created_at?: string;
					updated_at?: string;
				};
				Update: {
					id?: string;
					user_id?: string;
					type?: 'income' | 'expense';
					amount?: number;
					category?: string;
					description?: string | null;
					date?: string;
					created_at?: string;
					updated_at?: string;
				};
			};
		};
	};
};
