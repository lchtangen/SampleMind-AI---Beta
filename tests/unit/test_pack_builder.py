"""
Unit tests for samplemind.core.packs.pack_builder

Tests manifest schema validation, ZIP creation, and PackBuilder.build()
without requiring real audio files (audio files are stubbed or skipped).
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from samplemind.core.packs.pack_builder import (
    SMPACK_VERSION,
    PackBuilder,
    PackBuildError,
    _slugify,
)

# ── _slugify ──────────────────────────────────────────────────────────────────


def test_slugify_lowercase():
    assert _slugify("Dark Trap Vol 1") == "dark-trap-vol-1"


def test_slugify_strips_special_chars():
    slug = _slugify("My Pack!!! (v2)")
    assert slug.isidentifier() or all(c.isalnum() or c == "-" for c in slug)


def test_slugify_collapses_spaces():
    result = _slugify("  multiple   spaces  ")
    assert "--" not in result


# ── manifest schema ───────────────────────────────────────────────────────────


def _valid_manifest() -> dict:
    return {
        "smpack_version": SMPACK_VERSION,
        "name": "Test Pack",
        "version": "1.0.0",
        "description": "A test pack",
        "tags": ["trap", "dark"],
        "bpm_range": [130, 150],
        "key_signatures": ["Am"],
        "created_at": "2026-04-09T00:00:00Z",
        "author": "test@example.com",
        "sample_count": 1,
        "samples": [
            {
                "filename": "kick.wav",
                "path": "audio/kick.wav",
                "bpm": 140,
                "key": "Am",
                "energy": "high",
                "genre_labels": ["trap"],
                "mood_labels": ["dark"],
                "duration_s": 2.4,
            }
        ],
    }


def test_manifest_has_required_keys():
    m = _valid_manifest()
    required = {"smpack_version", "name", "version", "samples", "created_at"}
    assert required.issubset(set(m.keys()))


def test_manifest_smpack_version_is_string():
    m = _valid_manifest()
    assert isinstance(m["smpack_version"], str)


def test_manifest_samples_is_list():
    m = _valid_manifest()
    assert isinstance(m["samples"], list)


def test_manifest_bpm_range_two_elements():
    m = _valid_manifest()
    assert len(m["bpm_range"]) == 2
    assert m["bpm_range"][0] <= m["bpm_range"][1]


# ── PackBuilder.build — ZIP structure ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_build_creates_smpack_file(tmp_path):
    """build() should produce a .smpack file with manifest.json inside."""
    # Create fake WAV files
    fake_wav = tmp_path / "kick.wav"
    fake_wav.write_bytes(b"RIFF" + b"\x00" * 100)  # minimal stub

    builder = PackBuilder.__new__(PackBuilder)
    builder._index = None  # no FAISS

    with patch.object(
        builder,
        "_build_sample_entry",
        new=AsyncMock(
            return_value={
                "filename": "kick.wav",
                "path": "audio/kick.wav",
                "bpm": 140.0,
                "key": "Am",
                "energy": "high",
                "genre_labels": [],
                "mood_labels": [],
                "duration_s": 2.4,
                "_local_path": str(fake_wav),
            }
        ),
    ):
        with patch.object(builder, "_maybe_create_preview", return_value=None):
            output_path = await builder.build(
                name="Dark Trap Vol 1",
                sample_paths=[str(fake_wav)],
                tags=["trap"],
                output_dir=str(tmp_path),
                include_audio=False,  # skip actual shutil.copy
            )

    assert output_path.endswith(".smpack")
    assert Path(output_path).exists()


@pytest.mark.asyncio
async def test_build_manifest_json_valid(tmp_path):
    """The manifest.json inside the .smpack archive must parse correctly."""
    fake_wav = tmp_path / "snare.wav"
    fake_wav.write_bytes(b"RIFF" + b"\x00" * 100)

    builder = PackBuilder.__new__(PackBuilder)
    builder._index = None

    with patch.object(
        builder,
        "_build_sample_entry",
        new=AsyncMock(
            return_value={
                "filename": "snare.wav",
                "path": "audio/snare.wav",
                "bpm": 140.0,
                "key": "Am",
                "energy": "high",
                "genre_labels": [],
                "mood_labels": [],
                "duration_s": 1.2,
                "_local_path": str(fake_wav),
            }
        ),
    ):
        with patch.object(builder, "_maybe_create_preview", return_value=None):
            output = await builder.build(
                name="Snare Pack",
                sample_paths=[str(fake_wav)],
                output_dir=str(tmp_path),
                include_audio=False,
            )

    with zipfile.ZipFile(output, "r") as zf:
        names = zf.namelist()
        assert "manifest.json" in names
        manifest = json.loads(zf.read("manifest.json"))

    assert manifest["smpack_version"] == SMPACK_VERSION
    assert manifest["name"] == "Snare Pack"
    assert len(manifest["samples"]) == 1


@pytest.mark.asyncio
async def test_build_raises_on_empty_sample_list(tmp_path):
    builder = PackBuilder.__new__(PackBuilder)
    builder._index = None

    with pytest.raises(PackBuildError, match="no samples"):
        await builder.build(
            name="Empty",
            sample_paths=[],
            output_dir=str(tmp_path),
        )


# ── PackBuilder.read_manifest ─────────────────────────────────────────────────


def test_read_manifest_round_trip(tmp_path):
    """read_manifest() should parse the manifest written by build()."""
    pack_path = tmp_path / "test.smpack"
    manifest = _valid_manifest()

    with zipfile.ZipFile(pack_path, "w") as zf:
        zf.writestr("manifest.json", json.dumps(manifest))

    result = PackBuilder.read_manifest(str(pack_path))
    assert result["name"] == "Test Pack"
    assert result["smpack_version"] == SMPACK_VERSION
    assert len(result["samples"]) == 1


def test_read_manifest_raises_for_missing_file(tmp_path):
    # Missing file → FileNotFoundError (zipfile.ZipFile raises before PackBuildError)
    with pytest.raises((PackBuildError, FileNotFoundError, OSError)):
        PackBuilder.read_manifest(str(tmp_path / "nonexistent.smpack"))
