# 💰 Stori Expense Tracker

A modern, full-stack expense tracker with AI-powered financial advice built for Stori's Generative AI Squad technical challenge.

![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

## ✨ Features

### 📊 **Data Visualization**

- Interactive expense summary with category breakdowns
- Timeline charts showing income vs expenses over time
- Responsive charts optimized for mobile devices
- Real-time data updates with React Query

### 🤖 **AI Financial Advisor**

- Personalized financial advice based on spending patterns
- Multi-provider AI support (OpenAI, Azure, AWS Bedrock, Ollama, OpenRouter)
- Contextual recommendations using transaction history
- Chat-style interface with message history

### 🔐 **Authentication & Security**

- Secure authentication with Supabase Auth
- JWT token-based authorization
- Row Level Security (RLS) for data protection
- Protected routes and API endpoints

### 📱 **Mobile-First Design**

- Responsive design for all screen sizes (320px+)
- Touch-optimized interactions
- Dark mode by default
- Progressive Web App (PWA) ready

### 🚀 **Production Ready**

- Docker containerization for easy deployment
- Performance optimized (40% bundle size reduction)
- Comprehensive error handling and fallback UI
- WCAG accessibility compliance

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST     ┌──────────────────┐
│   React Frontend │ ──────────────► │  FastAPI Backend │
│   (TypeScript)   │                 │    (Python)      │
└─────────────────┘                 └──────────────────┘
         │                                    │
         │                                    │
         ▼                                    ▼
┌─────────────────┐                 ┌──────────────────┐
│   Supabase Auth │                 │ Supabase Database│
│   (JWT Tokens)  │                 │   (PostgreSQL)   │
└─────────────────┘                 └──────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │   AI Providers   │
                                    │ (OpenAI/Ollama) │
                                    └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ with **bun** package manager
- **Python** 3.13+ with **uv** package manager
- **Docker** and **Docker Compose** (for containerized deployment)
- **Supabase** account (for database and authentication)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/stori-expense-tracker.git
cd stori-expense-tracker
```

### 2. Environment Setup

Create `.env` files in both `backend/` and `frontend/` directories:

#### Backend `.env`
You can copy from the provided `.env.example` file in the `backend/` directory and fill in your actual values.

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# AI provider Configuration
OPENAI_API_KEY=your-openai-api-key
DEFAULT_LLM_PROVIDER=openai

# Ollama Configuration
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama27b-chat

# OpenRouter Configuration
OPENROUTER_API_KEY=your-openrouter-api-key

# Application Settings
ENVIRONMENT=development
DEBUG=true
```

#### Frontend `.env`
You can copy from the provided `.env.example` file in the `frontend/` directory and fill in your actual values.

```bash
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Database Setup

Set up your Supabase database with the provided schema:

```bash
cd backend
uv run python setup_database.py
```

This will create all tables and populate with 232+ sample transactions across 5 user profiles.

### 4. Development Mode

#### Option A: Docker Compose (Recommended)

```bash
docker-compose up --build
```

#### Option B: Manual Setup

```bash
# Backend
cd backend
uv sync
uv run python main.py

# Frontend (in another terminal)
cd frontend
bun install
bun dev
```

### 5. Access the Application

- **Frontend**: http://localhost:5173 (or :3000 with Docker)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 6. Test Authentication

Use these test credentials:

- **Email**: `test@example.com`
- **Password**: `Test123!`

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint             | Description       |
| ------ | -------------------- | ----------------- |
| POST   | `/api/auth/register` | Register new user |
| POST   | `/api/auth/login`    | User login        |
| GET    | `/api/auth/profile`  | Get user profile  |

### Transaction Endpoints

| Method | Endpoint                 | Description            |
| ------ | ------------------------ | ---------------------- |
| GET    | `/api/transactions`      | List user transactions |
| POST   | `/api/transactions`      | Create transaction     |
| PUT    | `/api/transactions/{id}` | Update transaction     |
| DELETE | `/api/transactions/{id}` | Delete transaction     |

### Analytics Endpoints

| Method | Endpoint                     | Description                 |
| ------ | ---------------------------- | --------------------------- |
| GET    | `/api/expenses/summary`      | Expense summary by category |
| GET    | `/api/transactions/timeline` | Timeline data for charts    |

### AI Advisor Endpoints

| Method | Endpoint         | Description                       |
| ------ | ---------------- | --------------------------------- |
| POST   | `/api/ai/advice` | Get personalized financial advice |
| GET    | `/api/ai/config` | Get AI configuration              |
| PUT    | `/api/ai/config` | Update AI settings                |

## 🔧 Development

### Project Structure

```
stori-expense-tracker/
├── backend/                 # FastAPI Python backend
│   ├── src/
│   │   ├── modules/        # Feature modules (transactions, expenses, timeline, ai)
│   │   ├── core/           # Core models and types
│   │   ├── services/       # Business logic services
│   │   └── providers/      # External integrations (AI, embeddings)
│   ├── main.py            # FastAPI application entry point
│   └── Dockerfile         # Backend containerization
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API client and utilities
│   │   └── types/         # TypeScript type definitions
│   ├── nginx.conf         # Production nginx configuration
│   └── Dockerfile         # Frontend containerization
├── docker-compose.yml     # Multi-service orchestration
└── README.md             # This file
```

### Code Quality

- **Backend**: Black formatting, FastAPI auto-docs
- **Frontend**: ESLint + Prettier, TypeScript strict mode
- **Testing**: Pytest (backend), Vitest (frontend)
- **File Size**: ≤150 lines per file (target 100)

### Package Management

- **Frontend**: Use `bun` exclusively (`bun install`, `bun add`, `bun dev`)
- **Backend**: Use `uv` exclusively (`uv sync`, `uv add`, `uv run`)

## 🚀 Production Deployment

### AWS Deployment (Recommended)

1. **Backend**: Deploy to EC2 with Docker
2. **Frontend**: Deploy to S3 + CloudFront
3. **Database**: Use hosted Supabase
4. **Environment**: Configure production environment variables

### Docker Production Build

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
uv run pytest
```

### Run Frontend Tests

```bash
cd frontend
bun test
```

### Integration Testing

```bash
# Start both services
docker-compose up -d

# Run end-to-end tests
cd frontend
bun run test:e2e
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, email support@stori.com or create an issue on GitHub.

## 🙏 Acknowledgments

- Built for Stori's Generative AI Squad technical challenge
- Powered by Supabase, FastAPI, and React
- AI capabilities by OpenAI and LangChain
- UI components by Shadcn/ui and Tailwind CSS

---

**⭐ If you find this project helpful, please give it a star on GitHub!**
