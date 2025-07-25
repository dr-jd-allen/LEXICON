# Agent 4: gpt-4.5-research-preview - Brief Writer
# Synthesizes research findings into compelling legal briefs
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy writer service code
COPY writer_service.py .
COPY brief_generator.py .
COPY legal_strategies.py .
COPY brief_templates/ ./brief_templates/
COPY strategies/ ./strategies/
COPY utils/ ./utils/

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=brief-writer
ENV MODEL_NAME=gpt-4.5-research-preview
ENV ENABLE_STRATEGY_SELECTION=true
ENV BRIEF_TEMPLATES_PATH=/app/brief_templates
ENV STRATEGIES_PATH=/app/strategies

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8004/health')"

EXPOSE 8004

CMD ["python", "writer_service.py"]