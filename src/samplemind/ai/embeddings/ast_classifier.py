#!/usr/bin/env python3
"""
SampleMind AI — AST Audio Classifier
527-class AudioSet classification using the Audio Spectrogram Transformer (AST).

Model: ``MIT/ast-finetuned-audioset-10-10-0.4593``
Output: Top-N AudioSet labels with confidence scores.

Follows the lazy-load + mock-fallback pattern from neural_engine.py.
"""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy globals
# ---------------------------------------------------------------------------

_torch: Any = None
_ASTForAudioClassification: Any = None
_AutoFeatureExtractor: Any = None
_AST_AVAILABLE = False
_AST_MODEL_NAME = "MIT/ast-finetuned-audioset-10-10-0.4593"

# Subset of AudioSet classes relevant to music/sample production
_MUSIC_RELEVANT_LABELS = frozenset(
    {
        "Music",
        "Musical instrument",
        "Drum",
        "Bass drum",
        "Snare drum",
        "Hi-hat",
        "Cymbal",
        "Guitar",
        "Bass guitar",
        "Electric guitar",
        "Piano",
        "Keyboard",
        "Synthesizer",
        "Violin",
        "Trumpet",
        "Saxophone",
        "Clapping",
        "Singing",
        "Vocal",
        "Beat",
        "Rhythm",
        "Melody",
        "Chord",
        "Electronic music",
        "Hip hop music",
        "Pop music",
        "Rock music",
        "Techno",
        "Dance music",
    }
)


def _ensure_ast() -> bool:
    global _torch, _ASTForAudioClassification, _AutoFeatureExtractor, _AST_AVAILABLE
    if _AST_AVAILABLE:
        return True
    try:
        import torch as _t
        from transformers import ASTForAudioClassification as _AST
        from transformers import AutoFeatureExtractor as _AFE

        _torch = _t
        _ASTForAudioClassification = _AST
        _AutoFeatureExtractor = _AFE
        _AST_AVAILABLE = True
    except ImportError:
        logger.warning(
            "transformers or torch not installed — ASTClassifier falling back to mock mode"
        )
    return _AST_AVAILABLE


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


class AudioLabel:
    """A single AudioSet classification result."""

    __slots__ = ("label", "score", "label_id")

    def __init__(self, label: str, score: float, label_id: int = -1) -> None:
        self.label = label
        self.score = score
        self.label_id = label_id

    def __repr__(self) -> str:
        return f"AudioLabel(label={self.label!r}, score={self.score:.3f})"


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


class ASTClassifier:
    """
    MIT AST classifies audio into 527 AudioSet categories.

    Features:
    - Lazy model loading
    - CPU / CUDA / MPS auto-detection
    - Configurable top-N outputs
    - Optional filtering to music-relevant labels
    - Mock mode for tests / missing deps

    Usage::

        clf = ASTClassifier()
        labels = clf.classify("sample.wav", top_k=5)
        for lbl in labels:
            print(lbl.label, lbl.score)
    """

    def __init__(
        self,
        model_name: str = _AST_MODEL_NAME,
        use_gpu: bool = True,
        use_mock: bool = False,
    ) -> None:
        self.model_name = model_name
        self.use_mock = use_mock or (model_name == "mock")
        self.device = "cpu"
        self._extractor: Any = None
        self._model: Any = None

        if not self.use_mock:
            if _ensure_ast():
                self._init_device(use_gpu)
                self._load_model()
            else:
                self.use_mock = True
        if self.use_mock:
            logger.info("ASTClassifier initialised in MOCK mode")

    # ------------------------------------------------------------------

    def _init_device(self, use_gpu: bool) -> None:
        if use_gpu and _AST_AVAILABLE:
            if _torch.cuda.is_available():
                self.device = "cuda"
            elif _torch.backends.mps.is_available():
                self.device = "mps"

    def _load_model(self) -> None:
        try:
            logger.info(f"Loading AST model: {self.model_name} on {self.device}")
            self._extractor = _AutoFeatureExtractor.from_pretrained(self.model_name)
            self._model = _ASTForAudioClassification.from_pretrained(
                self.model_name
            ).to(self.device)
            self._model.eval()
            logger.info("AST model loaded successfully")
        except Exception as exc:
            logger.error(f"Failed to load AST model: {exc}")
            logger.warning("Falling back to mock mode")
            self.use_mock = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(
        self,
        audio_path: str | Path,
        top_k: int = 10,
        music_only: bool = False,
    ) -> list[AudioLabel]:
        """
        Classify audio into AudioSet categories.

        Args:
            audio_path:   Path to audio file.
            top_k:        Number of top predictions to return.
            music_only:   If ``True``, filter to music-relevant labels only.

        Returns:
            List of :class:`AudioLabel` sorted by score descending.
        """
        audio_path = Path(audio_path)
        if self.use_mock:
            return self._mock_labels(top_k)
        return self._classify_file(audio_path, top_k, music_only)

    def classify_batch(
        self,
        paths: list[str | Path],
        top_k: int = 10,
    ) -> list[list[AudioLabel]]:
        """Classify multiple files."""
        return [self.classify(p, top_k) for p in paths]

    def get_primary_label(self, audio_path: str | Path) -> str:
        """Return the single highest-confidence AudioSet label."""
        labels = self.classify(audio_path, top_k=1)
        return labels[0].label if labels else "Unknown"

    # ------------------------------------------------------------------

    def _classify_file(
        self, audio_path: Path, top_k: int, music_only: bool
    ) -> list[AudioLabel]:
        try:
            import librosa

            waveform, _ = librosa.load(str(audio_path), sr=16000, mono=True)
        except Exception as exc:
            logger.error(f"Audio load failed: {exc}")
            return self._mock_labels(top_k)

        try:
            inputs = self._extractor(
                waveform, sampling_rate=16000, return_tensors="pt"
            ).to(self.device)

            with _torch.no_grad():
                logits = self._model(**inputs).logits
                probs = _torch.sigmoid(logits).squeeze(0).cpu().numpy()

            id2label: dict[int, str] = self._model.config.id2label
            results = [
                AudioLabel(label=id2label[i], score=float(probs[i]), label_id=i)
                for i in range(len(probs))
            ]
            results.sort(key=lambda x: x.score, reverse=True)

            if music_only:
                results = [r for r in results if r.label in _MUSIC_RELEVANT_LABELS]

            return results[:top_k]

        except Exception as exc:
            logger.error(f"AST inference failed: {exc}")
            return self._mock_labels(top_k)

    def _mock_labels(self, top_k: int) -> list[AudioLabel]:
        mock = [
            AudioLabel("Music", 0.95),
            AudioLabel("Drum", 0.82),
            AudioLabel("Beat", 0.77),
            AudioLabel("Electronic music", 0.71),
            AudioLabel("Bass drum", 0.66),
            AudioLabel("Hi-hat", 0.61),
            AudioLabel("Synthesizer", 0.55),
            AudioLabel("Piano", 0.50),
            AudioLabel("Guitar", 0.45),
            AudioLabel("Vocal", 0.38),
        ]
        return mock[:top_k]
