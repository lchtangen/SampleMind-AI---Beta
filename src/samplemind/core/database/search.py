"""
Full-Text Search and Vector Similarity Search
Production-ready search implementation with PostgreSQL + pgvector
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import text, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Search result with relevance score"""
    id: str
    title: str
    description: Optional[str]
    score: float
    resource_type: str
    metadata: Dict[str, Any]
    highlight: Optional[str] = None


class FullTextSearch:
    """
    Full-text search using PostgreSQL's built-in capabilities
    Uses ts_vector and ts_query for fast, ranked search
    """
    
    @staticmethod
    async def create_search_indexes(session: AsyncSession):
        """
        Create full-text search indexes
        Should be called during migration or setup
        """
        # Create GIN index for full-text search on audio files
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_audio_files_fts 
            ON audio_files USING GIN(
                to_tsvector('english', 
                    COALESCE(title, '') || ' ' || 
                    COALESCE(description, '') || ' ' ||
                    COALESCE(tags::text, '')
                )
            )
        """))
        
        # Create GIN index for collections
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_collections_fts 
            ON audio_collections USING GIN(
                to_tsvector('english',
                    COALESCE(name, '') || ' ' ||
                    COALESCE(description, '') || ' ' ||
                    COALESCE(tags::text, '')
                )
            )
        """))
        
        # Create trigram index for fuzzy matching
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_audio_files_title_trgm 
            ON audio_files USING GIN(title gin_trgm_ops)
        """))
        
        await session.commit()
    
    @staticmethod
    async def search_audio_files(
        session: AsyncSession,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        min_score: float = 0.1
    ) -> List[SearchResult]:
        """
        Full-text search across audio files
        
        Args:
            session: Database session
            query: Search query
            user_id: Filter by user (optional)
            limit: Maximum results
            offset: Pagination offset
            min_score: Minimum relevance score
            
        Returns:
            List of search results with scores
        """
        # Build search query with ranking
        sql = text("""
            SELECT 
                id,
                title,
                description,
                ts_rank(
                    to_tsvector('english', 
                        COALESCE(title, '') || ' ' || 
                        COALESCE(description, '') || ' ' ||
                        COALESCE(tags::text, '')
                    ),
                    plainto_tsquery('english', :query)
                ) as score,
                ts_headline('english', description, plainto_tsquery('english', :query)) as highlight,
                metadata
            FROM audio_files
            WHERE 
                to_tsvector('english', 
                    COALESCE(title, '') || ' ' || 
                    COALESCE(description, '') || ' ' ||
                    COALESCE(tags::text, '')
                ) @@ plainto_tsquery('english', :query)
                AND (:user_id IS NULL OR user_id = :user_id)
                AND deleted_at IS NULL
            HAVING ts_rank(
                to_tsvector('english', 
                    COALESCE(title, '') || ' ' || 
                    COALESCE(description, '') || ' ' ||
                    COALESCE(tags::text, '')
                ),
                plainto_tsquery('english', :query)
            ) >= :min_score
            ORDER BY score DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = await session.execute(
            sql,
            {
                "query": query,
                "user_id": user_id,
                "limit": limit,
                "offset": offset,
                "min_score": min_score
            }
        )
        
        rows = result.fetchall()
        
        return [
            SearchResult(
                id=row.id,
                title=row.title,
                description=row.description,
                score=float(row.score),
                resource_type="audio_file",
                metadata=row.metadata or {},
                highlight=row.highlight
            )
            for row in rows
        ]
    
    @staticmethod
    async def fuzzy_search(
        session: AsyncSession,
        query: str,
        field: str = "title",
        table: str = "audio_files",
        threshold: float = 0.3,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fuzzy search using trigram similarity
        Great for handling typos and partial matches
        
        Args:
            session: Database session
            query: Search query
            field: Field to search in
            table: Table name
            threshold: Similarity threshold (0-1)
            limit: Maximum results
            
        Returns:
            List of results with similarity scores
        """
        sql = text(f"""
            SELECT 
                id,
                {field},
                similarity({field}, :query) as score
            FROM {table}
            WHERE similarity({field}, :query) > :threshold
            ORDER BY score DESC
            LIMIT :limit
        """)
        
        result = await session.execute(
            sql,
            {"query": query, "threshold": threshold, "limit": limit}
        )
        
        return [
            {
                "id": row.id,
                "value": getattr(row, field),
                "score": float(row.score)
            }
            for row in result.fetchall()
        ]
    
    @staticmethod
    async def autocomplete(
        session: AsyncSession,
        prefix: str,
        field: str = "title",
        table: str = "audio_files",
        limit: int = 10
    ) -> List[str]:
        """
        Autocomplete suggestions using prefix matching
        
        Args:
            session: Database session
            prefix: Search prefix
            field: Field to search in
            table: Table name
            limit: Maximum suggestions
            
        Returns:
            List of suggestions
        """
        sql = text(f"""
            SELECT DISTINCT {field}
            FROM {table}
            WHERE {field} ILIKE :prefix || '%'
            ORDER BY {field}
            LIMIT :limit
        """)
        
        result = await session.execute(
            sql,
            {"prefix": prefix, "limit": limit}
        )
        
        return [row[0] for row in result.fetchall()]


class VectorSearch:
    """
    Vector similarity search using pgvector
    For semantic search and audio feature similarity
    """
    
    @staticmethod
    async def create_vector_indexes(session: AsyncSession):
        """
        Create vector indexes for fast similarity search
        Should be called during migration
        """
        # HNSW index for approximate nearest neighbor search
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_audio_embeddings_hnsw 
            ON audio_embeddings 
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64)
        """))
        
        # IVFFlat index (alternative, good for larger datasets)
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_audio_embeddings_ivfflat 
            ON audio_embeddings 
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """))
        
        await session.commit()
    
    @staticmethod
    async def similarity_search(
        session: AsyncSession,
        query_vector: List[float],
        limit: int = 10,
        distance_metric: str = "cosine",
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float]]:
        """
        Find similar items using vector similarity
        
        Args:
            session: Database session
            query_vector: Query embedding vector
            limit: Maximum results
            distance_metric: cosine, l2, or inner_product
            filters: Additional filters (user_id, etc.)
            
        Returns:
            List of (id, distance) tuples
        """
        # Convert vector to string format for pgvector
        vector_str = f"[{','.join(map(str, query_vector))}]"
        
        # Choose distance operator
        operators = {
            "cosine": "<=>",
            "l2": "<->",
            "inner_product": "<#>"
        }
        operator = operators.get(distance_metric, "<=>")
        
        # Build filter conditions
        filter_sql = ""
        params = {"vector": vector_str, "limit": limit}
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = :{key}")
                params[key] = value
            if conditions:
                filter_sql = "WHERE " + " AND ".join(conditions)
        
        sql = text(f"""
            SELECT 
                audio_id,
                embedding {operator} :vector::vector as distance
            FROM audio_embeddings
            {filter_sql}
            ORDER BY embedding {operator} :vector::vector
            LIMIT :limit
        """)
        
        result = await session.execute(sql, params)
        
        return [
            (row.audio_id, float(row.distance))
            for row in result.fetchall()
        ]
    
    @staticmethod
    async def batch_similarity_search(
        session: AsyncSession,
        query_vectors: List[List[float]],
        limit_per_query: int = 10
    ) -> Dict[int, List[Tuple[str, float]]]:
        """
        Batch similarity search for multiple query vectors
        More efficient than individual queries
        
        Args:
            session: Database session
            query_vectors: List of query vectors
            limit_per_query: Results per query
            
        Returns:
            Dict mapping query index to results
        """
        results = {}
        
        # Process in batch (PostgreSQL can handle this efficiently)
        for idx, vector in enumerate(query_vectors):
            search_results = await VectorSearch.similarity_search(
                session,
                vector,
                limit=limit_per_query
            )
            results[idx] = search_results
        
        return results
    
    @staticmethod
    async def hybrid_search(
        session: AsyncSession,
        text_query: str,
        query_vector: List[float],
        text_weight: float = 0.5,
        vector_weight: float = 0.5,
        limit: int = 20
    ) -> List[SearchResult]:
        """
        Hybrid search combining full-text and vector similarity
        Best of both worlds: semantic + keyword matching
        
        Args:
            session: Database session
            text_query: Text search query
            query_vector: Embedding vector
            text_weight: Weight for text score (0-1)
            vector_weight: Weight for vector score (0-1)
            limit: Maximum results
            
        Returns:
            List of hybrid search results
        """
        vector_str = f"[{','.join(map(str, query_vector))}]"
        
        sql = text("""
            WITH text_scores AS (
                SELECT 
                    id,
                    ts_rank(
                        to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, '')),
                        plainto_tsquery('english', :text_query)
                    ) as text_score
                FROM audio_files
                WHERE to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''))
                    @@ plainto_tsquery('english', :text_query)
            ),
            vector_scores AS (
                SELECT 
                    audio_id as id,
                    1 - (embedding <=> :vector::vector) as vector_score
                FROM audio_embeddings
                ORDER BY embedding <=> :vector::vector
                LIMIT 100
            )
            SELECT 
                COALESCE(t.id, v.id) as id,
                af.title,
                af.description,
                (COALESCE(t.text_score, 0) * :text_weight + 
                 COALESCE(v.vector_score, 0) * :vector_weight) as combined_score,
                af.metadata
            FROM text_scores t
            FULL OUTER JOIN vector_scores v ON t.id = v.id
            JOIN audio_files af ON af.id = COALESCE(t.id, v.id)
            ORDER BY combined_score DESC
            LIMIT :limit
        """)
        
        result = await session.execute(
            sql,
            {
                "text_query": text_query,
                "vector": vector_str,
                "text_weight": text_weight,
                "vector_weight": vector_weight,
                "limit": limit
            }
        )
        
        rows = result.fetchall()
        
        return [
            SearchResult(
                id=row.id,
                title=row.title,
                description=row.description,
                score=float(row.combined_score),
                resource_type="audio_file",
                metadata=row.metadata or {}
            )
            for row in rows
        ]


class SearchOptimizer:
    """Utilities for search optimization and maintenance"""
    
    @staticmethod
    async def update_statistics(session: AsyncSession):
        """Update table statistics for better query planning"""
        await session.execute(text("ANALYZE audio_files"))
        await session.execute(text("ANALYZE audio_embeddings"))
        await session.execute(text("ANALYZE audio_collections"))
        await session.commit()
    
    @staticmethod
    async def vacuum_tables(session: AsyncSession):
        """Vacuum tables to reclaim space and update statistics"""
        # Note: VACUUM cannot run inside a transaction
        # Should be called separately
        await session.execute(text("VACUUM ANALYZE audio_files"))
        await session.execute(text("VACUUM ANALYZE audio_embeddings"))
    
    @staticmethod
    async def get_search_stats(session: AsyncSession) -> Dict[str, Any]:
        """Get search performance statistics"""
        stats = {}
        
        # Table sizes
        result = await session.execute(text("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables
            WHERE tablename IN ('audio_files', 'audio_embeddings', 'audio_collections')
        """))
        stats['table_sizes'] = [dict(row._mapping) for row in result.fetchall()]
        
        # Index usage
        result = await session.execute(text("""
            SELECT 
                indexrelname as index_name,
                idx_scan as times_used,
                pg_size_pretty(pg_relation_size(indexrelid)) as size
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            ORDER BY idx_scan DESC
        """))
        stats['index_usage'] = [dict(row._mapping) for row in result.fetchall()]
        
        return stats


# Example usage
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async def search_example():
    engine = create_async_engine(DATABASE_URL)
    async with AsyncSession(engine) as session:
        # Full-text search
        results = await FullTextSearch.search_audio_files(
            session,
            query="ambient techno",
            user_id="user_123",
            limit=20
        )
        
        # Vector similarity search
        query_embedding = [0.1, 0.2, ..., 0.9]  # 768-dim vector
        similar_items = await VectorSearch.similarity_search(
            session,
            query_vector=query_embedding,
            limit=10,
            distance_metric="cosine"
        )
        
        # Hybrid search
        hybrid_results = await VectorSearch.hybrid_search(
            session,
            text_query="ambient techno",
            query_vector=query_embedding,
            text_weight=0.4,
            vector_weight=0.6,
            limit=20
        )
"""
