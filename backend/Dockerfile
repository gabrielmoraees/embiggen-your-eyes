# Embiggen Your Eyes - Backend Dockerfile
# Optimized for Google Cloud Run deployment

FROM python:3.11-slim

# Install system dependencies including GDAL
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p tiles_cache downloads

# Expose port (Cloud Run will set PORT env var)
ENV PORT=8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
