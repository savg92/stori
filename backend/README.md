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
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key

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

- **Multi-Vector-Store Architecture**: Isolated databases for each embedding configuration
- **Conversational Memory**: Session-based chat history with follow-up support
- **FastAPI Backend**: Modern async API with automatic OpenAPI documentation
- **Multiple Provider Support**: Configurable LLM and embedding providers
- **Automatic Database Creation**: Smart initialization and model switching
- **Vector Store Management**: Complete API and CLI management tools
- **CORS Enabled**: Frontend-ready with configurable origins

## 🚀 **Quick Start**

### 1. **Setup Environment**

```bash
# Clone and navigate
git clone https://github.com/savg92/ai_agent_app
cd ai_agent_app/backend

# Create environment (choose one)
uv venv .venv              # Using uv (recommended)
python -m venv .venv       # Using standard Python

# Activate environment
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate     # On Windows
```

### 2. **Install Dependencies**

```bash
# Modern approach (recommended)
uv pip install -r requirements.txt

# Or traditional approach
pip install -r requirements.txt
```

### 3. **Configure Environment**

```bash
# Copy and edit configuration
cp .env.example .env
# Edit .env with your preferred providers and API keys
```

### 4. **Start the Server**

```bash
# From the backend directory
uv run python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Or using Python directly
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be accessible at `http://localhost:8000` with API docs at `http://localhost:8000/docs`.

## ⚙️ **Configuration**

The modular architecture centralizes all configuration in the `config/` module. All settings are loaded from environment variables with validation and type conversion.

### **Provider Configuration**

**OpenAI:**

```bash
EMBEDDING_PROVIDER=openai
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

**Ollama:**

```bash
EMBEDDING_PROVIDER=ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=granite-embedding:278m
OLLAMA_LLM_MODEL=llama3.2:3b
```

**Azure OpenAI:**

```bash
EMBEDDING_PROVIDER=azure
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
AZURE_OPENAI_LLM_DEPLOYMENT_NAME=gpt-35-turbo
```

**LM Studio:**

```bash
EMBEDDING_PROVIDER=lmstudio
LLM_PROVIDER=lmstudio
LM_STUDIO_BASE_URL=http://localhost:1234
LM_STUDIO_EMBEDDING_MODEL=text-embedding-qwen3-embedding-0.6b
LM_STUDIO_MODEL=qwen2.5-coder-7b-instruct
```

**AWS Bedrock:**

```bash
EMBEDDING_PROVIDER=bedrock
LLM_PROVIDER=bedrock
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
BEDROCK_MODEL_ID=anthropic.claude-v2
AWS_REGION=us-east-1
```

## 🔧 **API Usage**

### **Ask Questions**

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this application about?",
    "session_id": "user-session-123"
  }'
```

### **Vector Store Management**

````bash
# List all vector stores
curl -X GET "http://localhost:8000/vector-stores"

# Delete a specific store
curl -X DELETE "http://localhost:8000/vector-stores/ollama_granite-embedding_278m"

# Rebuild current store
curl -X POST "http://localhost:8000/vector-stores/rebuild" \
  -H "Content-Type: application/json" \
  -d '{"force": true}'

# Health check
curl -X GET "http://localhost:8000/health"

### **Runtime LLM Switching**

You can change the LLM provider without restarting the server. The vector store and sessions remain intact.

```bash
# Inspect current LLM
curl -X GET "http://localhost:8000/llm"

# Switch to Ollama (example)
curl -X POST "http://localhost:8000/llm" \
    -H "Content-Type: application/json" \
    -d '{
        "provider": "ollama",
        "ollama_llm_model": "llama3.2:3b",
        "ollama_base_url": "http://localhost:11434",
        "llm_temperature": 0.7
    }'

# Switch to Azure OpenAI (example)
curl -X POST "http://localhost:8000/llm" \
    -H "Content-Type: application/json" \
    -d '{
        "provider": "azure",
        "azure_api_key": "<key>",
        "azure_endpoint": "https://<resource>.openai.azure.com/",
        "azure_api_version": "2024-02-01",
        "azure_llm_deployment": "gpt-4o-mini"
    }'
````

````

## 🧩 **Modular Development**

### **Adding a New Provider**

1. **Update Provider Factory** (`providers/embeddings.py` or `providers/llms.py`):

```python
elif provider == "new_provider":
    # Implementation here
    return NewProviderEmbeddings(...)
