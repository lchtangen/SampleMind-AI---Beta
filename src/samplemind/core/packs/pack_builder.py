"""
.smpack Format + Pack Builder — SampleMind Phase 15

.smpack is a ZIP archive containing:
  manifest.json  — pack metadata (name, version, tags, samples[])
  audio/         — audio files (copied from local library)
  preview.wav    — optional short preview (first 30s of first sample)

Spec:
  manifest.json schema:
    {
      "smpack_version": "1.0",
      "name": "Dark Trap Vol 1",
      "version": "1.0.0",
      "description": "...",
      "tags": ["trap", "dark", "808"],
      "bpm_range": [130, 150],
      "key_signatures": ["Am", "Dm"],
      "created_at": "2026-04-09T00:00:00Z",
      "author": "user@example.com",
      "samples": [
        {
          "filename": "kick_140.wav",
          "path": "audio/kick_140.wav",
          "bpm": 140,
          "key": "Am",
          "energy": "high",
          "genre_labels": ["trap"],
          "mood_labels": ["dark"],
          "duration_s": 2.4
        }
      ]
    }

Usage::

    from samplemind.core.packs.pack_builder import PackBuilder

    builder = PackBuilder()
    pack_path = await builder.build(
        name="Dark Trap Vol 1",
        sample_paths=["/path/to/kick.wav", "/path/to/snare.wav"],
        tags=["trap", "dark"],
        output_dir="./packs/",
    )
    # → "./packs/dark-trap-vol-1.smpack"

    # Read back
    manifest = PackBuilder.read_manifest(pack_path)
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import shutil
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

SMPACK_VERSION = "1.0"


class PackBuildError(Exception):
    """Raised when pack construction fails."""


class PackBuilder:
    """
    Builds .smpack archives from a list of local audio file paths.

    Reads metadata from the FAISS index when available; falls back to
    filename heuristics for BPM/key/energy estimation.
    """

    def __init__(self) -> None:
        self._index = self._load_index()

    def _load_index(self):
        try:
            from samplemind.core.search.faiss_index import get_index

            return get_index()
        except Exception:
            return None

    # ── Public API ────────────────────────────────────────────────────────────

    async def build(
        self,
        name: str,
        sample_paths: list[str],
        tags: list[str] | None = None,
        description: str = "",
        author: str = "",
        output_dir: str = ".",
        include_audio: bool = True,
    ) -> str:
        """
        Build a .smpack archive.

        Args:
            name: Human-readable pack name (e.g. "Dark Trap Vol 1").
            sample_paths: Absolute paths to audio files to include.
            tags: Genre/mood/style tags.
            description: Free-text description.
            author: Creator email or username.
            output_dir: Directory where the .smpack file will be written.
            include_audio: If True, copies audio files into the archive.
                           Set False to create a metadata-only manifest pack.

        Returns:
            Absolute path to the created .smpack file.
        """
        if not sample_paths:
            raise PackBuildError("Cannot build a pack with no samples.")

        slug = _slugify(name)
        output_path = Path(output_dir) / f"{slug}.smpack"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        sample_entries = await asyncio.gather(
            *[self._build_sample_entry(p, include_audio) for p in sample_paths]
        )

        bpms = [e["bpm"] for e in sample_entries if e.get("bpm")]
        keys = list({e["key"] for e in sample_entries if e.get("key")})

        manifest = {
            "smpack_version": SMPACK_VERSION,
            "name": name,
            "version": "1.0.0",
            "description": description,
            "tags": tags or [],
            "bpm_range": [min(bpms), max(bpms)] if bpms else [],
            "key_signatures": keys,
            "created_at": datetime.now(UTC).isoformat(),
            "author": author,
            "sample_count": len(sample_entries),
            "samples": sample_entries,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            (tmp / "audio").mkdir()

            # Write manifest
            manifest_path = tmp / "manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2))

            # Copy audio files
            if include_audio:
                for entry in sample_entries:
                    src = entry.get("_local_path")
                    if src and Path(src).exists():
                        shutil.copy2(src, tmp / "audio" / entry["filename"])

            # Create preview from first sample
            self._maybe_create_preview(sample_paths[0] if sample_paths else None, tmp)

            # Zip everything
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(manifest_path, "manifest.json")
                for audio_file in (tmp / "audio").iterdir():
                    zf.write(audio_file, f"audio/{audio_file.name}")
                preview = tmp / "preview.wav"
                if preview.exists():
                    zf.write(preview, "preview.wav")

        logger.info("✓ Built pack: %s (%d samples)", output_path, len(sample_entries))
        return str(output_path)

    async def _build_sample_entry(self, path: str, include_audio: bool) -> dict:
        """Build a manifest sample entry from a file path."""
        p = Path(path)
        entry: dict = {
            "filename": p.name,
            "path": f"audio/{p.name}" if include_audio else path,
            "_local_path": path,
            "bpm": None,
            "key": None,
            "energy": None,
            "genre_labels": [],
            "mood_labels": [],
            "duration_s": None,
        }

        # Try FAISS index first
        if self._index:
            by_path = {e.path: e for e in self._index._entries}
            idx_entry = by_path.get(path)
            if idx_entry:
                entry["bpm"] = idx_entry.bpm
                entry["key"] = idx_entry.key
                entry["energy"] = idx_entry.energy
                entry["genre_labels"] = idx_entry.genre_labels or []
                entry["mood_labels"] = idx_entry.mood_labels or []

        # Fallback: filename heuristics for BPM
        if entry["bpm"] is None:
            entry["bpm"] = _bpm_from_filename(p.name)

        # Duration via soundfile if available
        entry["duration_s"] = await _get_duration(path)

        return entry

    def _maybe_create_preview(self, first_path: str | None, tmp: Path) -> None:
        """Create a 30-second preview clip from the first sample."""
        if not first_path:
            return
        try:
            import soundfile as sf

            data, sr = sf.read(first_path, always_2d=True)
            preview_samples = min(len(data), sr * 30)
            preview_data = data[:preview_samples]
            sf.write(str(tmp / "preview.wav"), preview_data, sr)
        except Exception:
            pass  # Preview is optional

    # ── Static helpers ────────────────────────────────────────────────────────

    @staticmethod
    def read_manifest(smpack_path: str) -> dict:
        """
        Read the manifest.json from a .smpack archive.

        Returns:
            Parsed manifest dict.

        Raises:
            PackBuildError if the archive is invalid.
        """
        try:
            with zipfile.ZipFile(smpack_path, "r") as zf:
                with zf.open("manifest.json") as f:
                    return json.loads(f.read())
        except (zipfile.BadZipFile, KeyError) as exc:
            raise PackBuildError(f"Invalid .smpack archive: {smpack_path}") from exc

    @staticmethod
    def extract(smpack_path: str, output_dir: str) -> list[str]:
        """
        Extract all audio files from a .smpack archive.

        Returns:
            List of extracted file paths.
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        extracted = []
        with zipfile.ZipFile(smpack_path, "r") as zf:
            for member in zf.namelist():
                if member.startswith("audio/") and not member.endswith("/"):
                    target = out / Path(member).name
                    with zf.open(member) as src, open(target, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    extracted.append(str(target))
        logger.info(
            "Extracted %d files from %s → %s", len(extracted), smpack_path, output_dir
        )
        return extracted

    @staticmethod
    def validate(smpack_path: str) -> tuple[bool, list[str]]:
        """
        Validate a .smpack archive.

        Returns:
            (is_valid, list_of_errors)
        """
        errors: list[str] = []
        try:
            with zipfile.ZipFile(smpack_path, "r") as zf:
                names = set(zf.namelist())
                if "manifest.json" not in names:
                    errors.append("Missing manifest.json")
                    return False, errors

                manifest = json.loads(zf.read("manifest.json"))
                required = ["smpack_version", "name", "samples"]
                for field in required:
                    if field not in manifest:
                        errors.append(f"manifest.json missing field: {field}")

                # Check audio files match manifest
                for sample in manifest.get("samples", []):
                    audio_path = sample.get("path", "")
                    if audio_path.startswith("audio/") and audio_path not in names:
                        errors.append(f"Audio file missing from archive: {audio_path}")

        except zipfile.BadZipFile:
            errors.append("Not a valid ZIP/smpack archive")
        except json.JSONDecodeError as exc:
            errors.append(f"manifest.json is not valid JSON: {exc}")

        return len(errors) == 0, errors


# ── Helpers ───────────────────────────────────────────────────────────────────


def _slugify(text: str) -> str:
    """Convert display name to filesystem-safe slug."""
    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-")


def _bpm_from_filename(filename: str) -> int | None:
    """Extract BPM from filename patterns like 'kick_140bpm.wav' or 'snare-130.wav'."""
    patterns = [
        r"(\d{2,3})\s*bpm",
        r"_(\d{2,3})_",
        r"-(\d{2,3})-",
        r"[\s_-](\d{2,3})[\s_.-]",
    ]
    name_lower = filename.lower()
    for pat in patterns:
        m = re.search(pat, name_lower)
        if m:
            bpm = int(m.group(1))
            if 60 <= bpm <= 220:
                return bpm
    return None


async def _get_duration(path: str) -> float | None:
    """Get audio duration in seconds using soundfile (non-blocking)."""

    def _read():
        try:
            import soundfile as sf

            info = sf.info(path)
            return info.duration
        except Exception:
            return None

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _read)


# ── Module-level convenience ──────────────────────────────────────────────────


_builder: PackBuilder | None = None


def get_pack_builder() -> PackBuilder:
    """Return the PackBuilder singleton."""
    global _builder
    if _builder is None:
        _builder = PackBuilder()
    return _builder
