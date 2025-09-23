# Stori Expense Tracker - Docker Development Guide

## Quick Start

1. **Copy environment template**:

   ```bash
   cp .env.example .env
   ```

2. **Configure Supabase** (required):

   - Create a Supabase project at https://supabase.com
   - Copy your project URL and keys to `.env` file
   - Update `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY`

3. **Configure AI Provider** (optional):

   - Add your OpenAI API key to `OPENAI_API_KEY` in `.env`
   - Or configure alternative providers (Anthropic, Azure, AWS)

4. **Start the backend**:

   ```bash
   docker-compose up backend
   ```

5. **Access the application**:
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

## Development Workflow

### Backend Only

```bash
# Start backend service
docker-compose up backend

# View logs
docker-compose logs -f backend

# Rebuild after code changes
docker-compose build backend && docker-compose up backend
```

### Full Stack (when frontend is ready)

```bash
# Start all services
docker-compose --profile frontend up

# Or start specific services
docker-compose up backend frontend
```

### Development Commands

```bash
# Stop all services
docker-compose down

# Remove volumes (reset data)
docker-compose down -v

# Rebuild all images
docker-compose build

# View service status
docker-compose ps
```

## Service Details

### Backend Service

- **Port**: 8000
- **Health Check**: Automated via Docker
- **Auto-reload**: Enabled for development
- **Volume Mount**: `./backend:/app` for live code updates

### Frontend Service (Coming Soon)

- **Port**: 3000
- **Profile**: `frontend` (optional startup)
- **Dependencies**: Waits for backend to be healthy

## Environment Variables

### Required for Backend

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Public anon key for client operations
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for admin operations

### Optional for AI Features

- `OPENAI_API_KEY`: For AI financial advice
- `DEFAULT_LLM_PROVIDER`: AI provider (openai, anthropic, azure)

### Development Settings

- `ENVIRONMENT`: Set to `development` for debug features
- `DEBUG`: Enable detailed logging and error traces

## Troubleshooting

### Backend Won't Start

1. Check Supabase configuration in `.env`
2. Verify Docker is running
3. Check logs: `docker-compose logs backend`

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Use different ports in docker-compose.yml
ports:
  - "8001:8000"  # External:Internal
```

### Database Connection Issues

1. Verify Supabase URL and keys are correct
2. Check Supabase project is active
3. Ensure service role key has proper permissions

## Next Steps

1. **Database Setup**: Create tables in your Supabase project
2. **Frontend Development**: Initialize React application
3. **API Testing**: Use http://localhost:8000/docs for API exploration
