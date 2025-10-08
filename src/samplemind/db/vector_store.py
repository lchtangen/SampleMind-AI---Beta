"""
Vector Database Integration using ChromaDB

Provides vector storage and similarity search for audio features
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB wrapper for audio feature vectors"""

    def __init__(self, persist_directory: str = "data/chromadb"):
        """
        Initialize ChromaDB client

        Args:
            persist_directory: Directory to persist vector database
        """
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))

        # Use default embedding function for now
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        # Create collections
        self.audio_collection = self._get_or_create_collection("audio_features")
        self.sample_collection = self._get_or_create_collection("samples")

        logger.info(f"VectorStore initialized with persist directory: {self.persist_dir}")

    def _get_or_create_collection(self, name: str):
        """Get or create a collection"""
        try:
            return self.client.get_collection(name)
        except Exception:
            return self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )

    def add_audio_features(
        self,
        file_path: str,
        features: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add audio features to vector store

        Args:
            file_path: Path to audio file
            features: Extracted audio features
            metadata: Additional metadata

        Returns:
            Document ID
        """
        # Create feature vector from audio features
        feature_vector = self._create_feature_vector(features)

        # Prepare metadata
        doc_metadata = {
            "file_path": file_path,
            "file_name": Path(file_path).name,
            **(metadata or {})
        }

        # Add to collection
        doc_id = f"audio_{hash(file_path)}"

        self.audio_collection.add(
            ids=[doc_id],
            embeddings=[feature_vector],
            metadatas=[doc_metadata],
            documents=[file_path]
        )

        logger.info(f"Added audio features for: {file_path}")
        return doc_id

    def search_similar(
        self,
        features: Dict[str, Any],
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar audio samples

        Args:
            features: Audio features to search for
            n_results: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of similar samples with distances
        """
        # Create query vector
        query_vector = self._create_feature_vector(features)

        # Search
        results = self.audio_collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            where=filter_metadata
        )

        # Format results
        similar_samples = []
        for i in range(len(results['ids'][0])):
            similar_samples.append({
                'id': results['ids'][0][i],
                'file_path': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
            })

        return similar_samples

    def search_by_file(
        self,
        file_path: str,
        n_results: int = 10,
        exclude_self: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find samples similar to a given file

        Args:
            file_path: Path to reference audio file
            n_results: Number of results
            exclude_self: Whether to exclude the query file from results

        Returns:
            List of similar samples
        """
        # Get features for the file
        doc_id = f"audio_{hash(file_path)}"

        try:
            result = self.audio_collection.get(
                ids=[doc_id],
                include=['embeddings']
            )

            if len(result.get('embeddings', [])) == 0:
                raise ValueError(f"No features found for: {file_path}")

            query_vector = result['embeddings'][0]

            # Search
            results = self.audio_collection.query(
                query_embeddings=[query_vector],
                n_results=n_results + (1 if exclude_self else 0)
            )

            # Format results
            similar_samples = []
            for i in range(len(results['ids'][0])):
                if exclude_self and results['ids'][0][i] == doc_id:
                    continue

                similar_samples.append({
                    'id': results['ids'][0][i],
                    'file_path': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'similarity': 1 - results['distances'][0][i]
                })

            return similar_samples[:n_results]

        except Exception as e:
            logger.error(f"Error searching by file: {e}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            'audio_count': self.audio_collection.count(),
            'sample_count': self.sample_collection.count(),
            'persist_directory': str(self.persist_dir)
        }

    def delete_audio(self, file_path: str) -> bool:
        """
        Delete audio features from vector store

        Args:
            file_path: Path to audio file

        Returns:
            Success status
        """
        doc_id = f"audio_{hash(file_path)}"

        try:
            self.audio_collection.delete(ids=[doc_id])
            logger.info(f"Deleted audio features for: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting audio features: {e}")
            return False

    def _create_feature_vector(self, features: Dict[str, Any]) -> List[float]:
        """
        Create feature vector from audio features

        Args:
            features: Audio feature dictionary

        Returns:
            Feature vector as list of floats
        """
        # Extract key features and normalize
        vector = []

        # Basic features
        vector.append(features.get('tempo', 120.0) / 200.0)  # Normalize to 0-1
        vector.append(features.get('energy', 0.5))
        vector.append(features.get('loudness', -20.0) / -60.0)  # Normalize dB

        # Spectral features
        spectral = features.get('spectral_features', {})
        vector.append(spectral.get('centroid', 2000.0) / 10000.0)
        vector.append(spectral.get('bandwidth', 2000.0) / 10000.0)
        vector.append(spectral.get('rolloff', 5000.0) / 10000.0)
        vector.append(spectral.get('flatness', 0.5))
        vector.append(spectral.get('brightness', 0.5))

        # Harmonic features
        harmonic = features.get('harmonic_features', {})
        vector.append(harmonic.get('harmonic_ratio', 0.5))
        vector.append(harmonic.get('percussive_ratio', 0.5))

        # Rhythm features
        rhythm = features.get('rhythm_features', {})
        vector.append(rhythm.get('onset_strength', 0.5))
        vector.append(rhythm.get('beat_strength', 0.5))

        # Chroma features (reduce dimensionality)
        chroma = features.get('chroma', [])
        if chroma and len(chroma) > 0:
            if isinstance(chroma, list) and len(chroma) > 0 and isinstance(chroma[0], list):
                # Chroma is (12, time) - take mean across time axis
                chroma_array = np.array(chroma)
                if chroma_array.shape[0] == 12:
                    chroma_mean = np.mean(chroma_array, axis=1).tolist()[:12]
                else:
                    # Transpose if needed
                    chroma_mean = np.mean(chroma_array.T, axis=0).tolist()[:12]
            else:
                chroma_mean = chroma[:12]  # Take first 12 values
            # Ensure we have exactly 12 values
            while len(chroma_mean) < 12:
                chroma_mean.append(0.0)
            vector.extend(chroma_mean[:12])
        else:
            vector.extend([0.0] * 12)  # Pad with zeros

        # MFCC features (reduce dimensionality)
        mfcc = features.get('mfcc', [])
        if mfcc and len(mfcc) > 0:
            if isinstance(mfcc, list) and len(mfcc) > 0 and isinstance(mfcc[0], list):
                # MFCC is (n_mfcc, time) - take mean across time, use first 13 coefficients
                mfcc_array = np.array(mfcc)
                if mfcc_array.shape[0] >= 13:
                    mfcc_mean = np.mean(mfcc_array[:13], axis=1).tolist()
                else:
                    # Take what we have and pad
                    mfcc_mean = np.mean(mfcc_array, axis=1).tolist()
            else:
                mfcc_mean = mfcc[:13]
            # Ensure we have exactly 13 values
            while len(mfcc_mean) < 13:
                mfcc_mean.append(0.0)
            vector.extend(mfcc_mean[:13])
        else:
            vector.extend([0.0] * 13)  # Pad with zeros

        # Total: 12 + 13 + 12 = 37 dimensions

        # Ensure all values are floats
        vector = [float(v) for v in vector]

        return vector

    def clear_collection(self, collection_name: str = "audio_features") -> bool:
        """
        Clear all data from a collection

        Args:
            collection_name: Name of collection to clear

        Returns:
            Success status
        """
        try:
            self.client.delete_collection(collection_name)
            new_collection = self._get_or_create_collection(collection_name)

            # Update instance variable if it's one of our main collections
            if collection_name == "audio_features":
                self.audio_collection = new_collection
            elif collection_name == "samples":
                self.sample_collection = new_collection

            logger.info(f"Cleared collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            return False


# Singleton instance
_vector_store_instance: Optional[VectorStore] = None


def get_vector_store(persist_directory: str = "data/chromadb") -> VectorStore:
    """Get or create VectorStore singleton instance"""
    global _vector_store_instance

    if _vector_store_instance is None:
        _vector_store_instance = VectorStore(persist_directory)

    return _vector_store_instance
