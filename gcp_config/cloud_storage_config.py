import os
from google.cloud import storage
from typing import Optional, BinaryIO
import tempfile
from pathlib import Path

class CloudStorageConfig:
    """Configuration for Google Cloud Storage"""
    
    def __init__(self):
        self.project_id = os.environ.get('GCP_PROJECT_ID')
        self.bucket_name = os.environ.get('GCS_BUCKET_NAME', 'lexicon-documents')
        self.storage_client = storage.Client(project=self.project_id)
        self.bucket = None
        
    def initialize_bucket(self):
        """Initialize or create the storage bucket"""
        try:
            self.bucket = self.storage_client.bucket(self.bucket_name)
            if not self.bucket.exists():
                self.bucket = self.storage_client.create_bucket(
                    self.bucket_name,
                    location='us-central1'
                )
                # Set bucket-level uniform access control
                self.bucket.iam_configuration.uniform_bucket_level_access_enabled = True
                self.bucket.patch()
        except Exception as e:
            print(f"Error initializing bucket: {e}")
            raise
    
    def upload_document(self, file_content: BinaryIO, file_name: str, folder: str = 'raw') -> str:
        """Upload a document to Cloud Storage"""
        if not self.bucket:
            self.initialize_bucket()
            
        blob_name = f"{folder}/{file_name}"
        blob = self.bucket.blob(blob_name)
        
        # Upload with content type detection
        content_type = self._get_content_type(file_name)
        blob.upload_from_file(file_content, content_type=content_type)
        
        # Return the GCS URI
        return f"gs://{self.bucket_name}/{blob_name}"
    
    def download_document(self, blob_name: str, destination_path: Optional[str] = None) -> str:
        """Download a document from Cloud Storage"""
        if not self.bucket:
            self.initialize_bucket()
            
        blob = self.bucket.blob(blob_name)
        
        if destination_path is None:
            # Create a temporary file
            suffix = Path(blob_name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                destination_path = tmp_file.name
        
        blob.download_to_filename(destination_path)
        return destination_path
    
    def list_documents(self, prefix: str = '') -> list:
        """List documents in the bucket"""
        if not self.bucket:
            self.initialize_bucket()
            
        blobs = self.bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]
    
    def delete_document(self, blob_name: str):
        """Delete a document from Cloud Storage"""
        if not self.bucket:
            self.initialize_bucket()
            
        blob = self.bucket.blob(blob_name)
        blob.delete()
    
    def get_signed_url(self, blob_name: str, expiration_minutes: int = 60) -> str:
        """Generate a signed URL for temporary access"""
        if not self.bucket:
            self.initialize_bucket()
            
        blob = self.bucket.blob(blob_name)
        url = blob.generate_signed_url(
            expiration=timedelta(minutes=expiration_minutes),
            method='GET'
        )
        return url
    
    @staticmethod
    def _get_content_type(file_name: str) -> str:
        """Determine content type based on file extension"""
        ext = Path(file_name).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.json': 'application/json',
        }
        return content_types.get(ext, 'application/octet-stream')