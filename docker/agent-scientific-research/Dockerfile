# Agent 3: o4-mini-deep-research - Scientific Domain Specialist
# Retrieves and analyzes medical/scientific literature for TBI cases
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scientific research code
COPY scientific_research_service.py .
COPY pubmed_client.py .
COPY scholar_client.py .
COPY domain_knowledge_store.py .
COPY medical_analysis.py .
COPY utils/ ./utils/

# Create knowledge storage directory
RUN mkdir -p /app/knowledge

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=scientific-research
ENV MODEL_NAME=o4-mini-deep-research
ENV ENABLE_DOMAIN_KNOWLEDGE=true
ENV KNOWLEDGE_STORE_PATH=/app/knowledge

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8003/health')"

EXPOSE 8003

CMD ["python", "scientific_research_service.py"]