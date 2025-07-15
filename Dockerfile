# Dockerfile optimized for Google Cloud Run
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install GCP-specific dependencies
RUN pip install --no-cache-dir \
    cloud-sql-python-connector[pg8000] \
    google-cloud-storage \
    google-cloud-logging \
    google-cloud-secret-manager

# Copy application code
COPY . .

# Copy GCP configuration
COPY gcp_config/ ./gcp_config/

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/processed /app/output /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV ENVIRONMENT=production

# Cloud Run expects the app to listen on $PORT
EXPOSE 8080

# Use Streamlit with proper configuration for Cloud Run
CMD exec streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.serverAddress=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
