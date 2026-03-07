#!/usr/bin/env python3
"""
SampleMind AI — Ollama Local Integration
Offline-capable AI inference using locally-running Ollama models.

Provides <100ms response times for basic analysis with no API keys required.
Requires Ollama running at localhost:11434 (or OLLAMA_HOST env var).

Supported models (install with `make install-models`):
  - qwen2.5:7b-instruct  (recommended, best quality)
  - phi3:mini             (fastest, lowest RAM)
  - gemma2:2b             (Google, good for music context)
"""

import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)


class OllamaModel(Enum):
    """Available Ollama local models"""
    QWEN_2_5_7B = "qwen2.5:7b-instruct"   # recommended — best quality
    PHI3_MINI = "phi3:mini"                 # fastest — lowest RAM
    GEMMA2_2B = "gemma2:2b"                # Google model
    LLAMA3_2 = "llama3.2:3b"               # Meta Llama 3.2 — good instruction following
    MISTRAL_7B = "mistral:7b-instruct"     # Mistral 7B instruct


@dataclass
class OllamaMusicAnalysis:
    """Result from Ollama local music analysis"""
    summary: str = ""
    production_tips: List[str] = field(default_factory=list)
    creative_ideas: List[str] = field(default_factory=list)
    model_used: OllamaModel = OllamaModel.QWEN_2_5_7B
    processing_time: float = 0.0
    timestamp: float = field(default_factory=time.time)
    # Conservative default — local models less reliable than cloud
    confidence_score: float = 0.5


class OllamaMusicProducer:
    """
    Offline-first music production AI using locally-running Ollama models.
    No API keys required. Needs `ollama serve` running.

    Priority 0 in the routing table: fastest (<100ms) but limited quality.
    Only used for QUICK_ANALYSIS routing, or when explicitly requested.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        default_model: OllamaModel = OllamaModel.QWEN_2_5_7B,
    ) -> None:
        if not OLLAMA_AVAILABLE:
            raise ImportError(
                "ollama package not installed. Install with: pip install ollama"
            )
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.default_model = default_model
        self._client = ollama.AsyncClient(host=self.host)
        logger.info(f"Ollama producer initialized: {default_model.value} @ {self.host}")

    async def analyze_music_comprehensive(
        self,
        audio_features: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> OllamaMusicAnalysis:
        """
        Perform quick music analysis with a local Ollama model.

        Args:
            audio_features: Audio features dict from audio engine
            user_context: Optional additional context

        Returns:
            OllamaMusicAnalysis with summary, tips, and ideas
        """
        start_time = time.time()
        prompt = self._build_prompt(audio_features, user_context)
        try:
            response = await self._client.chat(
                model=self.default_model.value,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7, "num_predict": 1024},
            )
            text = response.message.content  # ollama ^0.4.0: typed object, not dict
            result = self._parse_response(text)
            result.processing_time = time.time() - start_time
            result.model_used = self.default_model
            logger.info(
                f"Ollama analysis complete ({result.processing_time:.3f}s, "
                f"model={self.default_model.value})"
            )
            return result
        except Exception as e:
            logger.error(f"Ollama analysis failed: {e}")
            raise

    def _build_prompt(
        self, features: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> str:
        """Build a concise prompt for local model inference"""
        tempo = features.get("tempo", "unknown")
        key = features.get("key", "unknown")
        mode = features.get("mode", "unknown")
        duration = features.get("duration", "unknown")
        return (
            f"You are a music production expert. Analyze this audio track concisely.\n\n"
            f"Track info: {tempo} BPM, key {key} {mode}, {duration}s duration\n\n"
            f"Provide:\n1. One-sentence summary\n2. Top 3 production tips\n"
            f"3. Top 2 creative ideas\n\nKeep responses brief and practical."
        )

    def _parse_response(self, text: str) -> OllamaMusicAnalysis:
        """Parse plain-text Ollama response into structured fields"""
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        summary = lines[0] if lines else "Analysis complete."
        tips = [line.lstrip("0123456789.-) ") for line in lines[1:4] if line]
        ideas = [line.lstrip("0123456789.-) ") for line in lines[4:6] if line]
        return OllamaMusicAnalysis(
            summary=summary,
            production_tips=tips,
            creative_ideas=ideas,
        )

    async def analyze_audio_with_description(
        self,
        audio_features: Dict[str, Any],
        stem_description: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> OllamaMusicAnalysis:
        """
        Audio-aware analysis that incorporates pre-extracted feature descriptions.

        Accepts an optional ``stem_description`` (e.g. from Demucs separation) so
        the local model can reason about individual stems without loading audio data.

        Args:
            audio_features: Feature dict from the audio engine.
            stem_description: Human-readable description of detected stems/layers.
            user_context: Optional extra context for the model.

        Returns:
            OllamaMusicAnalysis with summary, tips, and ideas.
        """
        start_time = time.time()
        prompt = self._build_prompt(audio_features, user_context)
        if stem_description:
            prompt += (
                f"\n\nAdditional stem/layer context (from source separation):\n"
                f"{stem_description}\n\nPlease incorporate this stem information into your analysis."
            )
        try:
            response = await self._client.chat(
                model=self.default_model.value,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7, "num_predict": 1500},
            )
            text = response.message.content  # ollama ^0.4.0: typed object, not dict
            result = self._parse_response(text)
            result.processing_time = time.time() - start_time
            result.model_used = self.default_model
            logger.info(
                f"Ollama audio description analysis complete "
                f"({result.processing_time:.3f}s)"
            )
            return result
        except Exception as e:
            logger.error(f"Ollama audio description analysis failed: {e}")
            raise

    async def check_availability(self) -> bool:
        """Check if Ollama is running and the configured model is available."""
        try:
            models = await self._client.list()
            available = [m.model for m in models.models]  # ollama ^0.4.0: typed ListResponse
            return self.default_model.value in available
        except Exception:
            return False
