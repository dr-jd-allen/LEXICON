"""Firestore-based vector store for LEXICON"""

import os
from typing import List, Dict, Any, Optional
from google.cloud import firestore
from google.cloud import storage
import numpy as np
from datetime import datetime
import hashlib

class FirestoreVectorStore:
    """Vector store implementation using Firestore and Vertex AI"""
    
    def __init__(self):
        self.project_id = os.environ.get('GCP_PROJECT_ID', 'spinwheel-464709')
        self.db = firestore.Client(project=self.project_id)
        self.storage_client = storage.Client(project=self.project_id)
        
        # Collections
        self.documents_collection = 'legal_documents'
        self.embeddings_collection = 'document_embeddings'
        self.precedents_collection = 'legal_precedents'
        self.expert_testimony_collection = 'expert_testimony'
        
        # Initialize Vertex AI for embeddings
        from .vertex_ai_config import VertexAIConfig
        self.vertex_config = VertexAIConfig()
    
    def add_document(self, document: Dict[str, Any], document_type: str) -> str:
        """Add a document to the vector store"""
        # Generate document ID
        doc_id = self._generate_doc_id(document.get('content', ''))
        
        # Create embeddings for the document
        embeddings = self.vertex_config.create_embedding(document['content'])
        
        # Store document metadata
        doc_ref = self.db.collection(self.documents_collection).document(doc_id)
        doc_data = {
            'id': doc_id,
            'type': document_type,
            'title': document.get('title', ''),
            'content': document['content'],
            'metadata': document.get('metadata', {}),
            'created_at': datetime.utcnow(),
            'embedding_id': doc_id
        }
        doc_ref.set(doc_data)
        
        # Store embeddings separately for efficient vector search
        embedding_ref = self.db.collection(self.embeddings_collection).document(doc_id)
        embedding_data = {
            'document_id': doc_id,
            'embedding': embeddings,
            'document_type': document_type,
            'created_at': datetime.utcnow()
        }
        embedding_ref.set(embedding_data)
        
        # Store in specialized collections based on type
        if document_type == 'precedent':
            self._store_precedent(doc_id, document)
        elif document_type == 'expert_testimony':
            self._store_expert_testimony(doc_id, document)
        
        return doc_id
    
    def search_similar(self, query: str, document_type: Optional[str] = None, 
                      top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity"""
        # Create query embedding
        query_embedding = self.vertex_config.create_embedding(query)
        
        # Get all embeddings (in production, use Vertex AI Vector Search)
        embeddings_query = self.db.collection(self.embeddings_collection)
        
        if document_type:
            embeddings_query = embeddings_query.where('document_type', '==', document_type)
        
        embeddings = embeddings_query.stream()
        
        # Calculate similarities
        similarities = []
        for embedding_doc in embeddings:
            doc_data = embedding_doc.to_dict()
            similarity = self._cosine_similarity(query_embedding, doc_data['embedding'])
            similarities.append({
                'document_id': doc_data['document_id'],
                'similarity': similarity
            })
        
        # Sort by similarity and get top_k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        top_results = similarities[:top_k]
        
        # Fetch full documents
        results = []
        for result in top_results:
            doc_ref = self.db.collection(self.documents_collection).document(result['document_id'])
            doc = doc_ref.get()
            if doc.exists:
                doc_data = doc.to_dict()
                doc_data['similarity_score'] = result['similarity']
                results.append(doc_data)
        
        return results
    
    def search_precedents(self, jurisdiction: str, keywords: List[str], 
                         limit: int = 20) -> List[Dict[str, Any]]:
        """Search legal precedents by jurisdiction and keywords"""
        query = self.db.collection(self.precedents_collection)
        
        # Filter by jurisdiction
        query = query.where('jurisdiction', '==', jurisdiction)
        
        # Get all matching documents
        precedents = query.stream()
        
        # Score based on keyword matches
        scored_precedents = []
        for precedent in precedents:
            doc_data = precedent.to_dict()
            score = self._calculate_keyword_score(doc_data, keywords)
            if score > 0:
                doc_data['relevance_score'] = score
                scored_precedents.append(doc_data)
        
        # Sort by score and return top results
        scored_precedents.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_precedents[:limit]
    
    def find_contradictions(self, expert_id: str) -> List[Dict[str, Any]]:
        """Find potential contradictions in expert testimony"""
        # Get all testimony from this expert
        expert_docs = self.db.collection(self.expert_testimony_collection)\
            .where('expert_id', '==', expert_id)\
            .stream()
        
        testimonies = [doc.to_dict() for doc in expert_docs]
        
        # Compare testimonies for contradictions
        contradictions = []
        for i, testimony1 in enumerate(testimonies):
            for testimony2 in testimonies[i+1:]:
                # Create embeddings and check similarity
                emb1 = self.vertex_config.create_embedding(testimony1['content'])
                emb2 = self.vertex_config.create_embedding(testimony2['content'])
                
                similarity = self._cosine_similarity(emb1, emb2)
                
                # Low similarity might indicate contradiction
                if similarity < 0.7:  # Threshold for potential contradiction
                    contradictions.append({
                        'testimony1': testimony1,
                        'testimony2': testimony2,
                        'similarity_score': similarity,
                        'potential_contradiction': True
                    })
        
        return contradictions
    
    def _store_precedent(self, doc_id: str, document: Dict[str, Any]):
        """Store legal precedent with additional metadata"""
        precedent_ref = self.db.collection(self.precedents_collection).document(doc_id)
        precedent_data = {
            'document_id': doc_id,
            'case_name': document.get('case_name', ''),
            'citation': document.get('citation', ''),
            'jurisdiction': document.get('jurisdiction', ''),
            'court': document.get('court', ''),
            'date': document.get('date', ''),
            'holding': document.get('holding', ''),
            'keywords': document.get('keywords', []),
            'created_at': datetime.utcnow()
        }
        precedent_ref.set(precedent_data)
    
    def _store_expert_testimony(self, doc_id: str, document: Dict[str, Any]):
        """Store expert testimony with additional metadata"""
        testimony_ref = self.db.collection(self.expert_testimony_collection).document(doc_id)
        testimony_data = {
            'document_id': doc_id,
            'expert_id': document.get('expert_id', ''),
            'expert_name': document.get('expert_name', ''),
            'case_reference': document.get('case_reference', ''),
            'date': document.get('date', ''),
            'testimony_type': document.get('testimony_type', ''),
            'key_opinions': document.get('key_opinions', []),
            'created_at': datetime.utcnow()
        }
        testimony_ref.set(testimony_data)
    
    def _generate_doc_id(self, content: str) -> str:
        """Generate unique document ID"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def _calculate_keyword_score(self, document: Dict[str, Any], keywords: List[str]) -> int:
        """Calculate keyword relevance score"""
        score = 0
        content = document.get('content', '').lower()
        doc_keywords = [kw.lower() for kw in document.get('keywords', [])]
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Check in content
            score += content.count(keyword_lower) * 1
            # Check in keywords (higher weight)
            if keyword_lower in doc_keywords:
                score += 5
        
        return score