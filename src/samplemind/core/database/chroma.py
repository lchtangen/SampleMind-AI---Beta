"""ChromaDB client for vector similarity search"""

import logging
import os
from typing import Any, Dict, List, Optional

import chromadb

try:
    from chromadb.config import Settings
except ImportError:
    Settings = None

from samplemind.core.config import Settings as AppSettings

logger = logging.getLogger(__name__)

# Global ChromaDB client
_chroma_client = None
_collection = None
_settings = AppSettings()


def init_chromadb(
    persist_directory: str = "./data/chroma",
    collection_name: str = _settings.chroma_collection
):
    """Initialize ChromaDB client"""
    global _chroma_client, _collection

    try:
        logger.info(f"🔌 Initializing ChromaDB: {collection_name}")

        # Check environment for Chroma host (e.g. from Docker)
        host = os.getenv("CHROMA_HOST", _settings.chroma_host)
        port = int(os.getenv("CHROMA_PORT", _settings.chroma_port))

        # Determine client type
        if host and host != "localhost":
            logger.info(f"Connecting to ChromaDB at {host}:{port}")
            _chroma_client = chromadb.HttpClient(host=host, port=port)
        else:
            logger.info(f"Using local ChromaDB at {persist_directory}")
            # Use PersistentClient for local storage
            _chroma_client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        _collection = _chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Audio sample embeddings for similarity search"}
        )

        logger.info(f"✅ ChromaDB initialized with {_collection.count()} embeddings")
        return _chroma_client

    except Exception as e:
        logger.error(f"❌ Failed to initialize ChromaDB: {e}")
        raise


def get_chroma_client():
    """Get ChromaDB client instance"""
    if _chroma_client is None:
        raise RuntimeError("ChromaDB not initialized. Call init_chromadb() first.")
    return _chroma_client


def get_collection():
    """Get ChromaDB collection"""
    if _collection is None:
        raise RuntimeError("ChromaDB collection not initialized")
    return _collection


async def add_embedding(
    file_id: str,
    embedding: List[float],
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Add audio embedding to ChromaDB"""
    try:
        collection = get_collection()

        collection.add(
            ids=[file_id],
            embeddings=[embedding],
            metadatas=[metadata or {}]
        )

        logger.debug(f"Added embedding for file: {file_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to add embedding: {e}")
        return False


async def query_similar(
    embedding: List[float],
    n_results: int = 10,
    where: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Query similar audio samples"""
    try:
        collection = get_collection()

        results = collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=where
        )

        return {
            "ids": results["ids"][0] if results["ids"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else []
        }

    except Exception as e:
        logger.error(f"Failed to query similar: {e}")
        return {"ids": [], "distances": [], "metadatas": []}


async def delete_embedding(file_id: str) -> bool:
    """Delete audio embedding from ChromaDB"""
    try:
        collection = get_collection()
        collection.delete(ids=[file_id])
        logger.debug(f"Deleted embedding for file: {file_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete embedding: {e}")
        return False


async def get_collection_stats() -> Dict[str, Any]:
    """Get collection statistics"""
    try:
        collection = get_collection()
        return {
            "count": collection.count(),
            "name": collection.name,
            "metadata": collection.metadata
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"count": 0, "name": "unknown", "metadata": {}}
