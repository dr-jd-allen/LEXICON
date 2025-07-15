# LEXICON GCP Services Mapping

## Service Replacements

### Dify → GCP Equivalent Mapping

1. **Dify Workflow Engine → Cloud Workflows + Cloud Tasks**
   - Cloud Workflows for orchestration
   - Cloud Tasks for async processing
   - Pub/Sub for event-driven communication

2. **Dify Vector Store (Weaviate) → Vertex AI Vector Search**
   - Native GCP vector similarity search
   - Integrated with Vertex AI embeddings
   - Scalable and managed service

3. **Dify Knowledge Base → Firestore + Cloud Storage**
   - Firestore for metadata and indexing
   - Cloud Storage for document storage
   - Full-text search with Firestore

4. **Dify LLM Integration → Vertex AI**
   - Native access to Google models (Gemini, PaLM)
   - Model Garden for third-party models
   - Unified API for all models

5. **Redis Cache → Memorystore for Redis**
   - Already configured in previous setup

6. **PostgreSQL → Cloud SQL**
   - Already configured in previous setup

7. **File Storage → Cloud Storage**
   - Already configured in previous setup

## API Key Management

All API keys will be stored in Secret Manager:
- `openai-api-key`
- `anthropic-api-key`
- `tavily-api-key`
- `lexis-nexis-api-key`
- `vertex-ai-service-account`

## Architecture Benefits

1. **Fully Managed** - No infrastructure to maintain
2. **Native Integration** - Services work seamlessly together
3. **Security** - IAM and VPC controls
4. **Scalability** - Auto-scaling for all services
5. **Cost Optimization** - Pay only for what you use