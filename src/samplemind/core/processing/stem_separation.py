import asyncio
import importlib.util
import logging
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Callable

from .exceptions import OptionalDependencyError

logger = logging.getLogger(__name__)

_DEFAULT_STEMS = ("vocals", "drums", "bass", "other")


class StemQuality(str, Enum):
    """Quality presets for stem separation"""
    FAST = "fast"           # Quick, lower quality
    STANDARD = "standard"   # Balanced quality/speed
    HIGH = "high"           # Best quality, slower


class StemBackend(str, Enum):
    """Available stem separation backends"""
    DEMUCS = "demucs"
    SPLEETER = "spleeter"


@dataclass
class QualityPreset:
    """Configuration for a quality preset"""
    model: str
    shifts: int
    overlap: float
    description: str


# Quality preset configurations
QUALITY_PRESETS: Dict[StemQuality, QualityPreset] = {
    StemQuality.FAST: QualityPreset(
        model="mdx",
        shifts=1,
        overlap=0.1,
        description="Fast processing, good for previews"
    ),
    StemQuality.STANDARD: QualityPreset(
        model="mdx_extra",
        shifts=1,
        overlap=0.25,
        description="Balanced quality and speed (recommended)"
    ),
    StemQuality.HIGH: QualityPreset(
        model="mdx_extra",
        shifts=5,
        overlap=0.5,
        description="Best quality, slower processing"
    ),
}


@dataclass
class StemSeparationResult:
    """Container for separated stem audio paths."""

    output_directory: Path
    stems: Dict[str, Path]
    command: List[str]


