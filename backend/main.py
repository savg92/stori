"""Main application entry point for Stori Expense Tracker."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import modular components
from config.settings import get_settings
from api.routes import router

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()
    
    logging.info("Stori Expense Tracker startup: Initializing services...")
    
    try:
        # Initialize Supabase client
        from services.supabase_service import get_supabase_client
        supabase = get_supabase_client()
        
        # Test database connection
        try:
            health = await supabase.health_check()
            if health["status"] == "healthy":
                logging.info("✅ Supabase connection established successfully")
            else:
                logging.warning(f"⚠️  Supabase connection degraded: {health}")
        except Exception as db_error:
            logging.warning(f"⚠️  Supabase connection test failed: {db_error}")
        
        # Initialize AI services (optional)
        try:
            from providers.llms import LLMProviderFactory
            llm_provider = LLMProviderFactory.create_llm()
            if llm_provider:
                logging.info(f"✅ AI Provider initialized: {llm_provider.__class__.__name__}")
            else:
                logging.info("ℹ️  AI Provider not configured - running in fallback mode")
        except Exception as ai_error:
            logging.warning(f"⚠️  AI Provider initialization failed: {ai_error}")
        
        logging.info("Stori Expense Tracker initialized successfully.")

    except Exception as e:
        logging.error(f"Startup failed due to Initialization Error: {e}", exc_info=True)
        raise RuntimeError(f"Application startup failed due to Initialization Error: {e}")

    yield

    logging.info("Stori Expense Tracker shutdown.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Stori Expense Tracker API",
        description="AI-powered expense tracking with financial insights",
        version="1.0.0",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(router, prefix="/api")
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
