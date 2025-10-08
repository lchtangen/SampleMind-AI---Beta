"""
Audio Embedding System

Extracts high-quality audio embeddings for similarity search and clustering.
Uses Essentia's pre-trained models for feature extraction and ChromaDB for
efficient vector storage and retrieval.

Features:
- Deep audio embeddings extraction
- Vector database storage (ChromaDB)
- Similarity search (find similar sounds)
- Audio clustering and organization
- Batch processing
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from loguru import logger
from dataclasses import dataclass
import json

# Essentia for embeddings
import essentia
import essentia.standard as es

# ChromaDB for vector storage
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    logger.warning("ChromaDB not available. Install with: pip install chromadb")
    CHROMADB_AVAILABLE = False


@dataclass
class AudioEmbedding:
    """Audio embedding with metadata"""
    file_path: Path
    embedding: np.ndarray
    metadata: Dict
    
    def __repr__(self):
        return f"AudioEmbedding({self.file_path.name}, dim={len(self.embedding)})"


@dataclass
class SimilarityResult:
    """Result of similarity search"""
    file_path: Path
    similarity: float
    metadata: Dict
    
    def __repr__(self):
        return f"{self.file_path.name} (similarity: {self.similarity:.2%})"


class AudioEmbedder:
    """
    Audio embedding extraction and similarity search
    
    Features:
    - Extract deep audio embeddings using CNN models
    - Store embeddings in ChromaDB vector database
    - Find similar audio files
    - Cluster audio by similarity
    - Batch processing support
    """
    
    # Available embedding models
    MODELS = {
        'musicnn': {
            'dim': 200,
            'description': 'MusicNN embeddings for music similarity'
        },
        'vggish': {
            'dim': 128,
            'description': 'VGGish embeddings (general audio)'
        },
        'openl3': {
            'dim': 512,
            'description': 'OpenL3 embeddings (high quality)'
        }
    }
    
    def __init__(
        self,
        model_name: str = 'musicnn',
        collection_name: str = 'audio_embeddings',
        persist_directory: Optional[Path] = None
    ):
        """
        Initialize audio embedder
        
        Args:
            model_name: Embedding model to use
            collection_name: ChromaDB collection name
            persist_directory: Directory to persist ChromaDB data
        """
        self.model_name = model_name
        self.collection_name = collection_name
        
        # Set persist directory
        if persist_directory is None:
            persist_directory = Path.home() / '.samplemind' / 'embeddings'
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize model and database
        self.model = None
        self.db_client = None
        self.collection = None
        
        logger.info(f"AudioEmbedder initialized with model: {model_name}")
    
    def _load_model(self):
        """Lazy load embedding model"""
        if self.model is not None:
            return
        
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            
            # Load Essentia embedding extractor
            # Note: This is a simplified version - actual implementation would
            # use specific Essentia extractors based on model_name
            self.model = es.TensorflowPredictMusiCNN(
                graphFilename='',  # Auto-download
                output='embeddings'
            )
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.warning("Using fallback feature extraction")
            self.model = None
    
    def _init_database(self):
        """Initialize ChromaDB"""
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available, running without vector storage")
            return
        
        if self.db_client is not None:
            return
        
        try:
            logger.info("Initializing ChromaDB")
            
            # Create ChromaDB client
            self.db_client = chromadb.PersistentClient(
                path=str(self.persist_directory)
            )
            
            # Get or create collection
            self.collection = self.db_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Audio embeddings for similarity search"}
            )
            
            logger.info(f"ChromaDB initialized: {self.collection.count()} embeddings stored")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            self.db_client = None
    
    def extract_embedding(
        self,
        audio_path: Path,
        include_metadata: bool = True
    ) -> AudioEmbedding:
        """
        Extract embedding from audio file
        
        Args:
            audio_path: Path to audio file
            include_metadata: Whether to extract additional metadata
        
        Returns:
            AudioEmbedding object
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Extracting embedding: {audio_path.name}")
        
        try:
            # Load audio
            loader = es.MonoLoader(filename=str(audio_path), sampleRate=16000)
            audio = loader()
            
            # Extract embedding
            embedding = self._extract_features(audio)
            
            # Extract metadata
            metadata = {}
            if include_metadata:
                metadata = self._extract_metadata(audio_path, audio)
            
            result = AudioEmbedding(
                file_path=audio_path,
                embedding=embedding,
                metadata=metadata
            )
            
            logger.info(f"Embedding extracted: dim={len(embedding)}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting embedding: {e}")
            raise
    
    def _extract_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract embedding features from audio"""
        try:
            self._load_model()
            
            if self.model is not None:
                # Use CNN model for embeddings
                embedding = self.model(audio)
                return embedding
            else:
                # Fallback: use spectral features as embedding
                return self._fallback_embedding(audio)
                
        except Exception as e:
            logger.warning(f"Model extraction failed: {e}, using fallback")
            return self._fallback_embedding(audio)
    
    def _fallback_embedding(self, audio: np.ndarray) -> np.ndarray:
        """Fallback embedding using spectral features"""
        # Extract various spectral features
        features = []
        
        # Spectrum
        spectrum = es.Spectrum()(audio)
        
        # MFCC (13 coefficients)
        mfcc = es.MFCC(numberCoefficients=13)(spectrum)
        features.extend(mfcc)
        
        # Spectral centroid
        centroid = es.Centroid()(spectrum)
        features.append(centroid)
        
        # Spectral rolloff
        rolloff = es.RollOff()(spectrum)
        features.append(rolloff)
        
        # Spectral flux
        flux = es.Flux()(spectrum)
        features.append(flux)
        
        # Energy
        energy = es.Energy()(audio)
        features.append(energy)
        
        # Zero crossing rate
        zcr = es.ZeroCrossingRate()(audio)
        features.append(zcr)
        
        # Pad to fixed size (128 dimensions)
        embedding = np.array(features)
        if len(embedding) < 128:
            embedding = np.pad(embedding, (0, 128 - len(embedding)))
        else:
            embedding = embedding[:128]
        
        return embedding
    
    def _extract_metadata(self, audio_path: Path, audio: np.ndarray) -> Dict:
        """Extract metadata from audio"""
        metadata = {
            'filename': audio_path.name,
            'path': str(audio_path),
            'size_bytes': audio_path.stat().st_size,
            'duration': len(audio) / 16000,  # Assuming 16kHz
        }
        
        # Add basic analysis
        try:
            metadata['rms'] = float(np.sqrt(np.mean(audio ** 2)))
            metadata['peak'] = float(np.max(np.abs(audio)))
        except Exception:
            pass
        
        return metadata
    
    def store_embedding(
        self,
        embedding: AudioEmbedding,
        update_if_exists: bool = True
    ) -> str:
        """
        Store embedding in vector database
        
        Args:
            embedding: AudioEmbedding to store
            update_if_exists: Whether to update if embedding exists
        
        Returns:
            Document ID
        """
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available, skipping storage")
            return ""
        
        self._init_database()
        
        if self.collection is None:
            logger.error("Collection not initialized")
            return ""
        
        try:
            # Generate unique ID
            doc_id = str(embedding.file_path)
            
            # Store in ChromaDB
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding.embedding.tolist()],
                metadatas=[embedding.metadata]
            )
            
            logger.info(f"Stored embedding: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            return ""
    
    def find_similar(
        self,
        audio_path: Path,
        n_results: int = 10,
        threshold: float = 0.0
    ) -> List[SimilarityResult]:
        """
        Find similar audio files
        
        Args:
            audio_path: Query audio file
            n_results: Number of results to return
            threshold: Minimum similarity threshold (0-1)
        
        Returns:
            List of SimilarityResult objects
        """
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available")
            return []
        
        self._init_database()
        
        if self.collection is None:
            logger.error("Collection not initialized")
            return []
        
        try:
            # Extract embedding for query
            query_embedding = self.extract_embedding(audio_path)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.embedding.tolist()],
                n_results=n_results
            )
            
            # Parse results
            similar = []
            
            if results and 'ids' in results:
                for i, doc_id in enumerate(results['ids'][0]):
                    # Skip self
                    if Path(doc_id) == audio_path:
                        continue
                    
                    # Get distance and convert to similarity (0-1)
                    distance = results['distances'][0][i] if 'distances' in results else 0
                    similarity = 1.0 / (1.0 + distance)  # Convert distance to similarity
                    
                    if similarity < threshold:
                        continue
                    
                    metadata = results['metadatas'][0][i] if 'metadatas' in results else {}
                    
                    similar.append(SimilarityResult(
                        file_path=Path(doc_id),
                        similarity=similarity,
                        metadata=metadata
                    ))
            
            logger.info(f"Found {len(similar)} similar files")
            return similar
            
        except Exception as e:
            logger.error(f"Error finding similar files: {e}")
            return []
    
    def batch_extract_and_store(
        self,
        audio_paths: List[Path],
        show_progress: bool = True
    ) -> int:
        """
        Extract and store embeddings for multiple files
        
        Args:
            audio_paths: List of audio file paths
            show_progress: Whether to show progress
        
        Returns:
            Number of successfully processed files
        """
        success_count = 0
        
        for i, audio_path in enumerate(audio_paths, 1):
            if show_progress:
                logger.info(f"Processing {i}/{len(audio_paths)}: {audio_path.name}")
            
            try:
                embedding = self.extract_embedding(audio_path)
                self.store_embedding(embedding)
                success_count += 1
            except Exception as e:
                logger.error(f"Error processing {audio_path.name}: {e}")
                continue
        
        logger.info(f"Batch processing complete: {success_count}/{len(audio_paths)} files")
        return success_count
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the embedding collection"""
        if not CHROMADB_AVAILABLE or self.collection is None:
            return {'error': 'ChromaDB not available'}
        
        try:
            count = self.collection.count()
            return {
                'total_embeddings': count,
                'collection_name': self.collection_name,
                'model': self.model_name,
                'persist_directory': str(self.persist_directory)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def clear_collection(self):
        """Clear all embeddings from collection"""
        if not CHROMADB_AVAILABLE or self.collection is None:
            logger.warning("Cannot clear: ChromaDB not available")
            return
        
        try:
            # Delete and recreate collection
            self.db_client.delete_collection(self.collection_name)
            self.collection = self.db_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Audio embeddings for similarity search"}
            )
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")


# Convenience functions

def quick_extract_embedding(audio_path: Path) -> AudioEmbedding:
    """Quick embedding extraction"""
    embedder = AudioEmbedder()
    return embedder.extract_embedding(audio_path)


def quick_find_similar(audio_path: Path, n_results: int = 5) -> List[SimilarityResult]:
    """Quick similarity search"""
    embedder = AudioEmbedder()
    return embedder.find_similar(audio_path, n_results)


def quick_build_library(audio_dir: Path) -> int:
    """Quick build embedding library from directory"""
    embedder = AudioEmbedder()
    
    # Find all audio files
    audio_paths = []
    for ext in ['*.wav', '*.mp3', '*.flac', '*.ogg', '*.m4a']:
        audio_paths.extend(audio_dir.glob(ext))
    
    logger.info(f"Found {len(audio_paths)} audio files")
    return embedder.batch_extract_and_store(audio_paths)
