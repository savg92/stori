/// <reference types="vitest" />
import path from 'path';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react-swc';

// https://vite.dev/config/
export default defineConfig({
	plugins: [react(), tailwindcss()],
	resolve: {
		alias: {
			'@': path.resolve(__dirname, './src'),
		},
	},
	build: {
		rollupOptions: {
			output: {
				manualChunks: {
					// Separate chart library into its own chunk
					charts: ['recharts'],
					// Separate UI components into their own chunk
					ui: [
						'@radix-ui/react-dialog',
						'@radix-ui/react-dropdown-menu',
						'@radix-ui/react-label',
						'@radix-ui/react-scroll-area',
						'@radix-ui/react-select',
						'@radix-ui/react-slot',
						'@radix-ui/react-tabs',
					],
					// Separate data fetching into its own chunk
					query: ['@tanstack/react-query'],
					// Separate routing into its own chunk
					router: ['@tanstack/react-router', 'react-router-dom'],
					// Separate auth/supabase into its own chunk
					auth: ['@supabase/supabase-js'],
				},
			},
		},
		// Increase chunk size warning limit to 750kb as we've optimized chunking
		chunkSizeWarningLimit: 750,
	},
	test: {
		globals: true,
		environment: 'jsdom',
		setupFiles: ['./src/test/setup.ts'],
		css: true,
		exclude: [
			'**/node_modules/**',
			'**/dist/**',
			'**/cypress/**',
			'**/.{idea,git,cache,output,temp}/**',
			'**/{karma,rollup,webpack,vite,vitest,jest,ava,babel,nyc,cypress,tsup,build}.config.*',
			'**/e2e/**',
		],
		deps: {
			external: ['@testing-library/react'],
		},
	},
});
