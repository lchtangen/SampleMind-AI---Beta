"""
Audio Embedding Service

Creates and manages embeddings for audio features
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from samplemind.db.vector_store import get_vector_store, VectorStore
from samplemind.core.engine.audio_engine import AudioEngine

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for creating and managing audio embeddings"""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize embedding service

        Args:
            vector_store: VectorStore instance (creates new if None)
        """
        self.vector_store = vector_store or get_vector_store()
        self.audio_engine = AudioEngine()
        self.executor = ThreadPoolExecutor(max_workers=4)

        logger.info("EmbeddingService initialized")

    async def index_audio_file(
        self,
        file_path: str,
        analysis_level: str = "STANDARD",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze and index an audio file

        Args:
            file_path: Path to audio file
            analysis_level: Analysis detail level
            metadata: Additional metadata to store

        Returns:
            Indexing result with document ID
        """
        try:
            # Analyze audio file
            loop = asyncio.get_event_loop()
            analysis_result = await loop.run_in_executor(
                self.executor,
                self.audio_engine.analyze,
                file_path,
                analysis_level
            )

            # Add to vector store
            doc_id = self.vector_store.add_audio_features(
                file_path=file_path,
                features=analysis_result.get('features', {}),
                metadata={
                    'analysis_level': analysis_level,
                    'file_size': Path(file_path).stat().st_size,
                    'file_name': Path(file_path).name,
                    **(metadata or {})
                }
            )

            logger.info(f"Indexed audio file: {file_path} (ID: {doc_id})")

            return {
                'doc_id': doc_id,
                'file_path': file_path,
                'features': analysis_result.get('features', {}),
                'status': 'indexed'
            }

        except Exception as e:
            logger.error(f"Error indexing audio file: {e}")
            raise

    async def index_directory(
        self,
        directory: str,
        recursive: bool = True,
        analysis_level: str = "STANDARD",
        extensions: List[str] = None
    ) -> Dict[str, Any]:
        """
        Index all audio files in a directory

        Args:
            directory: Directory path
            recursive: Whether to search recursively
            analysis_level: Analysis detail level
            extensions: List of file extensions to index

        Returns:
            Indexing results
        """
        if extensions is None:
            extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg']

        dir_path = Path(directory)
        if not dir_path.exists():
            raise ValueError(f"Directory not found: {directory}")

        # Find audio files
        audio_files = []
        if recursive:
            for ext in extensions:
                audio_files.extend(dir_path.rglob(f'*{ext}'))
        else:
            for ext in extensions:
                audio_files.extend(dir_path.glob(f'*{ext}'))

        logger.info(f"Found {len(audio_files)} audio files in {directory}")

        # Index files
        results = {
            'total_files': len(audio_files),
            'indexed': 0,
            'failed': 0,
            'files': []
        }

        for audio_file in audio_files:
            try:
                result = await self.index_audio_file(
                    str(audio_file),
                    analysis_level=analysis_level
                )
                results['indexed'] += 1
                results['files'].append({
                    'file': str(audio_file),
                    'status': 'success',
                    'doc_id': result['doc_id']
                })
            except Exception as e:
                results['failed'] += 1
                results['files'].append({
                    'file': str(audio_file),
                    'status': 'failed',
                    'error': str(e)
                })
                logger.error(f"Failed to index {audio_file}: {e}")

        logger.info(f"Directory indexing complete: {results['indexed']} indexed, {results['failed']} failed")

        return results

    async def find_similar(
        self,
        file_path: str,
        n_results: int = 10,
        exclude_self: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find similar audio files

        Args:
            file_path: Reference audio file path
            n_results: Number of similar files to return
            exclude_self: Whether to exclude the query file

        Returns:
            List of similar files with similarity scores
        """
        try:
            loop = asyncio.get_event_loop()
            similar = await loop.run_in_executor(
                self.executor,
                self.vector_store.search_by_file,
                file_path,
                n_results,
                exclude_self
            )

            return similar

        except Exception as e:
            logger.error(f"Error finding similar files: {e}")
            raise

    async def find_similar_by_features(
        self,
        features: Dict[str, Any],
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar audio files by features

        Args:
            features: Audio features to search for
            n_results: Number of results
            filter_metadata: Optional metadata filters

        Returns:
            List of similar files
        """
        try:
            loop = asyncio.get_event_loop()
            similar = await loop.run_in_executor(
                self.executor,
                self.vector_store.search_similar,
                features,
                n_results,
                filter_metadata
            )

            return similar

        except Exception as e:
            logger.error(f"Error finding similar by features: {e}")
            raise

    async def get_recommendations(
        self,
        file_path: str,
        n_results: int = 5,
        diversity: float = 0.3
    ) -> Dict[str, Any]:
        """
        Get smart recommendations based on audio file

        Args:
            file_path: Reference audio file
            n_results: Number of recommendations
            diversity: Diversity factor (0=similar, 1=diverse)

        Returns:
            Recommendations with categories
        """
        try:
            # Find similar files
            similar = await self.find_similar(
                file_path,
                n_results=int(n_results * 3)  # Get more for filtering
            )

            if not similar:
                return {
                    'reference_file': file_path,
                    'similar_samples': [],
                    'complementary_samples': [],
                    'contrasting_samples': []
                }

            # Categorize recommendations
            # Similar: High similarity (>0.8)
            similar_samples = [s for s in similar if s['similarity'] > 0.8][:n_results]

            # Complementary: Medium similarity (0.5-0.8)
            complementary = [s for s in similar if 0.5 <= s['similarity'] <= 0.8]
            if len(complementary) < n_results and len(similar) > 0:
                complementary = similar[len(similar_samples):len(similar_samples) + n_results]

            # Contrasting: Lower similarity but still relevant (0.3-0.5)
            contrasting = [s for s in similar if 0.3 <= s['similarity'] < 0.5]

            return {
                'reference_file': file_path,
                'similar_samples': similar_samples[:n_results],
                'complementary_samples': complementary[:n_results],
                'contrasting_samples': contrasting[:n_results],
                'total_results': len(similar)
            }

        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            raise

    async def remove_from_index(self, file_path: str) -> bool:
        """
        Remove audio file from index

        Args:
            file_path: Path to audio file

        Returns:
            Success status
        """
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                self.executor,
                self.vector_store.delete_audio,
                file_path
            )

            return success

        except Exception as e:
            logger.error(f"Error removing from index: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed audio"""
        return self.vector_store.get_collection_stats()

    async def reindex_file(
        self,
        file_path: str,
        analysis_level: str = "STANDARD"
    ) -> Dict[str, Any]:
        """
        Reindex an audio file (remove and re-add)

        Args:
            file_path: Path to audio file
            analysis_level: Analysis level

        Returns:
            Reindexing result
        """
        try:
            # Remove existing
            await self.remove_from_index(file_path)

            # Re-index
            result = await self.index_audio_file(file_path, analysis_level)

            # Update status to 'reindexed' (overriding 'indexed' from result)
            result['status'] = 'reindexed'
            return result

        except Exception as e:
            logger.error(f"Error reindexing file: {e}")
            raise


# Singleton instance
_embedding_service_instance: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create EmbeddingService singleton instance"""
    global _embedding_service_instance

    if _embedding_service_instance is None:
        _embedding_service_instance = EmbeddingService()

    return _embedding_service_instance
