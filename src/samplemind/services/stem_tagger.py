"""
Stem Tagger — KP-40

Separates audio into stems (via demucs), runs the full analysis pipeline
on each stem, and writes auto-generated tags back to MongoDB.

Stem types (htdemucs_6s model): drums, bass, vocals, piano, guitar, other

For each stem:
- Spectral, rhythmic, harmonic, timbral analysis
- Quality scoring
- Genre classification
- Tags saved to MongoDB collection ``stem_tags``

Dependencies:
- ``demucs ^4.0.0``      (stem separation)
- ``motor ^3.6.0``       (async MongoDB driver)
- The analysis modules in ``samplemind.core.analysis``
"""

from __future__ import annotations

import asyncio
import logging
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Stem names produced by the htdemucs_6s model
STEM_NAMES = ["drums", "bass", "vocals", "piano", "guitar", "other"]


@dataclass
class StemAnalysis:
    """Analysis result for a single separated stem."""

    stem_name: str
    stem_path: str

    # Per-stem analysis (populated by analyze_stem)
    bpm: float = 0.0
    key: str = "C"
    mode: str = "major"
    camelot_key: str = "8B"
    primary_genre: str = "Unknown"
    genre_confidence: float = 0.0
    brightness_score: float = 0.0
    warmth_score: float = 0.0
    mood_label: str = "unknown"
    quality_score: float = 0.0
    quality_label: str = "unknown"
    duration_class: str = "unknown"
    duration: float = 0.0

    # Auto-generated tags
    tags: list[str] = field(default_factory=list)


@dataclass
class StemTagResult:
    """Full stem separation + tagging result for an audio file."""

    source_path: str
    stems: list[StemAnalysis] = field(default_factory=list)

    # MongoDB document _id (str after insertion)
    mongo_id: str | None = None
    success: bool = False
    error: str | None = None


