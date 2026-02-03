"""
Semantic Audio Search Engine (Phase 15)

Uses CLAP (Contrastive Language-Audio Pretraining) to generate embeddings
for audio files and search them using natural language queries via ChromaDB.
"""

import logging
import uuid
from pathlib import Path
from typing import Any

try:
    import chromadb
    import librosa
    import torch
    from chromadb.config import Settings
    from transformers import ClapModel, ClapProcessor
except ImportError:
    # Handle missing deps gracefully (e.g. for lightweight installs)
    chromadb = None
    ClapModel = None
    ClapProcessor = None
    torch = None
    librosa = None

logger = logging.getLogger(__name__)

class VectorSearchEngine:
    """
    Manages audio embedding generation and vector search.
    """

    COLLECTION_NAME = "samplemind_audio"
    MODEL_NAME = "laion/clap-htsat-unfused"

    def __init__(self, persistent_path: str = "./db_chroma"):
        """
        Initialize the search engine.

        Args:
            persistent_path: Directory to store the vector database.
        """
        self.chroma_client = None
        self.collection = None
        self.model = None
        self.processor = None
        self.device = "cpu"
        self.persistent_path = persistent_path
        self._db_initialized = False

    def initialize_db(self):
        """Initialize ChromaDB client"""
        if not chromadb:
            logger.error("ChromaDB not installed")
            return

        try:
            self.chroma_client = chromadb.PersistentClient(path=self.persistent_path)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            self._db_initialized = True
            logger.info(f"Vector DB initialized at {self.persistent_path}")
        except Exception as e:
            logger.error(f"Failed to init ChromaDB: {e}")

    def load_model(self):
        """Load CLAP model and processor (Lazy Load)"""
        if self.model is not None:
            return

        if not torch or not ClapModel:
            logger.error("ML dependencies (torch, transformers) not found")
            return

        try:
            logger.info("Loading CLAP model... (this may take a moment)")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

            # Using the huggingface model
            self.processor = ClapProcessor.from_pretrained(self.MODEL_NAME)
            self.model = ClapModel.from_pretrained(self.MODEL_NAME).to(self.device)
            self.model.eval() # Inference mode
            logger.info(f"CLAP model loaded on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load CLAP model: {e}")

    def get_audio_embedding(self, file_path: Path) -> list[float] | None:
        """Generate embedding vector for an audio file"""
        self.load_model()
        if not self.model or not self.processor:
            return None

        try:
            # Load audio (resample to 48kHz for CLAP)
            y, sr = librosa.load(str(file_path), sr=48000, duration=10.0)

            # Prepare inputs
            inputs = self.processor(audios=y, sampling_rate=48000, return_tensors="pt").to(self.device)

            # Inference
            with torch.no_grad():
                outputs = self.model.get_audio_features(**inputs)

            # Convert to list
            embedding = outputs[0].cpu().numpy().tolist()
            return embedding
        except Exception as e:
            logger.error(f"Error embedding {file_path.name}: {e}")
            return None

    def get_text_embedding(self, text: str) -> list[float] | None:
        """Generate embedding vector for a text query"""
        self.load_model()
        if not self.model or not self.processor:
            return None

        try:
            inputs = self.processor(text=[text], return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.get_text_features(**inputs)

            embedding = outputs[0].cpu().numpy().tolist()
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text '{text}': {e}")
            return None

    def index_file(self, file_path: Path, metadata: dict[str, Any] = None) -> bool:
        """
        Index a single file into the vector database.

        Args:
            file_path: Path to the audio file
            metadata: Optional extra fields (duration, key, etc.)
        """
        if not self._db_initialized:
            self.initialize_db()

        if not self.collection:
            return False

        embedding = self.get_audio_embedding(file_path)
        if not embedding:
            return False

        # Prepare metadata
        if metadata is None:
            metadata = {}
        metadata["filename"] = file_path.name
        metadata["path"] = str(file_path.resolve())

        # ID: hash of path or UUID
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(file_path)))

        try:
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[file_path.name] # Optional source document
            )
            logger.info(f"Indexed: {file_path.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert to DB: {e}")
            return False

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        """
        Search for samples using a natural language query.

        Args:
            query: "sad piano", "punchy kick", etc.
            n_results: Number of matches

        Returns:
            List of dicts with 'path', 'score', 'metadata'
        """
        if not self._db_initialized:
            self.initialize_db()
        if not self.collection:
            return []

        query_embedding = self.get_text_embedding(query)
        if not query_embedding:
            return []

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

            # Format outputs
            formatted_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                count = len(results['ids'][0])
                for i in range(count):
                    # Chroma returns lists of lists
                    meta = results['metadatas'][0][i]
                    # distance/score ? 'distances' in results
                    distance = results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0

                    formatted_results.append({
                        "path": meta.get("path", ""),
                        "filename": meta.get("filename", ""),
                        "score": 1.0 - distance, # Convert distance to similarity score approx
                        "metadata": meta
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
