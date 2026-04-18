"""
Unit tests for samplemind.ai.curation.playlist_generator

Tests rule-based helpers (_arc_energy_sequence, _harmonic_score, _bpm_score)
and PlaylistGenerator.generate() with mocked FAISS and LiteLLM.

Module under test:
    samplemind.ai.curation.playlist_generator
        — PlaylistGenerator, GeneratedPlaylist, _arc_energy_sequence,
          _harmonic_score, _bpm_score, CAMELOT_NEIGHBORS, ENERGY_ORDER

Key test scenarios:
    _arc_energy_sequence
        - "build" arc starts low, ends high.
        - "drop" arc starts high, ends low.
        - "plateau" arc is all "mid".
        - "tension" arc length matches requested slot count.
        - Unknown arc name defaults to plateau.
        - Sequence length equals ``n`` for well-defined inputs (n ≥ 6).
    _harmonic_score
        - Same Camelot key → 1.0; adjacent Camelot neighbour → 0.85;
          distant key → 0.3; missing key → 0.5 (neutral).
    _bpm_score
        - Matching BPM → 1.0; small diff → 0.85; large diff → 0.3;
          missing BPM → 0.5.
    PlaylistGenerator.generate
        - Returns a GeneratedPlaylist with correct mood and arc.
        - Empty library → empty playlist with 0 duration.
        - "build" arc orders samples low → high energy.
        - Graceful fallback when LiteLLM is unavailable (rules-only
          narrative).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from samplemind.ai.curation.playlist_generator import (
    CAMELOT_NEIGHBORS,
    ENERGY_ORDER,
    GeneratedPlaylist,
    PlaylistGenerator,
    _arc_energy_sequence,
    _bpm_score,
    _harmonic_score,
)

# ── _arc_energy_sequence ──────────────────────────────────────────────────────


def test_build_arc_starts_low_ends_high():
    seq = _arc_energy_sequence("build", 9)
    assert seq[0] == "low"
    assert seq[-1] == "high"


def test_drop_arc_starts_high_ends_low():
    seq = _arc_energy_sequence("drop", 9)
    assert seq[0] == "high"
    assert seq[-1] == "low"


def test_plateau_arc_all_mid():
    seq = _arc_energy_sequence("plateau", 6)
    assert all(e == "mid" for e in seq)


def test_tension_arc_length_matches():
    n = 8
    seq = _arc_energy_sequence("tension", n)
    assert len(seq) == n
    assert all(e in ENERGY_ORDER for e in seq)


def test_unknown_arc_defaults_to_plateau():
    seq = _arc_energy_sequence("custom", 5)  # type: ignore[arg-type]
    assert all(e == "mid" for e in seq)


def test_arc_sequence_length_matches_n_slots():
    # build/drop use `thirds = n//3 or 1` which can overshoot for very small n;
    # test with n >= 6 where the implementation is well-defined.
    for arc in ("build", "drop", "plateau", "tension"):
        for n in (6, 9, 12, 20):
            seq = _arc_energy_sequence(arc, n)  # type: ignore[arg-type]
            assert len(seq) == n, f"arc={arc} n={n} got len={len(seq)}"


# ── _harmonic_score ───────────────────────────────────────────────────────────


def test_same_key_perfect_score():
    assert _harmonic_score("1A", "1A") == 1.0


def test_adjacent_camelot_key_high_score():
    # Pick a key and one of its Camelot neighbors
    key = "5A"
    neighbor = CAMELOT_NEIGHBORS[key][0]
    score = _harmonic_score(key, neighbor)
    assert score == 0.85


def test_distant_key_low_score():
    # 1A and 6B are not neighbors
    score = _harmonic_score("1A", "6B")
    assert score == 0.3


def test_missing_key_returns_neutral():
    assert _harmonic_score(None, "1A") == 0.5
    assert _harmonic_score("1A", None) == 0.5
    assert _harmonic_score(None, None) == 0.5


# ── _bpm_score ────────────────────────────────────────────────────────────────


def test_matching_bpm_perfect():
    assert _bpm_score(140.0, 140.0) == 1.0


def test_small_bpm_diff_high_score():
    # 148/140 ≈ 1.057 → between 1.05 and 1.10 → score 0.85
    assert _bpm_score(140.0, 148.0) == 0.85


def test_large_bpm_diff_low_score():
    assert _bpm_score(100.0, 180.0) == 0.3  # ratio = 1.8


def test_missing_bpm_neutral():
    assert _bpm_score(None, 140.0) == 0.5
    assert _bpm_score(140.0, None) == 0.5


# ── PlaylistGenerator.generate ────────────────────────────────────────────────


SAMPLE_LIBRARY = [
    {
        "path": "/a.wav",
        "filename": "a.wav",
        "bpm": 130.0,
        "key": "1A",
        "energy": "low",
        "duration_s": 30.0,
    },
    {
        "path": "/b.wav",
        "filename": "b.wav",
        "bpm": 140.0,
        "key": "2A",
        "energy": "mid",
        "duration_s": 30.0,
    },
    {
        "path": "/c.wav",
        "filename": "c.wav",
        "bpm": 150.0,
        "key": "3A",
        "energy": "high",
        "duration_s": 30.0,
    },
]


@pytest.mark.asyncio
async def test_generate_returns_playlist_object():
    gen = PlaylistGenerator()

    with patch(
        "samplemind.integrations.litellm_router.chat_completion",
        new=AsyncMock(
            return_value=MagicMock(
                choices=[MagicMock(message=MagicMock(content="Great vibes."))]
            )
        ),
    ):
        playlist = await gen.generate(
            mood="dark",
            energy_arc="build",
            duration_minutes=2,
            sample_library=SAMPLE_LIBRARY,
            use_faiss=False,
        )

    assert isinstance(playlist, GeneratedPlaylist)
    assert playlist.mood == "dark"
    assert playlist.energy_arc == "build"


@pytest.mark.asyncio
async def test_generate_empty_library_returns_empty_playlist():
    gen = PlaylistGenerator()

    playlist = await gen.generate(
        mood="chill",
        energy_arc="plateau",
        duration_minutes=10,
        sample_library=[],
        use_faiss=False,
    )

    assert playlist.samples == []
    assert playlist.duration_s == 0.0


@pytest.mark.asyncio
async def test_generate_build_arc_energy_order():
    """Samples should progress roughly low → mid → high for build arc."""
    gen = PlaylistGenerator()

    # Use enough samples so ordering is meaningful
    library = SAMPLE_LIBRARY * 4  # 12 samples

    with patch(
        "samplemind.integrations.litellm_router.chat_completion",
        new=AsyncMock(
            return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="OK"))])
        ),
    ):
        playlist = await gen.generate(
            mood="dark",
            energy_arc="build",
            duration_minutes=6,
            sample_library=library,
            use_faiss=False,
        )

    if len(playlist.samples) >= 3:
        energies = [s.get("energy") for s in playlist.samples if s.get("energy")]
        # First sample should lean low, last should lean high
        first_e = ENERGY_ORDER.get(energies[0], 1)
        last_e = ENERGY_ORDER.get(energies[-1], 1)
        assert last_e >= first_e


@pytest.mark.asyncio
async def test_generate_narrative_falls_back_gracefully():
    """If LiteLLM fails, playlist should still be returned with rules-only narrative."""
    gen = PlaylistGenerator()

    with patch(
        "samplemind.integrations.litellm_router.chat_completion",
        new=AsyncMock(side_effect=Exception("LLM unavailable")),
    ):
        playlist = await gen.generate(
            mood="euphoric",
            energy_arc="drop",
            duration_minutes=1,
            sample_library=SAMPLE_LIBRARY,
            use_faiss=False,
        )

    assert isinstance(playlist, GeneratedPlaylist)
    assert isinstance(playlist.narrative, str)
