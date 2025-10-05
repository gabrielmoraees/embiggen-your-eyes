"""
FastAPI application factory and configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes import catalog, views, annotations, collections
from app.data.catalog import initialize_catalog


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION
    )
    
    # Mount static tiles directory
    settings.TILES_CACHE_PATH.mkdir(exist_ok=True)
    app.mount("/tiles", StaticFiles(directory=str(settings.TILES_CACHE_PATH)), name="tiles")
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    
    # Root endpoints
    @app.get("/")
    def root():
        """API root"""
        return {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "description": settings.DESCRIPTION
        }
    
    @app.get("/api/health")
    def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "version": settings.VERSION}
    
    # Include routers
    app.include_router(catalog.router, prefix="/api", tags=["catalog"])
    app.include_router(views.router, prefix="/api", tags=["views"])
    app.include_router(annotations.router, prefix="/api", tags=["annotations"])
    app.include_router(collections.router, prefix="/api", tags=["collections"])
    
    # Initialize data catalog on startup
    initialize_catalog()
    
    return app
