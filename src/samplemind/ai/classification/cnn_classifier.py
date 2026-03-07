"""
CNN-based audio classifier for SampleMind AI.

Lightweight 1-D convolutional network trained on mel-spectrogram frames.
Uses the same lazy-load + mock-fallback pattern as the rest of the AI stack.

Architecture:
  Conv1D(1→32, k=3) → BN → ReLU → MaxPool(2)
  Conv1D(32→64, k=3) → BN → ReLU → MaxPool(2)
  Flatten → FC(→256) → ReLU → Dropout(0.5) → FC(→num_classes)

All heavy imports (torch, librosa) are deferred to first use so that
importing this module is instant.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Production-relevant music class labels
# ---------------------------------------------------------------------------
MUSIC_CLASSES: List[str] = [
    "kick",
    "snare",
    "hi_hat_closed",
    "hi_hat_open",
    "clap",
    "cymbal",
    "bass",
    "lead_synth",
    "pad",
    "arp",
    "chord",
    "vocal",
    "vocal_chop",
    "fx_riser",
    "fx_downlifter",
    "fx_transition",
    "guitar_electric",
    "guitar_acoustic",
    "piano",
    "strings",
    "brass",
    "woodwind",
    "percussion_misc",
    "foley",
    "ambient_texture",
    "full_loop",
    "drum_loop",
    "melody_loop",
    "bass_loop",
]

# ---------------------------------------------------------------------------
# Lazy module-level state
# ---------------------------------------------------------------------------
_torch: Any = None
_librosa: Any = None
_TORCH_AVAILABLE: bool = False
_LIBROSA_AVAILABLE: bool = False


def _ensure_torch() -> bool:
    global _torch, _TORCH_AVAILABLE
    if _TORCH_AVAILABLE:
        return True
    try:
        import torch as _t
        _torch = _t
        _TORCH_AVAILABLE = True
        return True
    except ImportError:
        logger.warning("torch not available — CNNAudioClassifier will use mock mode")
        return False


def _ensure_librosa() -> bool:
    global _librosa, _LIBROSA_AVAILABLE
    if _LIBROSA_AVAILABLE:
        return True
    try:
        import librosa as _l
        _librosa = _l
        _LIBROSA_AVAILABLE = True
        return True
    except ImportError:
        logger.warning("librosa not available — CNNAudioClassifier will use mock mode")
        return False


# ---------------------------------------------------------------------------
# Dataclass for results
# ---------------------------------------------------------------------------
@dataclass
class CNNClassificationResult:
    """Result from CNNAudioClassifier.classify()."""

    top_predictions: List[Tuple[str, float]]
    """Ordered list of (label, confidence) pairs, highest confidence first."""

    all_scores: List[Tuple[str, float]]
    """Full score vector for all 29 classes."""

    audio_path: Path
    processing_time: float
    mock: bool = False

    @property
    def top_label(self) -> str:
        return self.top_predictions[0][0] if self.top_predictions else "unknown"

    @property
    def top_confidence(self) -> float:
        return self.top_predictions[0][1] if self.top_predictions else 0.0


# ---------------------------------------------------------------------------
# Model definition (defined lazily inside the class so that torch only needs
# to be imported once _ensure_torch() has succeeded)
# ---------------------------------------------------------------------------
def _build_model(num_classes: int) -> Any:
    """Return a compiled torch.nn.Module for 1-D CNN classification."""
    nn = _torch.nn

    class _CNNClassifier(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.conv1 = nn.Conv1d(1, 32, kernel_size=3, padding=1)
            self.bn1 = nn.BatchNorm1d(32)
            self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
            self.bn2 = nn.BatchNorm1d(64)
            self.pool = nn.MaxPool1d(2)
            self.relu = nn.ReLU()
            self.dropout = nn.Dropout(0.5)
            self.fc1 = nn.Linear(64 * 32, 256)  # assumes 128-len input → pool×2 = 32
            self.fc2 = nn.Linear(256, num_classes)

        def forward(self, x: Any) -> Any:  # x: (B, 1, T)
            x = self.pool(self.relu(self.bn1(self.conv1(x))))
            x = self.pool(self.relu(self.bn2(self.conv2(x))))
            x = x.flatten(1)
            # Dynamic FC1 on first pass if T != 128
            if x.shape[1] != self.fc1.in_features:
                self.fc1 = type(self.fc1)(x.shape[1], 256).to(x.device)
            x = self.relu(self.fc1(x))
            x = self.dropout(x)
            return self.fc2(x)

    return _CNNClassifier()


# ---------------------------------------------------------------------------
# Public classifier class
# ---------------------------------------------------------------------------
class CNNAudioClassifier:
    """
    Lightweight CNN for quick per-sample audio classification.

    Usage::

        clf = CNNAudioClassifier()
        result = await clf.classify(Path("kick.wav"), top_k=5)
        print(result.top_label, result.top_confidence)

    If ``torch`` or ``librosa`` are not installed the classifier operates in
    *mock mode* and returns plausible-looking deterministic predictions.
    """

    SR: int = 22050         # target sample rate
    N_MELS: int = 128       # mel bands (== 1-D input length after mean-pooling)
    HOP_LENGTH: int = 512

    def __init__(self, weights_path: Optional[Path] = None) -> None:
        self.weights_path = Path(weights_path) if weights_path else None
        self._model: Any = None
        self._device: Any = None
        self.use_mock: bool = False
        self._num_classes: int = len(MUSIC_CLASSES)

    # ------------------------------------------------------------------
    def _load_model(self) -> bool:
        """Lazy initialise the model (called on first classify)."""
        if self._model is not None:
            return True

        if not (_ensure_torch() and _ensure_librosa()):
            self.use_mock = True
            return False

        try:
            self._device = _torch.device(
                "cuda" if _torch.cuda.is_available()
                else "mps" if getattr(_torch.backends, "mps", None) and _torch.backends.mps.is_available()
                else "cpu"
            )
            self._model = _build_model(self._num_classes).to(self._device)
            self._model.eval()

            if self.weights_path and self.weights_path.exists():
                state = _torch.load(
                    self.weights_path, map_location=self._device, weights_only=True
                )
                self._model.load_state_dict(state)
                logger.info(f"CNNAudioClassifier: loaded weights from {self.weights_path}")
            else:
                logger.info(
                    "CNNAudioClassifier: no weights file — using random weights (mock-similar)"
                )

            return True
        except Exception as exc:
            logger.error(f"CNNAudioClassifier: model init failed: {exc}")
            self.use_mock = True
            return False

    # ------------------------------------------------------------------
    def _extract_features(self, audio_path: Path) -> Any:
        """Return a (1, 1, N_MELS) float32 torch tensor."""
        y, _ = _librosa.load(str(audio_path), sr=self.SR, mono=True)
        mel = _librosa.feature.melspectrogram(
            y=y, sr=self.SR, n_mels=self.N_MELS, hop_length=self.HOP_LENGTH
        )
        # Average over time axis → (N_MELS,)
        mel_mean: Any = mel.mean(axis=1)
        tensor = _torch.tensor(mel_mean, dtype=_torch.float32).unsqueeze(0).unsqueeze(0)
        return tensor.to(self._device)

    # ------------------------------------------------------------------
    def _run_inference(
        self, audio_path: Path, top_k: int
    ) -> CNNClassificationResult:
        """Synchronous inference — called inside ThreadPoolExecutor."""
        t0 = time.perf_counter()
        features = self._extract_features(audio_path)

        with _torch.no_grad():
            logits = self._model(features)           # (1, num_classes)
            probs = _torch.softmax(logits, dim=-1)[0].cpu().tolist()

        all_scores = sorted(
            zip(MUSIC_CLASSES, probs), key=lambda x: x[1], reverse=True
        )
        top_k_list = all_scores[:top_k]

        return CNNClassificationResult(
            top_predictions=list(top_k_list),
            all_scores=list(all_scores),
            audio_path=audio_path,
            processing_time=time.perf_counter() - t0,
        )

    # ------------------------------------------------------------------
    def _mock_result(self, audio_path: Path, top_k: int) -> CNNClassificationResult:
        """Deterministic mock result based on filename hash."""
        import hashlib

        digest = int(hashlib.md5(audio_path.name.encode()).hexdigest(), 16)
        scores = []
        for i, label in enumerate(MUSIC_CLASSES):
            score = ((digest >> i) & 0xFF) / 255.0
            scores.append((label, score))
        # Normalise
        total = sum(s for _, s in scores) or 1.0
        scores = [(lbl, s / total) for lbl, s in scores]
        scores.sort(key=lambda x: x[1], reverse=True)

        return CNNClassificationResult(
            top_predictions=scores[:top_k],
            all_scores=scores,
            audio_path=audio_path,
            processing_time=0.0,
            mock=True,
        )

    # ------------------------------------------------------------------
    async def classify(
        self,
        audio_path: Path,
        top_k: int = 5,
    ) -> CNNClassificationResult:
        """
        Classify an audio file and return the top-k predicted labels.

        Args:
            audio_path: Path to the audio file.
            top_k: How many top predictions to return (default 5).

        Returns:
            CNNClassificationResult with ordered predictions.
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if not self._load_model() or self.use_mock:
            return self._mock_result(audio_path, top_k)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._run_inference, audio_path, top_k)