class StemSeparationEngine:
    """
    High-level wrapper around the `demucs` CLI for audio stem separation.

    Supports both Demucs v3 and v4 models:
    - v3: htdemucs, htdemucs_ft, hdemucs_mmi (classic models)
    - v4: mdx, mdx_extra, mdx_q (modern MDX-based models)

    The engine keeps the dependency optional – if `demucs` is not available in the
    current Python environment the feature will raise a helpful error rather than
    crashing at import time.
    """

    # Model categories for version detection
    V3_MODELS = {"htdemucs", "htdemucs_ft", "hdemucs_mmi"}
    V4_MODELS = {"mdx", "mdx_extra", "mdx_q"}
    ALL_MODELS = V3_MODELS | V4_MODELS

    def __init__(
        self,
        model: str = "mdx_extra",  # Changed default to v4 model
        device: Optional[str] = None,
        segment: Optional[float] = None,
        shifts: int = 1,  # Number of random shifts for inference stability
        overlap: float = 0.25,  # Overlap between segments (0-1)
        verbose: bool = False,  # Print progress information
    ) -> None:
        self.model = model
        self.device = device
        self.segment = segment
        self.shifts = shifts
        self.overlap = overlap
        self.verbose = verbose

        # Detect model version
        if model not in self.ALL_MODELS:
            logger.warning(
                "Unknown model '%s'. Assuming Demucs v4. "
                "Valid models: %s", model, self.ALL_MODELS
            )
        self.is_v4 = model in self.V4_MODELS or model not in self.V3_MODELS

    @classmethod
    def from_quality(
        cls,
        quality: StemQuality = StemQuality.STANDARD,
        device: Optional[str] = None,
        verbose: bool = False,
    ) -> "StemSeparationEngine":
        """
        Create a StemSeparationEngine from a quality preset.

        Args:
            quality: Quality preset (FAST, STANDARD, HIGH)
            device: Device to use (cpu, cuda, mps)
            verbose: Enable verbose output

        Returns:
            Configured StemSeparationEngine instance

        Example:
            engine = StemSeparationEngine.from_quality(StemQuality.HIGH)
            result = engine.separate("track.wav")
        """
        preset = QUALITY_PRESETS[quality]
        logger.info(f"Creating stem separation engine with {quality.value} preset: {preset.description}")
        return cls(
            model=preset.model,
            device=device,
            shifts=preset.shifts,
            overlap=preset.overlap,
            verbose=verbose,
        )

    @staticmethod
    def get_available_presets() -> Dict[str, str]:
        """Get available quality presets with descriptions"""
        return {q.value: QUALITY_PRESETS[q].description for q in StemQuality}

    @staticmethod
    def _assert_dependency() -> None:
        if importlib.util.find_spec("demucs") is None:
            raise OptionalDependencyError(
                "demucs",
                "Demucs is required for stem separation. Install it with `pip install demucs`.",
            )

    def separate(
        self,
        audio_path: Path,
        stems: Optional[Iterable[str]] = None,
        output_directory: Optional[Path] = None,
        clip_mode: str = "rescale",
        jobs: Optional[int] = None,
        two_stems: Optional[str] = None,  # v4: Split into 2 stems (e.g., "vocals")
    ) -> StemSeparationResult:
        """
        Run stem separation on an audio file and return the generated stems.

        Args:
            audio_path: Path to input audio file
            stems: Stems to extract (default: vocals, drums, bass, other)
            output_directory: Output directory for stems
            clip_mode: Clipping mode (rescale, clamp, softclip)
            jobs: Number of parallel jobs
            two_stems: (v4 only) Extract 2 stems (e.g., "vocals" or "drums")

        Returns:
            StemSeparationResult with separated stems
        """

        self._assert_dependency()

        audio_path = Path(audio_path).expanduser().resolve()
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        stems = tuple(stems) if stems else _DEFAULT_STEMS
        if set(stems) != set(_DEFAULT_STEMS):
            logger.warning(
                "Demucs currently supports the default stems %s; custom stems will be ignored.",
                _DEFAULT_STEMS,
            )

        target_dir = output_directory or Path(tempfile.mkdtemp(prefix="samplemind-demucs-"))
        target_dir = target_dir.expanduser().resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        command: List[str] = [
            sys.executable,
            "-m",
            "demucs",
        ]

        # Model selection (v3 vs v4 syntax)
        if self.is_v4:
            command.extend(["-n", self.model])
        else:
            command.extend(["-n", self.model])

        # Clipping mode
        command.extend(["--clip-mode", clip_mode])

        # Output directory
        command.extend(["-o", str(target_dir)])

        # Device selection (same for v3 and v4)
        if self.device:
            command.extend(["-d", self.device])

        # Segment size for long tracks (v4 supports longer segments)
        if self.segment:
            command.extend(["--segment", str(self.segment)])

        # Number of shifts for better quality (v4 feature)
        if self.shifts > 1 and self.is_v4:
            command.extend(["--shifts", str(self.shifts)])

        # Overlap factor (v4 feature)
        if self.overlap != 0.25 and self.is_v4:
            command.extend(["--overlap", str(self.overlap)])

        # Two stems mode (v4 feature for faster processing)
        if two_stems and self.is_v4:
            command.extend(["--two-stems", two_stems])

        # Parallel jobs
        if jobs:
            command.extend(["-j", str(jobs)])

        # Verbose output
        if self.verbose:
            command.append("-v")

        # Input file
        command.append(str(audio_path))

        logger.info("Running Demucs %s separation: %s",
                   "v4" if self.is_v4 else "v3",
                   " ".join(command))
        process = subprocess.run(command, check=False, capture_output=True, text=True)

        if process.returncode != 0:
            logger.error("Demucs separation failed: %s", process.stderr)
            raise RuntimeError(
                f"Demucs stem separation failed with code {process.returncode}: {process.stderr}"
            )

        # Demucs outputs files to <out>/<model>/<track_name>/<stem>.wav
        model_dir = target_dir / self.model
        track_dir = model_dir / audio_path.stem

        if not track_dir.exists():
            logger.error("Expected Demucs output directory not found: %s", track_dir)
            raise FileNotFoundError(f"Demucs output not found at {track_dir}")

        stem_map: Dict[str, Path] = {}
        for stem in _DEFAULT_STEMS:
            stem_path = track_dir / f"{stem}.wav"
            if stem_path.exists():
                stem_map[stem] = stem_path
            else:
                logger.warning("Stem '%s' missing from Demucs output.", stem)

        logger.info("Demucs separation complete. Generated %d stems.", len(stem_map))

        return StemSeparationResult(
            output_directory=track_dir,
            stems=stem_map,
            command=command,
        )

    async def batch_separate(
        self,
        audio_paths: List[Path],
        output_directory: Optional[Path] = None,
        max_concurrent: int = 1,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[StemSeparationResult]:
        """
        Separate multiple audio files with optional concurrency control.

        Args:
            audio_paths: List of paths to audio files
            output_directory: Base output directory for all stems
            max_concurrent: Maximum concurrent separations (default: 1 for stability)
            progress_callback: Callback function(current, total) for progress tracking

        Returns:
            List of StemSeparationResult objects

        Example:
            results = await engine.batch_separate(
                [Path("track1.wav"), Path("track2.wav")],
                max_concurrent=2,
                progress_callback=lambda c, t: print(f"{c}/{t} complete")
            )
        """
        self._assert_dependency()

        results = []
        total = len(audio_paths)

        # Use semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_file(index: int, path: Path) -> StemSeparationResult:
            async with semaphore:
                try:
                    # Run separation in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        self.separate,
                        path,
                        None,
                        output_directory,
                        "rescale",
                        None,
                        None,
                    )
                    logger.info(f"Separated {path.name} ({index+1}/{total})")
                    if progress_callback:
                        progress_callback(index + 1, total)
                    return result
                except Exception as e:
                    logger.error(f"Failed to separate {path.name}: {e}")
                    raise

        # Create tasks for all files
        tasks = [process_file(i, path) for i, path in enumerate(audio_paths)]

        # Run all tasks with progress tracking
        results = await asyncio.gather(*tasks, return_exceptions=False)

        logger.info(f"Batch separation complete. Processed {len(results)} files.")
        return results

    def batch_separate_sync(
        self,
        audio_paths: List[Path],
        output_directory: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[StemSeparationResult]:
        """
        Synchronous wrapper for batch_separate (blocks until complete).

        Args:
            audio_paths: List of paths to audio files
            output_directory: Base output directory
            progress_callback: Callback function(current, total)

        Returns:
            List of StemSeparationResult objects
        """
        return asyncio.run(
            self.batch_separate(audio_paths, output_directory, 1, progress_callback)
        )
