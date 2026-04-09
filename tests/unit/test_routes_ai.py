"""
Unit tests for samplemind.interfaces.api.routes.ai

All heavy deps (FAISS, LiteLLM, PlaylistGenerator, GapAnalyzer) are mocked
so the tests run in any CI environment without GPU or audio fixtures.

Note: PlaylistGenerator, get_index, GapAnalyzer are imported INSIDE function
bodies in routes/ai.py, so they must be patched at their source modules,
not in the routes.ai namespace.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from samplemind.interfaces.api.routes.ai import router


# ---------------------------------------------------------------------------
# Test app fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/ai")
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /ai/providers
# ---------------------------------------------------------------------------


def test_list_providers_no_manager(client: TestClient):
    """When ai_manager is not in app state, returns empty list."""
    with patch(
        "samplemind.interfaces.api.routes.ai.get_app_state",
        return_value=None,
    ):
        resp = client.get("/ai/providers")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_providers_with_manager(client: TestClient):
    """Returns provider list when ai_manager is present."""
    mock_manager = MagicMock()
    mock_manager.get_available_providers.return_value = []
    mock_manager.get_global_stats.return_value = {"provider_usage": {}}

    with patch(
        "samplemind.interfaces.api.routes.ai.get_app_state",
        return_value=mock_manager,
    ):
        resp = client.get("/ai/providers")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    statuses = {p["name"]: p["status"] for p in data}
    assert all(v in ("available", "unavailable") for v in statuses.values())


# ---------------------------------------------------------------------------
# POST /ai/curate/playlist
# ---------------------------------------------------------------------------


def test_generate_playlist_success(client: TestClient):
    """POST /curate/playlist returns PlaylistResponse on success."""
    mock_playlist = MagicMock()
    mock_playlist.name = "Dark Build"
    mock_playlist.mood = "dark"
    mock_playlist.energy_arc = "build"
    mock_playlist.duration_s = 120.0
    mock_playlist.samples = []
    mock_playlist.narrative = "Rising tension."
    mock_playlist.model_used = "rules"

    # PlaylistGenerator is a LOCAL import inside generate_playlist() body.
    # Patch via sys.modules so that `from ... import PlaylistGenerator` inside
    # the route handler resolves to our mock.
    import sys
    fake_gen_module = MagicMock()
    fake_gen_module.PlaylistGenerator.return_value.generate = AsyncMock(
        return_value=mock_playlist
    )
    with patch.dict(
        sys.modules,
        {"samplemind.ai.curation.playlist_generator": fake_gen_module},
    ):
        resp = client.post(
            "/ai/curate/playlist",
            json={"mood": "dark", "energy_arc": "build", "duration_minutes": 2.0},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["mood"] == "dark"
    assert body["energy_arc"] == "build"
    assert body["narrative"] == "Rising tension."


def test_generate_playlist_generator_error(client: TestClient):
    """POST /curate/playlist → 500 when generator raises."""
    import sys
    fake_gen_module = MagicMock()
    fake_gen_module.PlaylistGenerator.return_value.generate = AsyncMock(
        side_effect=RuntimeError("boom")
    )
    with patch.dict(
        sys.modules,
        {"samplemind.ai.curation.playlist_generator": fake_gen_module},
    ):
        resp = client.post("/ai/curate/playlist", json={"mood": "chill"})

    assert resp.status_code == 500
    # Route catches RuntimeError in generic handler → detail is "Internal server error"
    assert "internal server error" in resp.json()["detail"].lower()


def test_generate_playlist_defaults(client: TestClient):
    """PlaylistRequest defaults: mood=dark, energy_arc=build, duration=30."""
    mock_playlist = MagicMock()
    mock_playlist.name = "Default"
    mock_playlist.mood = "dark"
    mock_playlist.energy_arc = "build"
    mock_playlist.duration_s = 1800.0
    mock_playlist.samples = []
    mock_playlist.narrative = ""
    mock_playlist.model_used = "rules"

    import sys
    fake_gen_module = MagicMock()
    fake_gen_module.PlaylistGenerator.return_value.generate = AsyncMock(
        return_value=mock_playlist
    )
    with patch.dict(
        sys.modules,
        {"samplemind.ai.curation.playlist_generator": fake_gen_module},
    ):
        resp = client.post("/ai/curate/playlist", json={})

    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /ai/curate/gaps
# ---------------------------------------------------------------------------


def test_curate_gaps_empty_index(client: TestClient):
    """Returns 0-gap response when FAISS index is empty."""
    mock_idx = MagicMock()
    mock_idx.is_empty = True

    import sys
    fake_faiss_mod = MagicMock()
    fake_faiss_mod.get_index.return_value = mock_idx
    with patch.dict(
        sys.modules,
        {"samplemind.core.search.faiss_index": fake_faiss_mod},
    ):
        resp = client.get("/ai/curate/gaps")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total_samples"] == 0
    assert body["gap_count"] == 0
    assert body["model_used"] == "rules"
    assert any("index rebuild" in s.lower() for s in body["suggestions"])


def test_curate_gaps_with_samples(client: TestClient):
    """Returns gap report when index has samples."""
    mock_entry = MagicMock(
        filename="kick.wav",
        path="/kick.wav",
        bpm=140.0,
        key="1A",
        energy="high",
        genre_labels=["trap"],
        mood_labels=["dark"],
    )
    mock_idx = MagicMock()
    mock_idx.is_empty = False
    mock_idx._entries = [mock_entry]

    mock_report = MagicMock(
        total_samples=1,
        coverage_score=0.4,
        gaps=[],
        suggestions=["Add more chill samples"],
        summary="Library needs diversity.",
        model_used="rules",
    )

    import sys
    fake_faiss_mod = MagicMock()
    fake_faiss_mod.get_index.return_value = mock_idx
    fake_gap_mod = MagicMock()
    fake_gap_mod.GapAnalyzer.return_value.analyze = AsyncMock(return_value=mock_report)

    with patch.dict(
        sys.modules,
        {
            "samplemind.core.search.faiss_index": fake_faiss_mod,
            "samplemind.ai.curation.gap_analyzer": fake_gap_mod,
        },
    ):
        resp = client.get("/ai/curate/gaps")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total_samples"] == 1
    assert body["coverage_score"] == pytest.approx(0.4)


def test_curate_gaps_analyzer_error(client: TestClient):
    """Returns 500 when GapAnalyzer raises."""
    mock_idx = MagicMock()
    mock_idx.is_empty = False
    mock_idx._entries = [MagicMock(filename="a.wav", path="/a.wav")]

    import sys
    fake_faiss_mod = MagicMock()
    fake_faiss_mod.get_index.return_value = mock_idx
    fake_gap_mod = MagicMock()
    fake_gap_mod.GapAnalyzer.return_value.analyze = AsyncMock(
        side_effect=RuntimeError("analyzer down")
    )

    with patch.dict(
        sys.modules,
        {
            "samplemind.core.search.faiss_index": fake_faiss_mod,
            "samplemind.ai.curation.gap_analyzer": fake_gap_mod,
        },
    ):
        resp = client.get("/ai/curate/gaps")

    assert resp.status_code == 500


# ---------------------------------------------------------------------------
# POST /ai/curate/energy-arc
# ---------------------------------------------------------------------------


def test_energy_arc_no_matching_samples(client: TestClient):
    """Unknown sample IDs → empty ordered list + plateau arc."""
    mock_idx = MagicMock()
    mock_idx._entries = []

    import sys
    fake_faiss_mod = MagicMock()
    fake_faiss_mod.get_index.return_value = mock_idx
    with patch.dict(
        sys.modules,
        {"samplemind.core.search.faiss_index": fake_faiss_mod},
    ):
        resp = client.post("/ai/curate/energy-arc", json=["unknown-id"])

    assert resp.status_code == 200
    body = resp.json()
    assert body["ordered"] == []
    assert body["suggested_arc"] == "plateau"


def test_energy_arc_orders_samples(client: TestClient):
    """Known sample IDs are ordered by arc."""
    entries = [
        MagicMock(path="/a.wav", filename="a.wav", bpm=130.0, key="1A", energy="low"),
        MagicMock(path="/b.wav", filename="b.wav", bpm=140.0, key="2A", energy="high"),
    ]
    mock_idx = MagicMock()
    mock_idx._entries = entries

    ordered_result = [
        {"filename": "a.wav", "energy": "low"},
        {"filename": "b.wav", "energy": "high"},
    ]

    import sys
    fake_faiss_mod = MagicMock()
    fake_faiss_mod.get_index.return_value = mock_idx
    fake_gen_mod = MagicMock()
    fake_gen_mod.PlaylistGenerator.return_value._order_by_arc.return_value = (
        ordered_result
    )

    with patch.dict(
        sys.modules,
        {
            "samplemind.core.search.faiss_index": fake_faiss_mod,
            "samplemind.ai.curation.playlist_generator": fake_gen_mod,
        },
    ):
        resp = client.post("/ai/curate/energy-arc", json=["/a.wav", "/b.wav"])

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["ordered"]) == 2