````

2. **Add Configuration** (`config/settings.py`):

```python
# Add new provider settings
self.new_provider_api_key = os.getenv("NEW_PROVIDER_API_KEY")
```

### **Runtime Embedding Switching**

Switch the embedding provider/model at runtime. If a matching vector store exists, it will be loaded; otherwise, a new one will be built from the documents in `data/`.

```bash
# Inspect current embeddings
curl -X GET "http://localhost:8000/embeddings"

# Switch to Ollama embeddings (example)
curl -X POST "http://localhost:8000/embeddings" \
    -H "Content-Type: application/json" \
    -d '{
        "provider": "ollama",
        "ollama_embedding_model": "granite-embedding:278m",
        "ollama_base_url": "http://localhost:11434"
    }'

# Switch to LM Studio embeddings (example)
curl -X POST "http://localhost:8000/embeddings" \
    -H "Content-Type: application/json" \
    -d '{
        "provider": "lmstudio",
        "lm_studio_embedding_model": "text-embedding-qwen3-embedding-0.6b",
        "lm_studio_base_url": "http://localhost:1234"
    }'
```

### **Creating a New Service**

1. **Create Service** (`services/new_service.py`):

```python
class NewService:
    def __init__(self):
        self.settings = get_settings()

    def do_something(self):
        # Implementation here
        pass
```

2. **Update Exports** (`services/__init__.py`):

```python
from .new_service import NewService
__all__.append("NewService")
```

### **Adding API Endpoints**

Add to `api/routes.py`:

```python
@router.get("/new-endpoint")
def new_endpoint():
    service = NewService()
    return service.do_something()
```

## 🧪 **Testing**

The modular structure makes testing straightforward:

```python
# Test individual services
def test_document_service():
    service = DocumentService()
    documents, failed = service.load_documents_from_directory("/path/to/docs")
    assert len(documents) > 0

# Test providers
def test_embedding_factory():
    embeddings = EmbeddingProviderFactory.create_embedding_function("openai")
    assert embeddings is not None
```

## 📊 **Multi-Vector Store System**

Each embedding configuration gets its own isolated vector database:

- **Automatic Creation**: New stores created when switching models
- **Metadata Tracking**: Creation time, document count, usage statistics
- **Easy Switching**: Change `.env` and restart - no data loss
- **CLI Management**: Full command-line management tools
- **API Management**: RESTful endpoints for programmatic control

## 🔍 **Migration from Legacy**

The application maintains **100% API compatibility** with the previous monolithic version. All existing endpoints work exactly the same way, but the internal implementation is now much cleaner and more maintainable.

**Migration artifacts:**

- `backup_original/` - Contains original monolithic files
- `MODULAR_ARCHITECTURE.md` - Detailed architecture documentation
- `MIGRATION_COMPLETE.md` - Migration summary and validation

## 🛠️ **Development Workflow**

1. **Make changes** to specific modules based on functionality
2. **Use dependency injection** to pass services between modules
3. **Keep API layer thin** - business logic belongs in services
4. **Add environment variables** in `config/settings.py`
5. **Update type definitions** in `core/types.py` as needed

## 📚 **Documentation**

- **`MODULAR_ARCHITECTURE.md`** - Complete architecture guide
- **`MIGRATION_COMPLETE.md`** - Migration summary and status
- **`CLEANUP_SUMMARY.md`** - File cleanup documentation
- **OpenAPI Docs** - Available at `http://localhost:8000/docs`

