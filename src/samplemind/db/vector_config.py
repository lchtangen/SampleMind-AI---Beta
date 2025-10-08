"""ChromaDB vector search optimization configuration"""

import chromadb
from chromadb.config import Settings
from pathlib import Path


def get_optimized_chroma_settings(persist_dir: str = "/app/data/chromadb") -> Settings:
    """
    Get ChromaDB settings optimized for audio embeddings.
    
    HNSW Parameters:
    - M=32: Good balance (16-64 typical, higher = more memory, better recall)
    - ef_construction=200: Build quality (100-400 typical)
    - ef_search=64: Query quality (10-500 typical, higher = slower, better recall)
    
    Args:
        persist_dir: Directory for persistent storage
        
    Returns:
        Optimized ChromaDB Settings
    """
    return Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=persist_dir,
        anonymized_telemetry=False,
        # HNSW Index Parameters
        hnsw_space="cosine",
        hnsw_construction_ef=200,
        hnsw_search_ef=64,
        hnsw_M=32,
        # Performance
        allow_reset=True,
        chroma_api_impl="rest",
    )


def create_optimized_chroma_client(persist_dir: str = "/app/data/chromadb") -> chromadb.Client:
    """
    Create ChromaDB client with optimized settings.
    
    Args:
        persist_dir: Directory for persistent storage
        
    Returns:
        Configured ChromaDB client
    """
    settings = get_optimized_chroma_settings(persist_dir)
    return chromadb.Client(settings)


def tune_hnsw_for_speed() -> Settings:
    """Fast search, lower recall (good for initial filtering)"""
    settings = get_optimized_chroma_settings()
    settings.hnsw_search_ef = 32  # Lower for speed
    settings.hnsw_M = 16
    return settings


def tune_hnsw_for_accuracy() -> Settings:
    """Slower search, high recall (good for final results)"""
    settings = get_optimized_chroma_settings()
    settings.hnsw_search_ef = 128  # Higher for accuracy
    settings.hnsw_M = 48
    settings.hnsw_construction_ef = 400
    return settings
