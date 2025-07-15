"""Modified DocumentProcessor to use Google Cloud Storage"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile

from cloud_storage_config import CloudStorageConfig

# Import original document processing utilities
# Assuming these exist in the original codebase
from document_processor import extract_text_from_pdf, extract_text_from_docx

class DocumentProcessorGCP:
    """Document processor integrated with Google Cloud Storage"""
    
    def __init__(self):
        self.storage = CloudStorageConfig()
        self.storage.initialize_bucket()
        
    def process_document(self, file_path: str, file_name: str) -> Tuple[str, str]:
        """Process a document and store in Cloud Storage"""
        
        # Upload raw document to Cloud Storage
        with open(file_path, 'rb') as f:
            raw_uri = self.storage.upload_document(f, file_name, folder='raw')
        
        # Extract text based on file type
        file_ext = Path(file_name).suffix.lower()
        
        if file_ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            text = extract_text_from_docx(file_path)
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Process and chunk the text
        chunks = self._chunk_text(text)
        
        # Create metadata
        metadata = {
            'file_name': file_name,
            'raw_uri': raw_uri,
            'chunk_count': len(chunks),
            'total_chars': len(text),
            'file_type': file_ext
        }
        
        # Save processed data to Cloud Storage
        processed_data = {
            'metadata': metadata,
            'chunks': chunks,
            'full_text': text
        }
        
        json_name = f"{Path(file_name).stem}_processed.json"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(processed_data, tmp, indent=2)
            tmp.flush()
            
            with open(tmp.name, 'rb') as f:
                processed_uri = self.storage.upload_document(
                    f, json_name, folder='processed'
                )
        
        # Clean up temp file
        os.unlink(tmp.name)
        
        return raw_uri, processed_uri
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[Dict]:
        """Chunk text for vector embedding"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            
            chunks.append({
                'text': chunk_text,
                'start': start,
                'end': min(end, len(text)),
                'chunk_id': len(chunks)
            })
            
            start = end - overlap
            
        return chunks
    
    def retrieve_document(self, uri: str, local_path: Optional[str] = None) -> str:
        """Retrieve a document from Cloud Storage"""
        # Extract blob name from URI
        if uri.startswith('gs://'):
            blob_name = uri.replace(f'gs://{self.storage.bucket_name}/', '')
        else:
            blob_name = uri
            
        return self.storage.download_document(blob_name, local_path)
    
    def list_documents(self, document_type: str = 'raw') -> List[str]:
        """List documents in Cloud Storage"""
        return self.storage.list_documents(prefix=f'{document_type}/')
    
    def get_document_url(self, uri: str, expiration_minutes: int = 60) -> str:
        """Get a signed URL for document access"""
        if uri.startswith('gs://'):
            blob_name = uri.replace(f'gs://{self.storage.bucket_name}/', '')
        else:
            blob_name = uri
            
        return self.storage.get_signed_url(blob_name, expiration_minutes)