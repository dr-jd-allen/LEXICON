# Agent 1: Claude Opus 4 Orchestrator
# Handles document anonymization, case analysis, and agent coordination
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy orchestrator code
COPY orchestrator_service.py .
COPY anonymizer.py .
COPY case_analyzer.py .
COPY utils/ ./utils/

# Copy MCP configuration
COPY mcp_client.py .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=orchestrator
ENV AGENT_MODEL=claude-opus-4-20250514
ENV ENABLE_ANONYMIZATION=true
ENV ENABLE_MCP=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')"

EXPOSE 8001

CMD ["python", "orchestrator_service.py"]