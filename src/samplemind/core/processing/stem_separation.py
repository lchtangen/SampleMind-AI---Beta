import importlib.util
import logging
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .exceptions import OptionalDependencyError

logger = logging.getLogger(__name__)

_DEFAULT_STEMS = ("vocals", "drums", "bass", "other")


@dataclass
class StemSeparationResult:
    """Container for separated stem audio paths."""

    output_directory: Path
    stems: Dict[str, Path]
    command: List[str]


class StemSeparationEngine:
    """
    High-level wrapper around the `demucs` CLI for audio stem separation.

    The engine keeps the dependency optional – if `demucs` is not available in the
    current Python environment the feature will raise a helpful error rather than
    crashing at import time.
    """

    def __init__(
        self,
        model: str = "htdemucs",
        device: Optional[str] = None,
        segment: Optional[float] = None,
    ) -> None:
        self.model = model
        self.device = device
        self.segment = segment

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
    ) -> StemSeparationResult:
        """Run stem separation on an audio file and return the generated stems."""

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
            "-n",
            self.model,
            "--clip-mode",
            clip_mode,
            "-o",
            str(target_dir),
        ]

        if self.device:
            command.extend(["-d", self.device])
        if self.segment:
            command.extend(["--segment", str(self.segment)])
        if jobs:
            command.extend(["-j", str(jobs)])

        command.append(str(audio_path))

        logger.info("Running Demucs separation: %s", " ".join(command))
        process = subprocess.run(command, check=False, capture_output=True, text=True)
        if process.returncode != 0:
            logger.error("Demucs separation failed: %s", process.stderr)
            raise RuntimeError(f"Demucs stem separation failed with code {process.returncode}")

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

        return StemSeparationResult(
            output_directory=track_dir,
            stems=stem_map,
            command=command,
        )
