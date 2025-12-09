"""
Main FastAPI application for RAG Evaluation Backend
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings


# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events

    Args:
        app: FastAPI application instance
    """
    # Startup: Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    print(f"[STARTUP] Starting {settings.API_TITLE} v{settings.API_VERSION}")
    print(f"[STARTUP] Upload directory: {upload_dir.absolute()}")

    yield

    # Shutdown
    print("[SHUTDOWN] Shutting down API server")


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information

    Returns:
        dict: API information
    """
    return {
        "success": True,
        "message": f"Welcome to {settings.API_TITLE}",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


# Health check endpoint
@app.get(f"{settings.API_PREFIX}/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns:
        dict: Health status
    """
    return {
        "success": True,
        "status": "healthy",
        "message": "API is running",
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSONResponse: Error response
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "message": "Internal server error",
        },
    )


# Import and include routers
from app.routes import documents, evaluations, analysis, results

app.include_router(documents.router, prefix=settings.API_PREFIX, tags=["Documents"])
app.include_router(evaluations.router, prefix=settings.API_PREFIX, tags=["Evaluations"])
app.include_router(analysis.router, prefix=settings.API_PREFIX, tags=["Analysis"])
app.include_router(results.router, prefix=settings.API_PREFIX, tags=["Results"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
    )
