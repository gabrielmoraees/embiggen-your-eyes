"""
Application configuration
"""
from pathlib import Path


class Settings:
    """Application settings"""
    APP_NAME = "Embiggen Your Eyes API"
    VERSION = "1.0.0"
    DESCRIPTION = "Hierarchical map data model with sources, maps, variants, and layers"
    
    # CORS settings
    CORS_ORIGINS = ["*"]
    CORS_CREDENTIALS = True
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]
    
    # Paths
    TILES_CACHE_PATH = Path("./tiles_cache")
    
    # Server settings
    HOST = "0.0.0.0"
    PORT = 8000


settings = Settings()
