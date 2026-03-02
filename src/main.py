"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings
from src.utils.logging import setup_logging
from src.middleware.error_handler import (
    app_error_handler,
    validation_error_handler,
    integrity_error_handler,
    general_exception_handler,
    AppError
)
from src.middleware.security import SecurityHeadersMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

# Setup logging
setup_logging()

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="User Authentication and Registration API",
    version="1.0.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Register error handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Trello Auth API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


# Include API routers
from src.api.v1 import auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )