# LEXICON Web Application
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_webapp.txt .
RUN pip install --no-cache-dir -r requirements_webapp.txt

# Copy application code
COPY lexicon_webapp.py .
COPY lexicon_pipeline.py .
COPY lexicon_external_research.py .
COPY document_processor.py .
COPY lexicon_mcp_integration.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Create necessary directories
RUN mkdir -p uploads generated-briefs logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=lexicon_webapp.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["python", "lexicon_webapp.py"]