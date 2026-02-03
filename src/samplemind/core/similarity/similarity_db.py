"""
Similarity Database using ChromaDB

Provides persistent storage and querying of audio embeddings for similarity search.
Supports filtering by metadata (tempo, key, genre) and batch operations.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import chromadb
from chromadb.config import Settings

from .embedding_engine import AudioEmbeddingEngine, AudioEmbedding, EMBEDDING_DIM

logger = logging.getLogger(__name__)

DEFAULT_COLLECTION_NAME = "samplemind_audio_embeddings"
DEFAULT_PERSIST_DIR = "./data/similarity"


@dataclass
class SimilarityResult:
    """Result from a similarity search query"""
    file_id: str
    file_path: str
    similarity: float  # 0.0 to 1.0
    metadata: Dict[str, Any]

    @property
    def percentage(self) -> float:
        """Similarity as percentage"""
        return self.similarity * 100


class SimilarityDatabase:
    """
    ChromaDB-backed similarity search database for audio samples.

    Features:
    - Index audio files with embeddings
    - Find similar samples with optional filters
    - Persistent storage
    - Batch operations for large libraries
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ):
        """
        Initialize the similarity database.

        Args:
            persist_directory: Directory for persistent storage (None for in-memory)
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = persist_directory or DEFAULT_PERSIST_DIR
        self.collection_name = collection_name
        self.embedding_engine = AudioEmbeddingEngine()

        # Initialize ChromaDB
        self._init_chromadb()

    def _init_chromadb(self) -> None:
        """Initialize ChromaDB client and collection"""
        try:
            # Ensure persist directory exists
            persist_path = Path(self.persist_directory)
            persist_path.mkdir(parents=True, exist_ok=True)

            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=str(persist_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "SampleMind audio sample embeddings",
                    "embedding_dim": EMBEDDING_DIM,
                }
            )

            logger.info(
                f"Initialized similarity database: {self.collection_name} "
                f"({self.collection.count()} embeddings)"
            )

        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def index_file(
        self,
        file_path: Path,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Index a single audio file.

        Args:
            file_path: Path to audio file
            additional_metadata: Extra metadata to store (e.g., tags, genre)

        Returns:
            File ID of the indexed file
        """
        file_path = Path(file_path).expanduser().resolve()

        # Generate embedding
        embedding = self.embedding_engine.generate_embedding(file_path)

        # Merge metadata
        metadata = embedding.metadata.copy()
        if additional_metadata:
            metadata.update(additional_metadata)

        # Ensure all metadata values are valid types for ChromaDB
        clean_metadata = self._clean_metadata(metadata)

        # Check if already indexed
        existing = self.collection.get(ids=[embedding.file_id])
        if existing['ids']:
            # Update existing
            self.collection.update(
                ids=[embedding.file_id],
                embeddings=[embedding.to_list()],
                metadatas=[clean_metadata],
            )
            logger.info(f"Updated index for: {file_path.name}")
        else:
            # Add new
            self.collection.add(
                ids=[embedding.file_id],
                embeddings=[embedding.to_list()],
                metadatas=[clean_metadata],
            )
            logger.info(f"Indexed: {file_path.name}")

        return embedding.file_id

    def index_library(
        self,
        folder: Path,
        extensions: List[str] = None,
        recursive: bool = True,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> int:
        """
        Index all audio files in a folder.

        Args:
            folder: Directory to scan
            extensions: File extensions to include (default: common audio formats)
            recursive: Include subdirectories
            progress_callback: Optional callback(current, total, filename)

        Returns:
            Number of files indexed
        """
        folder = Path(folder).expanduser().resolve()
        if not folder.is_dir():
            raise NotADirectoryError(f"Not a directory: {folder}")

        extensions = extensions or ['.wav', '.mp3', '.flac', '.aiff', '.m4a', '.ogg']

        # Find all audio files
        if recursive:
            files = [f for f in folder.rglob('*') if f.suffix.lower() in extensions]
        else:
            files = [f for f in folder.iterdir() if f.suffix.lower() in extensions]

        if not files:
            logger.warning(f"No audio files found in {folder}")
            return 0

        logger.info(f"Indexing {len(files)} files from {folder}")

        indexed = 0
        for i, file_path in enumerate(files):
            if progress_callback:
                progress_callback(i + 1, len(files), file_path.name)

            try:
                self.index_file(file_path)
                indexed += 1
            except Exception as e:
                logger.warning(f"Failed to index {file_path}: {e}")

        logger.info(f"Successfully indexed {indexed}/{len(files)} files")
        return indexed

    def find_similar(
        self,
        query_file: Path,
        n_results: int = 10,
        min_similarity: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SimilarityResult]:
        """
        Find similar samples to a query file.

        Args:
            query_file: Path to query audio file
            n_results: Maximum number of results
            min_similarity: Minimum similarity threshold (0.0-1.0)
            filters: Metadata filters (e.g., {"tempo": {"$gte": 100, "$lte": 130}})

        Returns:
            List of SimilarityResult objects
        """
        query_file = Path(query_file).expanduser().resolve()

        # Generate embedding for query
        query_embedding = self.embedding_engine.generate_embedding(query_file)

        # Build ChromaDB where clause
        where_clause = self._build_where_clause(filters) if filters else None

        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding.to_list()],
            n_results=n_results,
            where=where_clause,
            include=["embeddings", "metadatas", "distances"],
        )

        # Convert to SimilarityResult objects
        similar_files = []
        if results['ids'] and results['ids'][0]:
            for i, file_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i] if results['distances'] else 0
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}

                # Convert distance to similarity (ChromaDB uses L2 distance by default)
                # For normalized vectors, L2 distance ranges from 0 to 2
                # Similarity = 1 - (distance / 2)
                similarity = max(0.0, min(1.0, 1.0 - (distance / 2)))

                if similarity >= min_similarity:
                    similar_files.append(SimilarityResult(
                        file_id=file_id,
                        file_path=metadata.get('file_path', 'Unknown'),
                        similarity=similarity,
                        metadata=metadata,
                    ))

        # Sort by similarity descending
        similar_files.sort(key=lambda x: x.similarity, reverse=True)

        return similar_files

    def find_similar_by_id(
        self,
        file_id: str,
        n_results: int = 10,
        min_similarity: float = 0.0,
    ) -> List[SimilarityResult]:
        """
        Find similar samples to an already-indexed file.

        Args:
            file_id: ID of the indexed file
            n_results: Maximum number of results
            min_similarity: Minimum similarity threshold

        Returns:
            List of SimilarityResult objects
        """
        # Get the embedding for the file
        result = self.collection.get(
            ids=[file_id],
            include=["embeddings"],
        )

        if not result['embeddings']:
            raise ValueError(f"File ID not found: {file_id}")

        # Query for similar
        results = self.collection.query(
            query_embeddings=[result['embeddings'][0]],
            n_results=n_results + 1,  # +1 to exclude the query itself
            include=["metadatas", "distances"],
        )

        similar_files = []
        if results['ids'] and results['ids'][0]:
            for i, fid in enumerate(results['ids'][0]):
                if fid == file_id:  # Skip the query file itself
                    continue

                distance = results['distances'][0][i] if results['distances'] else 0
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}

                similarity = max(0.0, min(1.0, 1.0 - (distance / 2)))

                if similarity >= min_similarity:
                    similar_files.append(SimilarityResult(
                        file_id=fid,
                        file_path=metadata.get('file_path', 'Unknown'),
                        similarity=similarity,
                        metadata=metadata,
                    ))

        return similar_files[:n_results]

    def compare_files(
        self,
        file1: Path,
        file2: Path,
    ) -> float:
        """
        Compare similarity between two audio files.

        Args:
            file1: First audio file
            file2: Second audio file

        Returns:
            Similarity score (0.0-1.0)
        """
        emb1 = self.embedding_engine.generate_embedding(file1)
        emb2 = self.embedding_engine.generate_embedding(file2)

        return self.embedding_engine.compute_similarity(emb1.embedding, emb2.embedding)

    def remove_file(self, file_id: str) -> bool:
        """
        Remove a file from the index.

        Args:
            file_id: ID of the file to remove

        Returns:
            True if removed, False if not found
        """
        try:
            self.collection.delete(ids=[file_id])
            logger.info(f"Removed file from index: {file_id}")
            return True
        except Exception as e:
            logger.warning(f"Failed to remove file {file_id}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            "collection_name": self.collection_name,
            "total_files": self.collection.count(),
            "persist_directory": self.persist_directory,
            "embedding_dim": EMBEDDING_DIM,
        }

    def clear(self) -> None:
        """Clear all data from the database"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "SampleMind audio sample embeddings"},
        )
        logger.info("Cleared similarity database")

    @staticmethod
    def _clean_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata for ChromaDB (only str, int, float, bool allowed)"""
        clean = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                clean[key] = value
            elif isinstance(value, Path):
                clean[key] = str(value)
            elif value is None:
                clean[key] = ""
            else:
                clean[key] = str(value)
        return clean

    @staticmethod
    def _build_where_clause(filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build ChromaDB where clause from filters"""
        if not filters:
            return None

        # Simple filters: {"key": "value"} or {"tempo": {"$gte": 100}}
        where_parts = []
        for key, value in filters.items():
            if isinstance(value, dict):
                # Range filter like {"$gte": 100, "$lte": 130}
                for op, val in value.items():
                    where_parts.append({key: {op: val}})
            else:
                # Exact match
                where_parts.append({key: value})

        if len(where_parts) == 1:
            return where_parts[0]
        elif len(where_parts) > 1:
            return {"$and": where_parts}
        return None