## 🚦 **Production Ready**

The modular architecture provides a solid foundation for production deployment:

- **Clean separation of concerns**
- **Easy testing and mocking**
- **Configurable via environment variables**
- **Comprehensive error handling**
- **Structured logging**
- **Type safety with Pydantic**
- **Async-ready with FastAPI**

## 🎯 **Future Development**

The modular structure makes it easy to:

- Add new LLM/embedding providers
- Implement caching layers
- Add authentication and authorization
- Scale individual components
- Add monitoring and metrics
- Implement advanced RAG techniques
- Create specialized services for different use cases

---

**The AI Agent RAG Application is now production-ready with a professional, maintainable modular architecture! 🎉**

## 🔗 **Acknowledgments**

Built with modern, professional tools and libraries:

- **Core Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- **AI/ML Stack**: [Langchain](https://www.langchain.com/) - Framework for developing LLM applications
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) - AI-native open-source embedding database
- **Server**: [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/) - Data validation using Python type annotations

**Provider Integrations:**

- [OpenAI](https://openai.com/) - GPT models and embeddings
- [Ollama](https://ollama.com/) - Local LLM deployment platform
- [LM Studio](https://lmstudio.ai/) - Desktop application for running LLMs
- [Azure AI Services](https://azure.microsoft.com/en-us/products/ai-services/) - Microsoft's AI platform
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - Amazon's managed AI service
- [HuggingFace](https://huggingface.co/) - Open-source ML models and embeddings

## 🐛 **Troubleshooting**

### **Common Issues**

**🔧 Server Won't Start:**

```bash
# Make sure you're in the backend directory
cd /Users/your-path/ai_agent_app/backend

# Use the correct python command
uv run python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**🔧 Provider Connection Issues:**

- Ensure your LLM service is running (Ollama, LM Studio, etc.)
- Verify API keys in your `.env` file
- Check network connectivity for external providers

**🔧 Vector Store Issues:**

- Use `curl -X GET "http://localhost:8000/vector-stores"` to list available stores
- Check that documents exist in the `data/` directory
- Verify embedding provider configuration

**🔧 Import/Module Errors:**

- Ensure all dependencies are installed: `uv pip install -r requirements.txt`
- Verify you're using the correct Python environment
- Check that all required packages are available

### **Getting Help**

- **API Documentation**: Visit `http://localhost:8000/docs` when server is running
- **Logs**: Check console output for detailed error messages and stack traces
- **Configuration**: Verify your `.env` file matches `.env.example` format
- **GitHub Issues**: Report bugs or request features in the repository

## 📈 **What's New in v2.0 (Modular Architecture)**

### ✨ **Major Improvements**

- **🏗️ Complete Modular Refactor**: Clean separation of concerns across 5 main modules
- **🧪 Enhanced Testability**: Each component can be tested independently
- **📦 Modern Architecture**: Industry-standard patterns with dependency injection
- **🔧 Better Maintainability**: Changes isolated to specific modules
- **🚀 Developer Experience**: Clear structure for adding new features

### 🔄 **Migration Benefits**

- **100% API Compatibility**: All existing endpoints work unchanged
- **Zero Downtime**: Seamless transition from monolithic structure
- **Preserved Data**: All vector stores and configurations maintained
- **Enhanced Performance**: More efficient service instantiation and management
- **Professional Codebase**: Production-ready architecture patterns

### 🛠️ **Development Enhancements**

- **Factory Patterns**: Clean provider instantiation and management
- **Service Layer**: Clear business logic separation
- **Configuration Management**: Centralized environment handling
- **Type Safety**: Comprehensive TypedDict and Pydantic integration
- **Error Handling**: Structured exception management across modules

---

**Ready to build the future of document intelligence with a rock-solid, modular foundation! 🚀✨**
