"""
MusicGen / AudioCraft Integration — SampleMind Phase 16

Generates short audio samples from text prompts using Meta's MusicGen model
(via the `audiocraft` library). Supports BPM and key hints embedded in prompts.

When a GPU is unavailable or `audiocraft` is not installed, falls back to a
mock provider that returns a short silence WAV and logs a warning.

Model tiers (configured via MUSICGEN_MODEL env var):
  small   — musicgen-small   (300M params, fast, CPU-capable)
  medium  — musicgen-medium  (1.5B params, GPU recommended)
  large   — musicgen-large   (3.3B params, GPU required)
  stereo  — musicgen-stereo-large (stereo output, GPU required)

Configuration (env vars):
    MUSICGEN_MODEL      — Model size: small | medium | large | stereo (default: small)
    MUSICGEN_OUTPUT_DIR — Where generated WAV files are saved (default: ~/.samplemind/generated)

Usage::

    from samplemind.ai.generation.musicgen import MusicGenService

    gen = MusicGenService()
    result = await gen.generate(
        prompt="dark trap hi-hat loop",
        duration_s=4.0,
        bpm=140,
        key="Am",
    )
    print(result.file_path)   # /path/to/generated/dark-trap-hi-hat-loop.wav
    print(result.duration_s)  # 4.0
    print(result.model_used)  # musicgen-small

CLI::
    samplemind generate "dark trap kick" --bpm 140 --duration 2
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import struct
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

MUSICGEN_MODEL = os.getenv("MUSICGEN_MODEL", "small")
MUSICGEN_OUTPUT_DIR = Path(
    os.getenv("MUSICGEN_OUTPUT_DIR", str(Path.home() / ".samplemind" / "generated"))
)


@dataclass
class GenerationResult:
    """Result from a MusicGen generation call."""
    file_path: str
    prompt: str
    duration_s: float
    bpm: Optional[int]
    key: Optional[str]
    model_used: str
    generation_time_s: float
    is_mock: bool = False


class MusicGenService:
    """
    Text-to-audio generation via Meta MusicGen (AudioCraft).

    Gracefully degrades to a mock silent WAV when:
    - `audiocraft` is not installed
    - No CUDA GPU is available and model > small
    - Model loading fails for any reason
    """

    def __init__(self, model_size: Optional[str] = None) -> None:
        self.model_size = model_size or MUSICGEN_MODEL
        self._model = None
        self._model_loaded = False
        MUSICGEN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def _load_model(self) -> bool:
        """Lazy-load the MusicGen model. Returns True if real model loaded."""
        if self._model_loaded:
            return self._model is not None

        self._model_loaded = True
        try:
            from audiocraft.models import MusicGen  # type: ignore
            import torch

            model_name = f"facebook/musicgen-{self.model_size}"
            logger.info("Loading MusicGen model: %s", model_name)
            self._model = MusicGen.get_pretrained(model_name)
            logger.info("✓ MusicGen model loaded: %s", model_name)
            return True

        except ImportError:
            logger.warning(
                "audiocraft not installed — MusicGen in mock mode. "
                "Install: pip install audiocraft"
            )
        except Exception as exc:
            logger.warning("MusicGen model load failed (%s) — mock mode: %s", self.model_size, exc)

        self._model = None
        return False

    # ── Public API ────────────────────────────────────────────────────────────

    async def generate(
        self,
        prompt: str,
        duration_s: float = 4.0,
        bpm: Optional[int] = None,
        key: Optional[str] = None,
        temperature: float = 1.0,
        top_k: int = 250,
        output_filename: Optional[str] = None,
    ) -> GenerationResult:
        """
        Generate an audio sample from a text prompt.

        Args:
            prompt: Text description of the desired sound (e.g. "dark trap 808 bass").
            duration_s: Target duration in seconds (1–30).
            bpm: Optional BPM hint appended to prompt.
            key: Optional key hint (e.g. "Am") appended to prompt.
            temperature: Sampling temperature (higher = more random).
            top_k: Top-k tokens for sampling.
            output_filename: Override the output filename (without extension).

        Returns:
            GenerationResult with file_path and metadata.
        """
        duration_s = max(1.0, min(30.0, duration_s))
        enriched_prompt = _build_prompt(prompt, bpm, key)

        start = time.perf_counter()
        loop = asyncio.get_event_loop()

        has_real_model = await loop.run_in_executor(None, self._load_model)

        if has_real_model and self._model is not None:
            file_path = await loop.run_in_executor(
                None,
                self._generate_real,
                enriched_prompt,
                duration_s,
                temperature,
                top_k,
                output_filename,
            )
            model_used = f"musicgen-{self.model_size}"
            is_mock = False
        else:
            file_path = _generate_mock_wav(
                prompt=enriched_prompt,
                duration_s=duration_s,
                output_dir=MUSICGEN_OUTPUT_DIR,
                filename=output_filename,
            )
            model_used = "mock-silence"
            is_mock = True

        elapsed = time.perf_counter() - start
        logger.info(
            "%s generated %.1fs of audio in %.2fs: %s",
            model_used, duration_s, elapsed, file_path,
        )

        return GenerationResult(
            file_path=file_path,
            prompt=enriched_prompt,
            duration_s=duration_s,
            bpm=bpm,
            key=key,
            model_used=model_used,
            generation_time_s=round(elapsed, 3),
            is_mock=is_mock,
        )

    def _generate_real(
        self,
        prompt: str,
        duration_s: float,
        temperature: float,
        top_k: int,
        output_filename: Optional[str],
    ) -> str:
        """Blocking real generation — called from executor."""
        import torch

        model = self._model
        model.set_generation_params(
            duration=duration_s,
            temperature=temperature,
            top_k=top_k,
        )

        with torch.no_grad():
            wav = model.generate([prompt])  # shape: (1, channels, samples)

        # Save to WAV
        audio_array = wav[0].cpu().numpy()
        sample_rate = model.sample_rate

        slug = _slugify(prompt)[:60]
        filename = output_filename or f"{slug}_{int(time.time())}"
        out_path = MUSICGEN_OUTPUT_DIR / f"{filename}.wav"

        try:
            import soundfile as sf
            if audio_array.ndim == 2:
                # (channels, samples) → (samples, channels)
                audio_array = audio_array.T
            sf.write(str(out_path), audio_array, sample_rate)
        except ImportError:
            # Fallback: write raw PCM wav with wave module
            _write_wav_from_numpy(str(out_path), audio_array, sample_rate)

        return str(out_path)

    async def batch_generate(
        self,
        prompts: list[str],
        duration_s: float = 4.0,
        bpm: Optional[int] = None,
        key: Optional[str] = None,
    ) -> list[GenerationResult]:
        """Generate multiple samples sequentially (GPU memory safety)."""
        results = []
        for prompt in prompts:
            result = await self.generate(prompt, duration_s=duration_s, bpm=bpm, key=key)
            results.append(result)
        return results

    @staticmethod
    def list_generated(limit: int = 50) -> list[dict]:
        """List recently generated files."""
        files = sorted(MUSICGEN_OUTPUT_DIR.glob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
        return [
            {
                "filename": f.name,
                "path": str(f),
                "size_bytes": f.stat().st_size,
                "modified_at": f.stat().st_mtime,
            }
            for f in files[:limit]
        ]


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_prompt(base: str, bpm: Optional[int], key: Optional[str]) -> str:
    """Enrich a generation prompt with BPM/key metadata."""
    parts = [base.strip()]
    if bpm:
        parts.append(f"{bpm} BPM")
    if key:
        parts.append(f"{key} key")
    return ", ".join(parts)


def _slugify(text: str) -> str:
    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-")


def _generate_mock_wav(
    prompt: str,
    duration_s: float,
    output_dir: Path,
    filename: Optional[str] = None,
) -> str:
    """Generate a silent WAV file as a mock placeholder."""
    slug = _slugify(prompt)[:60]
    out_name = filename or f"mock_{slug}_{int(time.time())}"
    out_path = output_dir / f"{out_name}.wav"

    sample_rate = 44100
    n_samples = int(sample_rate * duration_s)
    # Write 16-bit PCM silence
    with wave.open(str(out_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * n_samples)

    return str(out_path)


def _write_wav_from_numpy(path: str, array, sample_rate: int) -> None:
    """Write a numpy float array to WAV without soundfile dependency."""
    import numpy as np
    if array.ndim == 2:
        array = array[:, 0]  # take first channel
    # Clip and convert to int16
    clipped = np.clip(array, -1.0, 1.0)
    pcm = (clipped * 32767).astype(np.int16)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())


# ── Singleton ─────────────────────────────────────────────────────────────────

_service: MusicGenService | None = None


def get_musicgen() -> MusicGenService:
    """Return the MusicGenService singleton."""
    global _service
    if _service is None:
        _service = MusicGenService()
    return _service
