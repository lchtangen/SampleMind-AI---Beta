"""
PostgreSQL + pgvector storage for audio features and embeddings.
"""
from datetime import datetime
import json
import logging
import time
from typing import List, Optional, Dict, Any, Union, Tuple, Generator, Callable
from dataclasses import dataclass, asdict, field
import numpy as np
import psycopg2
from psycopg2 import sql, pool
from psycopg2.extras import Json, DictCursor, execute_batch
from psycopg2.sql import Composable, Literal
from psycopg2.extensions import register_adapter, AsIs, new_type, register_type
from psycopg2.extras import register_default_jsonb
from psycopg2.extensions import adapt, register_adapter

# Register numpy float32 type
def adapt_numpy_float32(numpy_float32):
    return AsIs(numpy_float32)

def adapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)

def adapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)

# Register numpy array type
def adapt_numpy_array(numpy_array):
    return adapt(numpy_array.tolist())

# Register adapters
register_adapter(np.float32, adapt_numpy_float32)
register_adapter(np.float64, adapt_numpy_float64)
register_adapter(np.int64, adapt_numpy_int64)
register_adapter(np.ndarray, adapt_numpy_array)

@dataclass
class AudioFeatureRecord:
    """Data class for audio feature records."""
    id: str
    audio_path: str
    file_hash: str
    sample_rate: int
    duration: float
    features: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary."""
        data = asdict(self)
        if isinstance(self.embedding, np.ndarray):
            data['embedding'] = self.embedding.tolist()
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioFeatureRecord':
        """Create record from dictionary."""
        if 'embedding' in data and data['embedding'] is not None:
            data['embedding'] = np.array(data['embedding'])
        return cls(**data)

class PgVectorStore:
    """PostgreSQL + pgvector storage for audio features and embeddings.
    
    Features:
    - Connection pooling for better performance
    - Batch operations
    - Metadata filtering
    - Custom similarity metrics
    - Performance monitoring
    """
    
    def __init__(self, 
                connection_string: Optional[str] = None,
                min_conn: int = 1,
                max_conn: int = 10,
                timeout: int = 30):
        """Initialize the vector store with connection pooling.
        
        Args:
            connection_string: PostgreSQL connection string.
            min_conn: Minimum number of connections in the pool.
            max_conn: Maximum number of connections in the pool.
            timeout: Connection timeout in seconds.
        """
        self.connection_string = connection_string or os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:postgres@localhost:5432/samplemind'
        )
        self.pool = None
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.timeout = timeout
        self.logger = self._setup_logging()
        self._ensure_extension()
        self._setup_connection_pool()
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('pgvector_store')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _setup_connection_pool(self):
        """Initialize the connection pool."""
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=self.min_conn,
                maxconn=self.max_conn,
                dsn=self.connection_string,
                options=f'-c statement_timeout={self.timeout * 1000}'
            )
            # Test the connection
            conn = self.pool.getconn()
            self._create_tables(conn)
            self.pool.putconn(conn)
            self.logger.info("Connection pool initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool."""
        if self.pool is None:
            self._setup_connection_pool()
        return self.pool.getconn()
    
    def return_connection(self, conn):
        """Return a connection to the pool."""
        if self.pool is not None:
            self.pool.putconn(conn)
    
    def close_all_connections(self):
        """Close all connections in the pool."""
        if self.pool is not None:
            self.pool.closeall()
            self.logger.info("All database connections closed")
    
    def with_connection(self, func):
        """Decorator to manage connection lifecycle."""
        def wrapper(*args, **kwargs):
            conn = self.get_connection()
            try:
                result = func(conn, *args, **kwargs)
                return result
            except Exception as e:
                self.logger.error(f"Database error: {e}")
                if conn:
                    conn.rollback()
                raise
            finally:
                if conn:
                    self.return_connection(conn)
        return wrapper
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def _ensure_extension(self):
        """Ensure required extensions are installed."""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            conn.autocommit = True
            with conn.cursor() as cur:
                # Required extensions
                for ext in ['vector', 'pg_trgm', 'btree_gin']:
                    try:
                        cur.execute(f"CREATE EXTENSION IF NOT EXISTS {ext}")
                        self.logger.info(f"Extension {ext} is available")
                    except Exception as e:
                        self.logger.warning(f"Could not enable {ext} extension: {e}")
                        conn.rollback()
        except Exception as e:
            self.logger.error(f"Failed to verify extensions: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def _create_tables(self, conn):
        """Create necessary tables and indexes if they don't exist."""
        with conn.cursor() as cur:
            try:
                # Create audio_features table with partitioning
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS audio_features (
                        id TEXT NOT NULL,
                        audio_path TEXT NOT NULL,
                        file_hash TEXT NOT NULL,
                        sample_rate INTEGER,
                        duration FLOAT,
                        features JSONB,
                        embedding VECTOR(1536),
                        metadata JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (id, created_at)
                    ) PARTITION BY RANGE (created_at);
                    
                    -- Create default partition
                    CREATE TABLE IF NOT EXISTS audio_features_default 
                    PARTITION OF audio_features DEFAULT;
                    
                    -- Create monthly partitions for the next year
                    DO $$
                    DECLARE
                        month_start DATE;
                        month_end DATE;
                        partition_name TEXT;
                    BEGIN
                        FOR i IN 0..12 LOOP
                            month_start := DATE_TRUNC('month', CURRENT_DATE + (i || ' months')::interval);
                            month_end := DATE_TRUNC('month', month_start + '1 month'::interval);
                            partition_name := 'audio_features_' || TO_CHAR(month_start, 'YYYY_MM');
                            
                            IF NOT EXISTS (
                                SELECT 1 
                                FROM pg_tables 
                                WHERE tablename = partition_name
                            ) THEN
                                EXECUTE format(
                                    'CREATE TABLE %I PARTITION OF audio_features ' ||
                                    'FOR VALUES FROM (%L) TO (%L)',
                                    partition_name,
                                    month_start,
                                    month_end
                                );
                            END IF;
                        END LOOP;
                    END $$;
                """)
                
                # Create indexes
                cur.execute("""
                    -- GIN index for JSONB fields
                    CREATE INDEX IF NOT EXISTS idx_audio_features_metadata 
                    ON audio_features USING GIN (metadata);
                    
                    -- Index for file hash with pg_trgm for similarity search
                    CREATE INDEX IF NOT EXISTS idx_audio_features_file_hash_trgm 
                    ON audio_features USING GIN (file_hash gin_trgm_ops);
                    
                    -- Index for audio path with pg_trgm
                    CREATE INDEX IF NOT EXISTS idx_audio_path_trgm 
                    ON audio_features USING GIN (audio_path gin_trgm_ops);
                    
                    -- HNSW index for faster approximate nearest neighbor search
                    CREATE INDEX IF NOT EXISTS idx_audio_features_embedding_hnsw 
                    ON audio_features USING hnsw (embedding vector_l2_ops)
                    WITH (m = 16, ef_construction = 64);
                    
                    -- Index for created_at for time-based queries
                    CREATE INDEX IF NOT EXISTS idx_audio_features_created_at 
                    ON audio_features (created_at);
                """)
                
                # Create function for updating updated_at
                cur.execute("""
                    CREATE OR REPLACE FUNCTION update_updated_at_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = NOW();
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
                    
                    DROP TRIGGER IF EXISTS update_audio_features_updated_at ON audio_features;
                    CREATE TRIGGER update_audio_features_updated_at
                    BEFORE UPDATE ON audio_features
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column();
                """)
                
                conn.commit()
                self.logger.info("Database schema initialized successfully")
                
            except Exception as e:
                self.logger.error(f"Error initializing database schema: {e}")
                conn.rollback()
                raise
    
    def add_audio_features(self, record: AudioFeatureRecord) -> str:
        """Add or update audio features in the database."""
        with self.connect() as conn, conn.cursor() as cur:
            # Convert numpy array to list for JSON serialization
            embedding = record.embedding.tolist() if record.embedding is not None else None
            
            cur.execute("""
                INSERT INTO audio_features 
                    (id, audio_path, file_hash, sample_rate, duration, 
                     features, embedding, metadata, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    audio_path = EXCLUDED.audio_path,
                    file_hash = EXCLUDED.file_hash,
                    sample_rate = EXCLUDED.sample_rate,
                    duration = EXCLUDED.duration,
                    features = EXCLUDED.features,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (
                record.id,
                record.audio_path,
                record.file_hash,
                record.sample_rate,
                record.duration,
                Json(record.features) if record.features else None,
                embedding,
                Json(record.metadata) if record.metadata else None,
                record.created_at or datetime.utcnow(),
                datetime.utcnow()
            ))
            
            result = cur.fetchone()
            conn.commit()
            return result[0] if result else None
    
    def get_audio_features(self, feature_id: str) -> Optional[AudioFeatureRecord]:
        """Retrieve audio features by ID."""
        with self.connect() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT id, audio_path, file_hash, sample_rate, duration, 
                       features, embedding, metadata, created_at, updated_at
                FROM audio_features
                WHERE id = %s
            """, (feature_id,))
            
            row = cur.fetchone()
            if not row:
                return None
                
            return AudioFeatureRecord(
                id=row[0],
                audio_path=row[1],
                file_hash=row[2],
                sample_rate=row[3],
                duration=row[4],
                features=row[5],
                embedding=np.array(row[6]) if row[6] else None,
                metadata=row[7],
                created_at=row[8],
                updated_at=row[9]
            )
    
    def find_similar(self, 
                    embedding: np.ndarray, 
                    limit: int = 10, 
                    threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Find similar audio features using vector similarity search."""
        with self.connect() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT id, audio_path, file_hash, 
                       sample_rate, duration, features, 
                       embedding <-> %s AS distance
                FROM audio_features
                WHERE embedding IS NOT NULL
                ORDER BY embedding <-> %s
                LIMIT %s
            "", (embedding.tolist(), embedding.tolist(), limit))
            
            results = []
            for row in cur.fetchall():
                if row[6] > threshold:  # Skip results above distance threshold
                    continue
                    
                results.append({
                    'id': row[0],
                    'audio_path': row[1],
                    'file_hash': row[2],
                    'sample_rate': row[3],
                    'duration': row[4],
                    'features': row[5],
                    'distance': float(row[6])
                })
            
            return results
    
    def delete_audio_features(self, feature_id: str) -> bool:
        """Delete audio features by ID."""
        with self.connect() as conn, conn.cursor() as cur:
            cur.execute("""
                DELETE FROM audio_features
                WHERE id = %s
                RETURNING id
            "", (feature_id,))
            
            result = cur.fetchone() is not None
            conn.commit()
            return result
    
    def count_audio_features(self) -> int:
        """Count the number of audio feature records."""
        with self.connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM audio_features")
            return cur.fetchone()[0]
