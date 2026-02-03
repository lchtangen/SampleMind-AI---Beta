"""
SampleMind AI - Neural Audio Engine
Handles deep learning based audio analysis and embedding generation.
Designed to interface with models like CLAP, YAMNet, or Audio Spectrogram Transformer (AST).
"""

import hashlib
import logging
import random
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np

# Check for meaningful dependencies
try:
    import librosa
    import torch
    import torch.nn.functional as F
    from transformers import AutoModel, AutoProcessor
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class NeuralFeatureExtractor:
    """
    Extracts semantic embeddings from audio using neural networks.
    Supports CLAP (Contrastive Language-Audio Pretraining) for text-audio alignment.
    Falls back to 'mock' mode if dependencies are missing or requested.
    """

    def __init__(self, model_name: str = "laion/clap-htsat-unfused", use_gpu: bool = False, use_mock: bool = False):
        """
        Initialize the neural engine.

        Args:
            model_name: HuggingFace model identifier.
            use_gpu: Whether to use CUDA/MPS if available.
            use_mock: Force mock mode (random deterministic embeddings).
        """
        self.model_name = model_name
        self.use_mock = use_mock or (model_name == "mock")
        self.device = "cpu"
        self.processor = None
        self.model = None

        if not self.use_mock:
            self._init_device(use_gpu)
            if TRANSFORMERS_AVAILABLE:
                self._load_model()
            else:
                logger.warning("Transformers not found. Forcing mock mode.")
                self.use_mock = True
        else:
            logger.info("NeuralFeatureExtractor initialized in MOCK mode explicitly.")

    def _init_device(self, use_gpu: bool):
        """Determine the best available device."""
        if use_gpu and TRANSFORMERS_AVAILABLE:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"

    def _load_model(self):
        """Lazy loader for the heavy transformer models."""
        try:
            logger.info(f"🧠 Loading Neural Model: {self.model_name} on {self.device}...")
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
            logger.info("✓ Neural Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            logger.warning("Falling back to mock mode.")
            self.use_mock = True

    def generate_embedding(self, audio_path: Union[str, Path]) -> List[float]:
        """
        Generate a semantic embedding vector for the audio file.
        Returns a list of floats (size 512 for CLAP).
        """
        if self.use_mock:
            return self._generate_mock_embedding(str(audio_path))

        try:
            return self._generate_real_embedding(Path(audio_path))
        except Exception as e:
            logger.error(f"Error generating embedding for {audio_path}: {e}")
            return self._generate_mock_embedding(str(audio_path))

    def _generate_real_embedding(self, audio_path: Path) -> List[float]:
        """
        Generate actual embedding using CLAP model.
        """
        # Load audio at 48k (common for CLAP)
        # Use librosa to load and resample
        y, sr = librosa.load(str(audio_path), sr=48000, duration=10.0)

        # Prepare inputs
        inputs = self.processor(audios=y, sampling_rate=sr, return_tensors="pt").to(self.device)

        # Inference
        with torch.no_grad():
            outputs = self.model.get_audio_features(**inputs)

        # Return as list
        return outputs[0].cpu().numpy().tolist()

    def generate_text_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text query.
        Used for semantic search (Finding audio by description).
        """
        if self.use_mock:
            return self._generate_mock_embedding(text)

        try:
            inputs = self.processor(text=[text], return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.model.get_text_features(**inputs)
            return outputs[0].cpu().numpy().tolist()
        except Exception as e:
            logger.error(f"Error generating text embedding: {e}")
            return []

    def _generate_mock_embedding(self, seed_source: Union[str, Path], dim: int = 512) -> List[float]:
        """
        Generate a deterministic random embedding based on input string hash.
        """
        seed_val = int(hashlib.md5(str(seed_source).encode()).hexdigest(), 16) % (2**32)
        random.seed(seed_val)
        # Simulate a 512-dim vector (typical size)
        return [random.uniform(-1.0, 1.0) for _ in range(dim)]


