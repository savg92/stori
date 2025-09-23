import { useEffect, useState, type ReactNode } from 'react';
import type { User, Session } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';
import { AuthContext, type AuthContextType } from '../contexts/auth-context';

export function AuthProvider({ children }: { children: ReactNode }) {
	const [user, setUser] = useState<User | null>(null);
	const [session, setSession] = useState<Session | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		// Get initial session
		supabase.auth.getSession().then(({ data: { session } }) => {
			setSession(session);
			setUser(session?.user ?? null);
			setLoading(false);
		});

		// Listen for auth changes
		const {
			data: { subscription },
		} = supabase.auth.onAuthStateChange((_event, session) => {
			setSession(session);
			setUser(session?.user ?? null);
			setLoading(false);
		});

		return () => subscription.unsubscribe();
	}, []);

	const signIn = async (email: string, password: string) => {
		setLoading(true);
		const result = await supabase.auth.signInWithPassword({ email, password });
		setLoading(false);
		return { error: result.error };
	};

	const signUp = async (email: string, password: string) => {
		setLoading(true);
		const result = await supabase.auth.signUp({ email, password });
		setLoading(false);
		return { error: result.error };
	};

	const signOut = async () => {
		setLoading(true);
		const result = await supabase.auth.signOut();
		setLoading(false);
		return { error: result.error };
	};

	const resetPassword = async (email: string) => {
		const result = await supabase.auth.resetPasswordForEmail(email, {
			redirectTo: `${window.location.origin}/reset-password`,
		});
		return { error: result.error };
	};

	const value: AuthContextType = {
		user,
		session,
		loading,
		signIn,
		signUp,
		signOut,
		resetPassword,
	};

	return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
