import os
import redis
from typing import Optional

class MemorystoreConfig:
    """Configuration for Google Cloud Memorystore (Redis)"""
    
    def __init__(self):
        self.redis_host = os.environ.get('MEMORYSTORE_REDIS_HOST')
        self.redis_port = int(os.environ.get('MEMORYSTORE_REDIS_PORT', '6379'))
        self.redis_password = os.environ.get('MEMORYSTORE_REDIS_PASSWORD', '')
        self.use_ssl = os.environ.get('MEMORYSTORE_USE_SSL', 'true').lower() == 'true'
        self.redis_client = None
        
    def get_redis_client(self, db: int = 0) -> redis.Redis:
        """Get Redis client for specified database"""
        if not self.redis_client:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password if self.redis_password else None,
                db=db,
                ssl=self.use_ssl,
                ssl_cert_reqs='required' if self.use_ssl else None,
                decode_responses=True
            )
        return self.redis_client
    
    def get_celery_broker_url(self) -> str:
        """Get Redis URL for Celery broker"""
        protocol = 'rediss' if self.use_ssl else 'redis'
        auth = f":{self.redis_password}@" if self.redis_password else ''
        return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/1"
    
    def get_cache_url(self) -> str:
        """Get Redis URL for caching"""
        protocol = 'rediss' if self.use_ssl else 'redis'
        auth = f":{self.redis_password}@" if self.redis_password else ''
        return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/0"
    
    def test_connection(self) -> bool:
        """Test Redis connection"""
        try:
            client = self.get_redis_client()
            client.ping()
            return True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            return False
    
    def get_dify_redis_config(self) -> dict:
        """Get Redis configuration for Dify"""
        return {
            'REDIS_HOST': self.redis_host,
            'REDIS_PORT': str(self.redis_port),
            'REDIS_PASSWORD': self.redis_password,
            'REDIS_USE_SSL': 'true' if self.use_ssl else 'false',
            'REDIS_DB': '0',
            'CELERY_BROKER_URL': self.get_celery_broker_url(),
            'BROKER_USE_SSL': 'true' if self.use_ssl else 'false'
        }