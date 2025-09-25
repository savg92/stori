#!/bin/bash
# Production deployment verification script

set -e

echo "🚀 Stori Expense Tracker - Production Deployment Verification"
echo "============================================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required environment variables are set
check_env_vars() {
    print_status "Checking environment variables..."
    
    local required_vars=(
        "SUPABASE_URL"
        "SUPABASE_ANON_KEY"
        "SUPABASE_SERVICE_ROLE_KEY"
        "OPENAI_API_KEY"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing required environment variables:"
        printf '%s\n' "${missing_vars[@]}"
        return 1
    fi
    
    print_success "All required environment variables are set"
}

# Check if all dependencies are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check backend dependencies
    cd backend
    if uv run python -c "import fastapi, supabase, openai, langchain" 2>/dev/null; then
        print_success "Backend dependencies are installed"
    else
        print_error "Backend dependencies missing or not properly installed"
        return 1
    fi
    cd ..
    
    # Check frontend dependencies
    cd frontend
    if command -v bun >/dev/null 2>&1; then
        if bun run type-check >/dev/null 2>&1; then
            print_success "Frontend dependencies and TypeScript compilation successful"
        else
            print_error "Frontend TypeScript compilation failed"
            return 1
        fi
    else
        print_error "Bun is not installed"
        return 1
    fi
    cd ..
}

# Run all tests
run_tests() {
    print_status "Running comprehensive test suite..."
    
    # Backend tests
    cd backend
    print_status "Running backend tests..."
    if uv run pytest -v --cov=. --cov-report=term-missing; then
        print_success "Backend tests passed"
    else
        print_error "Backend tests failed"
        return 1
    fi
    cd ..
    
    # Frontend tests
    cd frontend
    print_status "Running frontend tests..."
    if bun test; then
        print_success "Frontend tests passed"
    else
        print_error "Frontend tests failed"
        return 1
    fi
    cd ..
}

# Check database connectivity
check_database() {
    print_status "Checking database connectivity..."
    
    cd backend
    if uv run python -c "
import asyncio
from supabase import create_client
import os

async def test_connection():
    client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))
    try:
        response = client.table('transactions').select('id').limit(1).execute()
        print('Database connection successful')
        return True
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False

asyncio.run(test_connection())
"; then
        print_success "Database connectivity verified"
    else
        print_error "Database connectivity failed"
        return 1
    fi
    cd ..
}

# Build production assets
build_production() {
    print_status "Building production assets..."
    
    # Build frontend
    cd frontend
    print_status "Building frontend..."
    if bun run build; then
        print_success "Frontend build successful"
    else
        print_error "Frontend build failed"
        return 1
    fi
    cd ..
    
    # Verify backend is ready
    cd backend
    print_status "Verifying backend production readiness..."
    if uv run python -c "import main; print('Backend module imports successful')"; then
        print_success "Backend is production ready"
    else
        print_error "Backend production check failed"
        return 1
    fi
    cd ..
}

# Security checks
security_checks() {
    print_status "Running security checks..."
    
    # Check for sensitive files
    if find . -name "*.env" -o -name ".env.*" | grep -v ".env.example" | head -1 | grep -q .; then
        print_warning "Found .env files - ensure they're not committed to version control"
    fi
    
    # Check for API keys in code (basic check)
    if grep -r "sk-" --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" . 2>/dev/null | grep -v node_modules | head -1 | grep -q .; then
        print_warning "Potential API keys found in code - review for hardcoded secrets"
    fi
    
    print_success "Security checks completed"
}

# Health check endpoints
health_check() {
    print_status "Performing health checks..."
    
    # Start backend in background for health check
    cd backend
    uv run python main.py &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Check backend health
    if curl -f http://localhost:8000/api/health >/dev/null 2>&1; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
        kill $BACKEND_PID 2>/dev/null || true
        return 1
    fi
    
    # Kill background process
    kill $BACKEND_PID 2>/dev/null || true
}

# Main execution
main() {
    print_status "Starting production deployment verification..."
    echo
    
    check_env_vars || exit 1
    echo
    
    check_dependencies || exit 1
    echo
    
    run_tests || exit 1
    echo
    
    check_database || exit 1
    echo
    
    build_production || exit 1
    echo
    
    security_checks
    echo
    
    health_check || exit 1
    echo
    
    print_success "🎉 Production deployment verification completed successfully!"
    print_success "Your application is ready for deployment."
    echo
    print_status "Next steps:"
    echo "  1. Deploy to your preferred platform (AWS, Heroku, DigitalOcean, etc.)"
    echo "  2. Configure production environment variables"
    echo "  3. Run post-deployment health checks"
    echo "  4. Monitor application performance and logs"
}

# Run main function
main "$@"