class StemTagger:
    """
    Separates audio into stems via demucs and auto-tags each stem.

    Usage::

        tagger = StemTagger(mongo_uri="mongodb://localhost:27017")
        result = await tagger.tag_file(Path("track.wav"))

    MongoDB document structure::

        {
            "source_path": "/path/to/track.wav",
            "stems": [
                {
                    "stem_name": "drums",
                    "bpm": 128.0,
                    "tags": ["drums", "128bpm", "loop", "chill"],
                    ...
                },
                ...
            ]
        }
    """

    def __init__(
        self,
        mongo_uri: str = "mongodb://localhost:27017",
        db_name: str = "samplemind",
        collection_name: str = "stem_tags",
        model_name: str = "htdemucs_6s",
    ) -> None:
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.model_name = model_name

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def tag_file(
        self,
        path: Path,
        save_to_db: bool = True,
    ) -> StemTagResult:
        """
        Separate and tag all stems from an audio file.

        Args:
            path: Path to the source audio file
            save_to_db: If True, write result to MongoDB

        Returns:
            StemTagResult with all stem analyses and MongoDB id
        """
        path = Path(path).expanduser().resolve()
        result = StemTagResult(source_path=str(path))

        if not path.exists():
            result.error = f"File not found: {path}"
            return result

        # --- Stem separation (demucs) ------------------------------------
        try:
            stems = await asyncio.get_event_loop().run_in_executor(
                None, self._separate_stems, path
            )
        except Exception as exc:
            logger.error(f"Stem separation failed for {path}: {exc}")
            result.error = f"Stem separation failed: {exc}"
            return result

        # --- Analyze each stem in parallel --------------------------------
        analysis_tasks = [
            self._analyze_stem(stem_name, stem_path)
            for stem_name, stem_path in stems.items()
        ]
        stem_analyses = await asyncio.gather(*analysis_tasks, return_exceptions=True)

        for analysis in stem_analyses:
            if isinstance(analysis, BaseException):
                logger.warning(f"Stem analysis failed: {analysis}")
                continue
            result.stems.append(analysis)

        # --- Save to MongoDB ----------------------------------------------
        if save_to_db and result.stems:
            try:
                result.mongo_id = await self._save_to_mongo(result)
            except Exception as exc:
                logger.warning(f"MongoDB save failed: {exc}")

        result.success = len(result.stems) > 0
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _separate_stems(self, path: Path) -> dict[str, Path]:
        """
        Run demucs stem separation in a thread (CPU-bound).

        Returns dict mapping stem_name → stem_wav_path.
        """
        try:
            import demucs.separate as demucs_sep
        except ImportError as exc:
            raise RuntimeError(f"demucs is not installed: {exc}") from exc

        with tempfile.TemporaryDirectory(prefix="samplemind_stems_") as tmpdir:
            tmp = Path(tmpdir)

            # demucs.separate.main() is the CLI entry point
            # Run programmatically to avoid a subprocess
            args = [
                "--model",
                self.model_name,
                "--out",
                str(tmp),
                "--mp3",
                str(path),
            ]

            try:
                demucs_sep.main(args)
            except SystemExit:
                pass  # demucs calls sys.exit(0) on success

            # Collect output files
            # demucs writes to: <out>/<model>/<track_name>/<stem>.mp3
            stem_dir = tmp / self.model_name / path.stem
            if not stem_dir.exists():
                # Try with possible suffix in directory name
                candidates = list(tmp.glob(f"{self.model_name}/*"))
                stem_dir = candidates[0] if candidates else tmp

            stems: dict[str, Path] = {}
            for stem_name in STEM_NAMES:
                for ext in ("mp3", "wav", "flac"):
                    candidate = stem_dir / f"{stem_name}.{ext}"
                    if candidate.exists():
                        # Copy to a persistent temp dir outside the context manager
                        persistent = Path(tempfile.mkdtemp(prefix=f"stem_{stem_name}_"))
                        dest = persistent / candidate.name
                        import shutil

                        shutil.copy2(candidate, dest)
                        stems[stem_name] = dest
                        break

            return stems

    async def _analyze_stem(
        self,
        stem_name: str,
        stem_path: Path,
    ) -> StemAnalysis:
        """Run full analysis pipeline on a single stem."""
        from samplemind.core.analysis.genre_classifier import GenreClassifier
        from samplemind.core.analysis.harmonic_analyzer import HarmonicAnalyzer
        from samplemind.core.analysis.quality_scorer import AudioQualityScorer
        from samplemind.core.analysis.rhythmic_analyzer import RhythmicAnalyzer
        from samplemind.core.analysis.timbral_analyzer import TimbralAnalyzer

        analysis = StemAnalysis(stem_name=stem_name, stem_path=str(stem_path))

        # Run all analyzers concurrently
        rhythmic_task = asyncio.create_task(RhythmicAnalyzer().analyze_file(stem_path))
        harmonic_task = asyncio.create_task(HarmonicAnalyzer().analyze_file(stem_path))
        timbral_task = asyncio.create_task(TimbralAnalyzer().analyze_file(stem_path))
        quality_task = asyncio.create_task(AudioQualityScorer().score_file(stem_path))
        genre_task = asyncio.create_task(GenreClassifier().classify_file(stem_path))

        rhythmic, harmonic, timbral, quality, genre = await asyncio.gather(
            rhythmic_task,
            harmonic_task,
            timbral_task,
            quality_task,
            genre_task,
            return_exceptions=True,
        )

        # Populate StemAnalysis (handle any per-task exceptions gracefully)
        if not isinstance(rhythmic, BaseException):
            analysis.bpm = rhythmic.bpm
            analysis.duration = rhythmic.duration
            analysis.duration_class = rhythmic.duration_class

        if not isinstance(harmonic, BaseException):
            analysis.key = harmonic.key
            analysis.mode = harmonic.mode
            analysis.camelot_key = harmonic.camelot_key

        if not isinstance(timbral, BaseException):
            analysis.brightness_score = timbral.brightness_score
            analysis.warmth_score = timbral.warmth_score
            analysis.mood_label = timbral.mood_label

        if not isinstance(quality, BaseException):
            analysis.quality_score = quality.overall_score
            analysis.quality_label = quality.quality_label

        if not isinstance(genre, BaseException):
            analysis.primary_genre = genre.primary_genre
            analysis.genre_confidence = genre.primary_confidence

        # Generate tags
        analysis.tags = self._generate_tags(analysis)

        return analysis

    @staticmethod
    def _generate_tags(s: StemAnalysis) -> list[str]:
        """Compose a list of descriptive tags from the analysis results."""
        tags: list[str] = []

        # Stem type
        tags.append(s.stem_name)

        # BPM (round to nearest 5 for tagging)
        if s.bpm > 0:
            bpm_rounded = round(s.bpm / 5) * 5
            tags.append(f"{bpm_rounded}bpm")

        # Key + mode
        if s.key and s.mode:
            tags.append(f"{s.key}_{s.mode}")
            tags.append(s.camelot_key)

        # Genre
        if s.primary_genre and s.primary_genre != "Unknown":
            tags.append(s.primary_genre.lower().replace(" ", "_"))

        # Mood
        if s.mood_label and s.mood_label != "unknown":
            tags.append(s.mood_label)

        # Duration class
        if s.duration_class and s.duration_class != "unknown":
            tags.append(s.duration_class)

        # Quality
        if s.quality_label and s.quality_label != "unknown":
            tags.append(f"quality_{s.quality_label}")

        # Timbral
        if s.brightness_score >= 0.7:
            tags.append("bright")
        elif s.brightness_score <= 0.3:
            tags.append("dark")
        if s.warmth_score >= 0.7:
            tags.append("warm")

        return tags

    async def _save_to_mongo(self, result: StemTagResult) -> str | None:
        """
        Persist the StemTagResult to MongoDB.

        Returns the inserted document _id as a string, or None on failure.
        """
        try:
            import motor.motor_asyncio as motor

            client = motor.AsyncIOMotorClient(
                self.mongo_uri, serverSelectionTimeoutMS=3000
            )
            db = client[self.db_name]
            collection = db[self.collection_name]

            doc: dict[str, Any] = {
                "source_path": result.source_path,
                "stems": [asdict(s) for s in result.stems],
            }

            insert_result = await collection.insert_one(doc)
            return str(insert_result.inserted_id)

        except Exception as exc:
            logger.warning(f"MongoDB write failed: {exc}")
            return None
