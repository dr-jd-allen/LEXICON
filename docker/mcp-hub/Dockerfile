# MCP Server Hub - Model Context Protocol Management
# Enables inter-agent communication and shared context
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

# Copy MCP hub code
COPY mcp_hub_service.py .
COPY mcp_server.py .
COPY mcp_client.py .
COPY communication_broker.py .
COPY utils/ ./utils/

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV SERVICE_NAME=mcp-hub
ENV ENABLE_FILESYSTEM_SERVER=true
ENV ENABLE_MEMORY_SERVER=true
ENV ENABLE_FETCH_SERVER=true
ENV ENABLE_GITHUB_SERVER=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8006/health')"

EXPOSE 8006

CMD ["python", "mcp_hub_service.py"]