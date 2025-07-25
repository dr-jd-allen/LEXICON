# LEXICON API Keys Usage Guide

## Overview
This document explains how each API key in your `.env` file is used by the LEXICON system.

## API Keys Configuration

### 1. **ANTHROPIC_API_KEY**
- **Used by**: Agent 1 (Claude Opus 4) - Main Orchestrator
- **Purpose**: 
  - Orchestrates the entire pipeline
  - Searches internal ChromaDB corpus
  - Strategic editing of briefs
  - Document metadata extraction during preprocessing
- **Location**: `lexicon_pipeline.py`, `document_processor.py`

### 2. **OPENAI_API_KEY**
- **Used by**: 
  - Agent 2 (o3-pro-deep-research)
  - Agent 3 (gpt-4.1-2025-04-14)
  - Agent 4 (gpt-4.5)
  - Vector embeddings
- **Purpose**:
  - Deep legal/forensic research analysis (Agent 2)
  - Scientific research analysis (Agent 3)
  - Initial brief drafting (Agent 4)
  - Creating embeddings for ChromaDB
- **Location**: `lexicon_pipeline.py`, `document_processor.py`

#### Agent 2 Special Configuration:
- **Model**: `o3-pro-deep-research`
- **Reasoning Effort**: `high` (for maximum analysis depth)
- **Data Sources**: 
  - External databases (CourtListener, Google Scholar, Westlaw, PACER)
  - Local corpus (8,505 documents in ChromaDB)
- **RAG Strategy**: Cross-references external precedents with local expert history

### 3. **GOOGLEAI_STUDIO_API_KEY**
- **Used by**: Agent 5 (Gemini 2.5 Pro)
- **Purpose**:
  - Final fact-checking
  - Brief polishing
  - Format verification
- **Location**: `lexicon_pipeline.py`
- **Model**: `models/gemini-2.5-pro`

#### Agent 5 Special Configuration:
- **Google Search Grounding**: Enabled via `tools='google_search_retrieval'`
- **Fact-Checking Features**:
  - Verifies case citations are real and correctly cited
  - Confirms expert credentials and affiliations
  - Validates scientific claims and methodologies
  - Checks dates, court names, and judge names
  - Verifies statistics and research findings
- **Real-time validation**: Uses Google Search to verify any uncertain claims

### 4. **SERP_API_KEY**
- **Used by**: Agents 2 & 3
- **Purpose**:
  - Google Scholar searches (both legal and scientific)
  - No separate Google Scholar API needed
- **Location**: `lexicon_external_research.py`
- **Features**:
  - Legal precedent searches (Agent 2)
  - Scientific paper searches (Agent 3)
  - Citation counts, PDF links, author information

### 5. **Google Cloud Keys** (for future use)
- **GOOGLE_CLOUD_API_KEY**: General Google Cloud services
- **VERTEX_API_KEY**: Vertex AI services (could be used for custom models)
- **Project details**: spinwheel-464709

### 6. **Database Keys**
- **CHROMA_HOST/PORT**: Vector database connection
- **REDIS_HOST/PORT**: Caching and task queue (if needed)
- **Notion Integration Secrets**: For potential document import

## Agent Assignment Summary

| Agent | Model | API Key Used | Purpose & Features |
|-------|-------|--------------|---------|
| Agent 1 | Claude Opus 4 | ANTHROPIC_API_KEY | Orchestration & Strategy |
| Agent 2 | o3-pro-deep-research | OPENAI_API_KEY | Legal Research (External DBs + Local Corpus RAG, reasoning_effort="high") |
| Agent 3 | gpt-4.1-2025-04-14 | OPENAI_API_KEY | Scientific Research |
| Agent 4 | gpt-4.5 | OPENAI_API_KEY | Initial Drafting |
| Agent 5 | models/gemini-2.5-pro | GOOGLEAI_STUDIO_API_KEY | Fact Checking (with Google Search grounding) |

## External Research APIs

| Service | API Key | Used For |
|---------|---------|----------|
| Google Scholar | SERP_API_KEY | Legal & scientific literature |
| PubMed | PUBMED_API_KEY (optional) | Medical research |
| CourtListener | COURTLISTENER_API_KEY (optional) | Case law |
| Firecrawl | FIRECRAWL_API_KEY (optional) | Web scraping |

## Testing API Configuration

```python
# Test if all APIs are configured correctly
import os
from dotenv import load_dotenv

load_dotenv()

apis = {
    'Anthropic': os.getenv('ANTHROPIC_API_KEY'),
    'OpenAI': os.getenv('OPENAI_API_KEY'),
    'Google AI': os.getenv('GOOGLEAI_STUDIO_API_KEY'),
    'SerpAPI': os.getenv('SERP_API_KEY')
}

for name, key in apis.items():
    if key:
        print(f"✓ {name}: Configured ({key[:20]}...)")
    else:
        print(f"✗ {name}: Not configured")
```

## Security Notes

1. **Never commit `.env` file** to version control
2. **Rotate keys regularly** for production use
3. **Use environment-specific keys** (dev/staging/prod)
4. **Monitor API usage** to prevent unexpected charges
5. **Set rate limits** in your application code

## Cost Optimization

- **Claude Opus 4**: Most expensive, use strategically
- **GPT-4/4.1**: Moderate cost, bulk of analysis
- **Gemini 2.5 Pro**: Cost-effective for fact-checking
- **SerpAPI**: Pay per search, batch queries when possible