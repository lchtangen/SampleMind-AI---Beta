"""
Advanced operations for PgVectorStore including batch processing, metadata filtering,
and performance monitoring.
"""
from typing import List, Dict, Any, Optional, Tuple, Union, Callable, TypeVar
from datetime import datetime, timedelta
import time
import logging
import numpy as np
from psycopg2 import sql
from psycopg2.extras import execute_batch

from .pgvector_store import AudioFeatureRecord, PgVectorStore

T = TypeVar('T')

class AdvancedVectorOperations(PgVectorStore):
    """Extends PgVectorStore with advanced operations."""
    
    # Batch processing
    BATCH_SIZE = 1000
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('pgvector_store.advanced')
    
    # ===== Batch Operations =====
    
    def batch_add_audio_features(
        self, 
        records: List[AudioFeatureRecord],
        batch_size: Optional[int] = None
    ) -> List[str]:
        """Add multiple audio features in batches.
        
        Args:
            records: List of AudioFeatureRecord objects
            batch_size: Number of records per batch
            
        Returns:
            List of inserted/updated record IDs
        """
        batch_size = batch_size or self.BATCH_SIZE
        inserted_ids = []
        
        @self.with_connection
        def process_batch(conn, batch):
            with conn.cursor() as cur:
                query = sql.SQL("""
                    INSERT INTO audio_features 
                        (id, audio_path, file_hash, sample_rate, duration, 
                         features, embedding, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
                """)
                
                batch_data = [(
                    r.id,
                    r.audio_path,
                    r.file_hash,
                    r.sample_rate,
                    r.duration,
                    r.features,
                    r.embedding.tolist() if r.embedding is not None else None,
                    r.metadata
                ) for r in batch]
                
                cur.executemany(query, batch_data)
                return [row[0] for row in cur.fetchall()]
        
        # Process in batches
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            try:
                batch_ids = process_batch(batch)
                inserted_ids.extend(batch_ids)
                self.logger.info(
                    f"Processed batch {i//batch_size + 1}/"
                    f"{(len(records)-1)//batch_size + 1}"
                )
            except Exception as e:
                self.logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                raise
        
        return inserted_ids
    
    # ===== Metadata Filtering =====
    
    def query_by_metadata(
        self,
        metadata_filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Query audio features by metadata filters.
        
        Args:
            metadata_filters: Dictionary of metadata field filters
            limit: Maximum number of results to return
            offset: Number of results to skip
            
        Returns:
            List of matching audio feature records
        """
        @self.with_connection
        def execute_query(conn):
            with conn.cursor() as cur:
                # Build WHERE clause for metadata filters
                conditions = []
                params = []
                
                for i, (key, value) in enumerate(metadata_filters.items()):
                    if isinstance(value, (list, tuple)):
                        # Handle array containment
                        conditions.append(
                            sql.SQL("metadata->>{} = ANY(%s)").format(
                                sql.Literal(key)
                            )
                        )
                        params.append(value)
                    elif isinstance(value, dict) and 'range' in value:
                        # Handle range queries
                        if 'gt' in value['range']:
                            conditions.append(
                                sql.SQL("(metadata->>%s)::float > %s").format(
                                    sql.Literal(key)
                                )
                            )
                            params.extend([key, value['range']['gt']])
                        if 'lt' in value['range']:
                            conditions.append(
                                sql.SQL("(metadata->>%s)::float < %s").format(
                                    sql.Literal(key)
                                )
                            )
                            params.extend([key, value['range']['lt']])
                    else:
                        # Handle exact match
                        conditions.append(
                            sql.SQL("metadata->>%s = %s")
                        )
                        params.extend([key, value])
                
                # Build query
                query = sql.SQL("""
                    SELECT id, audio_path, file_hash, sample_rate, 
                           duration, features, embedding, metadata,
                           created_at, updated_at
                    FROM audio_features
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """).format(
                    where_clause=sql.SQL(" WHERE ").join(conditions) if conditions else sql.SQL(""),
                )
                
                params.extend([limit, offset])
                cur.execute(query, params)
                
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        
        return execute_query()
    
    # ===== Similarity Search with Filters =====
    
    def find_similar_with_filters(
        self,
        embedding: np.ndarray,
        metadata_filters: Optional[Dict[str, Any]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        limit: int = 10,
        distance_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Find similar audio features with metadata and time filters.
        
        Args:
            embedding: Query embedding vector
            metadata_filters: Metadata filters dictionary
            time_range: Tuple of (start_time, end_time) for filtering
            limit: Maximum number of results
            distance_threshold: Maximum distance threshold (0-1)
            
        Returns:
            List of similar audio features with distances
        """
        @self.with_connection
        def execute_similarity_search(conn):
            with conn.cursor() as cur:
                # Build WHERE clause
                conditions = [sql.SQL("embedding IS NOT NULL")]
                params = []
                
                # Add metadata filters
                if metadata_filters:
                    for key, value in metadata_filters.items():
                        conditions.append(
                            sql.SQL("metadata->>%s = %s")
                        )
                        params.extend([key, value])
                
                # Add time range filter
                if time_range:
                    start_time, end_time = time_range
                    conditions.append(
                        sql.SQL("created_at BETWEEN %s AND %s")
                    )
                    params.extend([start_time, end_time])
                
                # Build query
                where_clause = sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("TRUE")
                
                query = sql.SQL("""
                    SELECT 
                        id, audio_path, file_hash, sample_rate, 
                        duration, features, embedding, metadata,
                        created_at, updated_at,
                        embedding <-> %s AS distance
                    FROM audio_features
                    WHERE {where_clause}
                    ORDER BY embedding <-> %s
                    LIMIT %s
                """).format(where_clause=where_clause)
                
                params = [embedding.tolist()] + params + [embedding.tolist(), limit]
                
                cur.execute(query, params)
                
                columns = [desc[0] for desc in cur.description]
                results = []
                
                for row in cur.fetchall():
                    result = dict(zip(columns, row))
                    if result['distance'] <= distance_threshold:
                        results.append(result)
                
                return results
        
        return execute_similarity_search()
    
    # ===== Performance Monitoring =====
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics and performance metrics."""
        @self.with_connection
        def get_stats(conn):
            with conn.cursor() as cur:
                # Basic table stats
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        COUNT(DISTINCT file_hash) as unique_files,
                        MIN(created_at) as oldest_record,
                        MAX(created_at) as newest_record,
                        AVG(array_length(ARRAY(SELECT jsonb_object_keys(metadata)), 1)) as avg_metadata_fields
                    FROM audio_features
                """)
                
                stats = dict(zip(
                    ['total_records', 'unique_files', 'oldest_record', 
                     'newest_record', 'avg_metadata_fields'],
                    cur.fetchone()
                ))
                
                # Index usage statistics
                cur.execute("""
                    SELECT 
                        indexname,
                        indexdef,
                        idx_scan,
                        idx_tup_read,
                        idx_tup_fetch
                    FROM pg_indexes
                    JOIN pg_stat_all_indexes ON indexname = indexrelname
                    WHERE tablename = 'audio_features'
                """)
                
                stats['indexes'] = [
                    dict(zip(
                        ['name', 'definition', 'scans', 'tuples_read', 'tuples_fetched'],
                        row
                    ))
                    for row in cur.fetchall()
                ]
                
                # Query performance
                cur.execute("""
                    SELECT 
                        query,
                        calls,
                        total_exec_time,
                        mean_exec_time,
                        rows,
                        shared_blks_hit,
                        shared_blks_read
                    FROM pg_stat_statements
                    WHERE query LIKE '%audio_features%'
                    ORDER BY total_exec_time DESC
                    LIMIT 10
                """)
                
                stats['slow_queries'] = [
                    dict(zip(
                        ['query', 'calls', 'total_time_ms', 'avg_time_ms', 
                         'rows', 'cache_hits', 'disk_reads'],
                        row
                    ))
                    for row in cur.fetchall()
                ]
                
                return stats
        
        return get_stats()
    
    def benchmark_query_performance(
        self,
        query_func: Callable[..., T],
        *args,
        num_runs: int = 10,
        warmup_runs: int = 2,
        **kwargs
    ) -> Dict[str, Any]:
        """Benchmark the performance of a query function.
        
        Args:
            query_func: The query function to benchmark
            *args: Positional arguments to pass to the function
            num_runs: Number of benchmark runs
            warmup_runs: Number of warmup runs (not included in results)
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Dictionary with benchmark results
        """
        # Warmup
        for _ in range(warmup_runs):
            query_func(*args, **kwargs)
        
        # Benchmark
        run_times = []
        for _ in range(num_runs):
            start_time = time.perf_counter()
            result = query_func(*args, **kwargs)
            end_time = time.perf_counter()
            run_times.append(end_time - start_time)
        
        # Calculate statistics
        stats = {
            'function': query_func.__name__,
            'num_runs': num_runs,
            'min_time_ms': min(run_times) * 1000,
            'max_time_ms': max(run_times) * 1000,
            'avg_time_ms': sum(run_times) / len(run_times) * 1000,
            'p50_ms': np.percentile(run_times, 50) * 1000,
            'p95_ms': np.percentile(run_times, 95) * 1000,
            'p99_ms': np.percentile(run_times, 99) * 1000,
            'result_size': len(result) if hasattr(result, '__len__') else 1,
            'runs': run_times
        }
        
        return stats
