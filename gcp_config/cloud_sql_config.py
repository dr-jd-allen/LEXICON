import os
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
import pg8000

class CloudSQLConfig:
    """Configuration for Google Cloud SQL PostgreSQL connection"""
    
    def __init__(self):
        self.project_id = os.environ.get('GCP_PROJECT_ID')
        self.region = os.environ.get('GCP_REGION', 'us-central1')
        self.instance_name = os.environ.get('CLOUD_SQL_INSTANCE_NAME', 'lexicon-db')
        self.database_name = os.environ.get('DATABASE_NAME', 'dify')
        self.user = os.environ.get('DATABASE_USER', 'postgres')
        self.password = os.environ.get('DATABASE_PASSWORD')
        self.use_private_ip = os.environ.get('USE_PRIVATE_IP', 'false').lower() == 'true'
        
    def get_connection_string(self):
        """Get Cloud SQL connection string for production use"""
        if os.environ.get('ENVIRONMENT') == 'production':
            # Use Unix socket connection in Cloud Run
            return f"postgresql+pg8000://{self.user}:{self.password}@/{self.database_name}?unix_sock=/cloudsql/{self.project_id}:{self.region}:{self.instance_name}/.s.PGSQL.5432"
        else:
            # Use Cloud SQL Connector for local development
            return self._get_connector_string()
    
    def _get_connector_string(self):
        """Get connection string using Cloud SQL Python Connector"""
        connector = Connector()
        
        def getconn():
            conn = connector.connect(
                f"{self.project_id}:{self.region}:{self.instance_name}",
                "pg8000",
                user=self.user,
                password=self.password,
                db=self.database_name,
                ip_type=IPTypes.PRIVATE if self.use_private_ip else IPTypes.PUBLIC,
            )
            return conn
        
        pool = sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=getconn,
        )
        return pool
    
    def get_dify_database_url(self):
        """Format database URL for Dify configuration"""
        if os.environ.get('ENVIRONMENT') == 'production':
            # Cloud Run with Unix socket
            host = f"/cloudsql/{self.project_id}:{self.region}:{self.instance_name}"
            return f"postgresql://{self.user}:{self.password}@{host}/{self.database_name}"
        else:
            # Development with Cloud SQL Proxy
            proxy_host = os.environ.get('CLOUD_SQL_PROXY_HOST', '127.0.0.1')
            proxy_port = os.environ.get('CLOUD_SQL_PROXY_PORT', '5432')
            return f"postgresql://{self.user}:{self.password}@{proxy_host}:{proxy_port}/{self.database_name}"