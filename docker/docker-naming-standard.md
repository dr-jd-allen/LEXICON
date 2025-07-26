# Docker Naming Standards for LEXICON

## Container Naming Convention

All containers should follow this pattern:
```
lexicon-{component}-{environment}
```

Where:
- `{component}` is the service name (e.g., nginx, chromadb, redis, webapp)
- `{environment}` is optional and only used when differentiating environments (e.g., local, prod)

## Standard Names

### Core Services
- `lexicon-nginx` - Nginx reverse proxy
- `lexicon-chromadb` - ChromaDB vector database
- `lexicon-redis` - Redis cache
- `lexicon-webapp` - Main Flask web application

### Agent Services
- `lexicon-orchestrator` - Orchestrator agent (Claude Opus 4)
- `lexicon-legal-research` - Legal research agent
- `lexicon-scientific-research` - Scientific research agent
- `lexicon-writer` - Brief writer agent
- `lexicon-editor` - Editor agent (Gemini 2.5 Pro)

### Support Services
- `lexicon-mcp-hub` - MCP server hub

## Network Names
- `lexicon-network` - Main network for all services

## Volume Names
- `lexicon-chroma-data` - ChromaDB persistent storage
- `lexicon-redis-data` - Redis persistent storage
- `lexicon-uploads` - Uploaded documents
- `lexicon-briefs` - Generated briefs

## Image Names
When building custom images:
```
lexicon/{component}:{version}
```

Example: `lexicon/orchestrator:0.1.5`