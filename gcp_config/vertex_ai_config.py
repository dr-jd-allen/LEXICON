"""Vertex AI configuration for LEXICON"""

import os
from typing import Dict, Any, Optional
from google.cloud import aiplatform
from google.cloud import secretmanager
import vertexai
from vertexai.language_models import TextGenerationModel, ChatModel
from vertexai.generative_models import GenerativeModel
import google.generativeai as genai

class VertexAIConfig:
    """Configuration for Vertex AI and model integrations"""
    
    def __init__(self):
        self.project_id = os.environ.get('GCP_PROJECT_ID', 'spinwheel-464709')
        self.location = os.environ.get('GCP_REGION', 'us-central1')
        self.secret_client = secretmanager.SecretManagerServiceClient()
        
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)
        
        # Load API keys from Secret Manager
        self.api_keys = self._load_api_keys()
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from Secret Manager"""
        keys = {}
        secret_names = [
            'openai-api-key',
            'anthropic-api-key',
            'tavily-api-key',
            'lexis-nexis-api-key'
        ]
        
        for secret_name in secret_names:
            try:
                name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
                response = self.secret_client.access_secret_version(request={"name": name})
                keys[secret_name] = response.payload.data.decode('UTF-8')
            except Exception as e:
                print(f"Warning: Could not load {secret_name}: {e}")
        
        return keys
    
    def get_model(self, model_type: str) -> Any:
        """Get model instance based on type"""
        model_mapping = {
            # OpenAI Models (Primary - same as Dify workflow)
            'o3-pro-2025-06-10': lambda: self._get_openai_model('o1-pro'),
            'o4-mini': lambda: self._get_openai_model('o1-mini'),
            'gpt-4.1-nano': lambda: self._get_openai_model('gpt-4-turbo'),
            'gpt-4': lambda: self._get_openai_model('gpt-4'),
            'gpt-4-turbo': lambda: self._get_openai_model('gpt-4-turbo'),
            
            # Anthropic Models (Primary - same as Dify workflow)
            'claude-opus-4-20250514': lambda: self._get_anthropic_model('claude-3-opus-20240229'),
            'claude-sonnet': lambda: self._get_anthropic_model('claude-3-sonnet-20240229'),
            'claude-haiku': lambda: self._get_anthropic_model('claude-3-haiku-20240307'),
            
            # Google Models (Secondary - for specific tasks)
            'gemini-2.5-pro': lambda: GenerativeModel('gemini-1.5-pro'),
            'gemini-pro': lambda: GenerativeModel('gemini-pro'),
        }
        
        if model_type in model_mapping:
            return model_mapping[model_type]()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def _get_openai_model(self, model_name: str):
        """Initialize OpenAI model"""
        import openai
        openai.api_key = self.api_keys.get('openai-api-key')
        return openai.ChatCompletion(model=model_name)
    
    def _get_anthropic_model(self, model_name: str):
        """Initialize Anthropic model"""
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_keys.get('anthropic-api-key'))
        return client.messages(model=model_name)
    
    def create_embedding(self, text: str) -> list:
        """Create embeddings using Vertex AI"""
        from vertexai.language_models import TextEmbeddingModel
        
        model = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")
        embeddings = model.get_embeddings([text])
        return embeddings[0].values
    
    def search_similar(self, query_embedding: list, index_endpoint: str, num_neighbors: int = 10):
        """Search similar vectors using Vertex AI Vector Search"""
        from google.cloud import aiplatform_v1
        
        client = aiplatform_v1.MatchServiceClient()
        
        request = aiplatform_v1.FindNeighborsRequest(
            index_endpoint=index_endpoint,
            queries=[
                aiplatform_v1.FindNeighborsRequest.Query(
                    datapoint=aiplatform_v1.IndexDatapoint(
                        feature_vector=query_embedding
                    ),
                    neighbor_count=num_neighbors
                )
            ]
        )
        
        response = client.find_neighbors(request)
        return response.nearest_neighbors[0].neighbors