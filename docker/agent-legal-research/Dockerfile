# Agent 2: o3-pro-deep-research - Legal Analyst
# Searches legal precedents from internal corpus and external databases
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy legal research code
COPY legal_research_service.py .
COPY external_databases.py .
COPY corpus_searcher.py .
COPY legal_analysis.py .
COPY utils/ ./utils/

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=legal-research
ENV MODEL_NAME=o3-pro-deep-research
ENV REASONING_EFFORT=high
ENV ENABLE_CORPUS_SEARCH=true
ENV ENABLE_EXTERNAL_SEARCH=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health')"

EXPOSE 8002

CMD ["python", "legal_research_service.py"]