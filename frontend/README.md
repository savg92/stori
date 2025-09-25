# Stori Frontend - React + TypeScript + Vite

Modern React frontend for the Stori Expense Tracker with AI-powered financial advice.

## 🚀 Features

- **Modern React**: Built with React 18+ and TypeScript for type safety
- **Vite Development**: Lightning-fast development server with HMR
- **UI Components**: Shadcn/ui components with TailwindCSS styling
- **Authentication**: Supabase Auth integration with protected routes
- **Data Visualization**: Interactive charts with Recharts
- **Responsive Design**: Mobile-first design (320px+)
- **Dark Mode**: Dark theme by default
- **Performance**: Bundle size optimized with code splitting

## 🛠️ Tech Stack

- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS + Shadcn/ui
- **Charts**: Recharts
- **HTTP Client**: Axios with React Query
- **Authentication**: Supabase Auth
- **Package Manager**: Bun (exclusively)

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+
- **Bun** package manager (required)

### Installation

```bash
# Install dependencies (use bun exclusively)
bun install

# Start development server
bun dev

# Build for production
bun run build

# Preview production build
bun run preview
```

### Environment Setup

Create a `.env` file in the frontend directory:

```bash
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── ui/            # Shadcn/ui components
│   │   ├── auth/          # Authentication components
│   │   ├── dashboard/     # Dashboard components
│   │   ├── charts/        # Chart components
│   │   └── layout/        # Layout components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API client and utilities
│   ├── types/             # TypeScript type definitions
│   ├── lib/               # Utility functions
│   └── styles/            # CSS and styling
├── public/                # Static assets
└── index.html             # Entry HTML file
```

## 🧪 Testing

```bash
# Run unit tests
bun test

# Run tests in watch mode
bun run test:watch

# Run E2E tests
bun run test:e2e
```

## 📚 Available Scripts

- `bun dev` - Start development server
- `bun run build` - Build for production
- `bun run preview` - Preview production build
- `bun test` - Run unit tests
- `bun run lint` - Run ESLint
- `bun run lint:fix` - Fix ESLint issues

## 🔧 Development

### Code Style

- **ESLint**: TypeScript and React rules
- **Prettier**: Code formatting
- **TypeScript**: Strict mode enabled

### Adding New Components

Follow the existing pattern:

1. Create component in appropriate `src/components/` subdirectory
2. Export from `index.ts` file
3. Add TypeScript types in `src/types/`
4. Include tests alongside component files

### API Integration

Use the existing patterns:

- React Query for data fetching
- Axios client in `src/services/api.ts`
- TypeScript interfaces for API responses

## 🚀 Production

The frontend is optimized for production deployment:

- **Static Build**: Generates optimized static files
- **Code Splitting**: Automatic route-based splitting
- **Asset Optimization**: Images and assets optimized
- **Bundle Analysis**: Use `bun run analyze` to inspect bundle

### Deployment Options

- **Vercel/Netlify**: Deploy directly from Git
- **AWS S3 + CloudFront**: Static hosting with CDN
- **Docker**: Use provided Dockerfile for containerization

## 🤝 Contributing

1. Follow the frontend agent guidelines in `/frontend_agent.md`
2. Use `bun` exclusively (never npm/yarn)
3. Keep components under 150 lines
4. Include TypeScript types for all props
5. Add tests for new features
6. Follow existing file structure patterns

## 📖 Documentation

- Component documentation in component files
- API integration patterns in `src/services/`
- Type definitions in `src/types/`
- Styling guides in component examples

```

```
