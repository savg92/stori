# Stori Expense Tracker Backend

A powerful FastAPI backend for expense tracking with AI-powered financial advice.

## Features

- **Expense Tracking**: Complete CRUD operations for transactions
- **AI Financial Advisor**: Multi-provider LLM support (OpenAI, Anthropic, Azure, AWS Bedrock)
- **User Authentication**: Supabase Auth integration with JWT middleware
- **Data Analytics**: Expense summaries, timeline aggregation, and spending insights
- **Database**: Supabase PostgreSQL with optimized queries
- **API Documentation**: Auto-generated OpenAPI docs

## Tech Stack

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **AI**: LangChain with multi-provider support
- **Validation**: Pydantic v2
- **Package Manager**: uv
- **Testing**: Pytest

## API Endpoints

### Authentication

- `POST /api/auth/login` - User authentication
- `GET /api/auth/me` - Get current user

### Transactions

- `GET /api/transactions` - List user transactions
- `POST /api/transactions` - Create new transaction
- `PUT /api/transactions/{id}` - Update transaction
- `DELETE /api/transactions/{id}` - Delete transaction

### Analytics

- `GET /api/expenses/summary` - Expense summary by category
- `GET /api/transactions/timeline` - Timeline data for charts

### AI Advisor

- `POST /api/ai/advice` - Get personalized financial advice
- `GET /api/ai/config` - Get AI configuration
- `PUT /api/ai/config` - Update AI settings

### Health

- `GET /api/health` - System health check

## Quick Start

1. **Environment Setup**:

   ```bash
   cp .env.example .env
   # Configure Supabase and AI provider credentials
   ```

2. **Install Dependencies**:

   ```bash
   uv sync
   ```

3. **Run Development Server**:

   ```bash
   uv run uvicorn main:app --reload
   ```

4. **Access API Documentation**:
   - OpenAPI docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Docker Development

```bash
# Build and run with Docker Compose
docker-compose up backend

# View logs
docker-compose logs -f backend
```

## Configuration

### Required Environment Variables

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_PUBLISHABLE_KEY`: Supabase publishable key

### AI Configuration (Optional)

- `OPENAI_API_KEY`: OpenAI API key for AI advice
- `DEFAULT_LLM_PROVIDER`: AI provider (openai, anthropic, azure, bedrock)

## Architecture

The backend follows a service-oriented architecture:

```
backend/
├── api/           # FastAPI routes and middleware
├── core/          # Data models and types
├── services/      # Business logic and integrations
├── providers/     # AI provider implementations
└── config/        # Configuration and settings
```

## Development

- **Code Style**: Black formatter
- **Type Checking**: mypy
- **Testing**: pytest with coverage
- **Documentation**: Auto-generated from FastAPI

## Contributing

1. Follow the backend agent guidelines in `/backend_agent.md`
2. Keep services under 150 lines
3. Separate controllers, services, and repositories
4. Include tests for new features
5. Update API documentation

6. Include tests for new features
7. Update API documentation

## Testing

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=.

# Run specific test file
uv run pytest tests/test_auth.py
```

## Authentication

The backend uses Supabase Auth with JWT tokens. Test users are available:

- **Alex Johnson**: `alex.johnson.test123@gmail.com` / `testpassword123`
- **Maria Garcia**: `maria.garcia.test123@gmail.com` / `testpassword123`
- **Sam Chen**: `sam.chen.test123@gmail.com` / `testpassword123`
- **Robert Smith**: `robert.smith.test123@gmail.com` / `testpassword123`

Each test account has different financial data for comprehensive testing.

## Production Deployment

```bash
# Build Docker image
docker build -t stori-backend .

# Run production container
docker run -p 8000:8000 --env-file .env stori-backend
```

## Support

For backend-specific issues:

1. Check the API documentation at `/docs`
2. Review logs with `uv run uvicorn main:app --log-level debug`
3. Ensure all environment variables are properly configured
4. Verify Supabase connection and authentication setup
