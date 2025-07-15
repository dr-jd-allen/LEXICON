#!/usr/bin/env python3
"""Initialize Cloud SQL database for LEXICON/Dify"""

import os
import sys
from sqlalchemy import create_engine, text
from cloud_sql_config import CloudSQLConfig

def init_database():
    """Initialize Cloud SQL database with required extensions and settings"""
    config = CloudSQLConfig()
    
    try:
        # Connect to the database
        if hasattr(config.get_connection_string(), 'connect'):
            # Using Cloud SQL Connector (returns engine)
            engine = config.get_connection_string()
        else:
            # Using connection string
            engine = create_engine(config.get_connection_string())
        
        with engine.connect() as conn:
            # Enable required PostgreSQL extensions
            extensions = [
                'vector',  # For vector similarity search
                'uuid-ossp',  # For UUID generation
                'pg_trgm',  # For text search
                'btree_gin'  # For indexing
            ]
            
            for ext in extensions:
                try:
                    conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS \"{ext}\""))
                    conn.commit()
                    print(f"✓ Extension {ext} enabled")
                except Exception as e:
                    print(f"⚠ Extension {ext} failed: {e}")
            
            # Create schemas if needed
            schemas = ['public', 'dify']
            for schema in schemas:
                try:
                    conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                    conn.commit()
                    print(f"✓ Schema {schema} created")
                except Exception as e:
                    print(f"⚠ Schema {schema} failed: {e}")
            
            # Set search path
            conn.execute(text("ALTER DATABASE {} SET search_path TO public, dify".format(
                config.database_name
            )))
            conn.commit()
            
            print("\n✓ Database initialization complete!")
            
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Initializing Cloud SQL database...")
    init_database()