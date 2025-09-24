import { supabase } from './supabase';
import { API_BASE_URL } from './config';

export class ApiClient {
	private baseUrl: string;

	constructor(baseUrl: string = API_BASE_URL) {
		this.baseUrl = baseUrl;
	}

	private async getAuthHeaders(): Promise<Record<string, string>> {
		const {
			data: { session },
		} = await supabase.auth.getSession();

		const headers: Record<string, string> = {
			'Content-Type': 'application/json',
		};

		if (session?.access_token) {
			headers['Authorization'] = `Bearer ${session.access_token}`;
		}

		return headers;
	}

	private async request<T>(
		endpoint: string,
		options: RequestInit = {}
	): Promise<T> {
		const url = `${this.baseUrl}${endpoint}`;
		const headers = await this.getAuthHeaders();

		const config: RequestInit = {
			...options,
			headers: {
				...headers,
				...options.headers,
			},
		};

		const response = await fetch(url, config);

		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(
				errorData.detail || `HTTP ${response.status}: ${response.statusText}`
			);
		}

		return response.json();
	}

	// GET request
	async get<T>(endpoint: string): Promise<T> {
		return this.request<T>(endpoint, { method: 'GET' });
	}

	// POST request
	async post<T>(endpoint: string, data?: unknown): Promise<T> {
		return this.request<T>(endpoint, {
			method: 'POST',
			body: data ? JSON.stringify(data) : undefined,
		});
	}

	// PUT request
	async put<T>(endpoint: string, data?: unknown): Promise<T> {
		return this.request<T>(endpoint, {
			method: 'PUT',
			body: data ? JSON.stringify(data) : undefined,
		});
	}

	// DELETE request
	async delete<T>(endpoint: string): Promise<T> {
		return this.request<T>(endpoint, { method: 'DELETE' });
	}
}

export const apiClient = new ApiClient();
