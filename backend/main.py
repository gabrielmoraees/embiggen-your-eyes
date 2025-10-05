"""
Embiggen Your Eyes - Backend API
Application entry point
"""
from app.core.app import create_app
from app.core.config import settings

# Create the application
app = create_app()

# Startup
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)