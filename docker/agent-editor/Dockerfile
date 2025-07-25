# Agent 5: Gemini 2.5 Pro - Editor/Fact-Checker
# Verifies citations, corrects errors, and formats according to MLA/firm standards
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy editor service code
COPY editor_service.py .
COPY fact_checker.py .
COPY citation_verifier.py .
COPY mla_formatter.py .
COPY templates/ ./templates/
COPY utils/ ./utils/

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=editor-fact-checker
ENV MODEL_NAME=gemini-2.5-pro
ENV ENABLE_GOOGLE_SEARCH=true
ENV MLA_VERSION=9
ENV FIRM_TEMPLATES_PATH=/app/templates

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8005/health')"

EXPOSE 8005

CMD ["python", "editor_service.py"]