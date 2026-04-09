"""
Analytics Routes — SampleMind Phase 14

Plotly-based library analytics endpoints for BPM histograms, key heatmaps,
genre breakdowns, and usage growth charts.

All endpoints return Plotly-compatible JSON (plotly.graph_objs format)
for direct rendering in the web UI or TUI.

Endpoints:
  GET /api/v1/analytics/bpm-histogram     — BPM distribution bar chart
  GET /api/v1/analytics/key-heatmap       — Key/mode heatmap
  GET /api/v1/analytics/genre-breakdown   — Genre pie/bar chart
  GET /api/v1/analytics/energy-breakdown  — Energy level pie chart
  GET /api/v1/analytics/summary           — High-level library stats
"""

from __future__ import annotations

import logging
from collections import Counter

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


def _get_samples_from_index(limit: int = 5000) -> list[dict]:
    """Load sample metadata from FAISS index (fast, in-memory)."""
    try:
        from samplemind.core.search.faiss_index import get_index

        idx = get_index()
        return [
            {
                "filename": e.filename,
                "bpm": e.bpm,
                "key": e.key,
                "energy": e.energy,
                "genre_labels": e.genre_labels,
                "mood_labels": e.mood_labels,
            }
            for e in idx._entries[:limit]
        ]
    except Exception as exc:
        logger.warning("Could not load FAISS index for analytics: %s", exc)
        return []


@router.get("/bpm-histogram")
async def bpm_histogram(bins: int = 20) -> JSONResponse:
    """
    BPM distribution histogram.

    Returns Plotly bar chart JSON with BPM buckets on x-axis and count on y-axis.
    """
    samples = _get_samples_from_index()
    bpms = [s["bpm"] for s in samples if s.get("bpm") and 30 <= s["bpm"] <= 250]

    if not bpms:
        return JSONResponse({"data": [], "layout": {"title": "No BPM data available"}})

    try:
        import numpy as np

        counts, edges = np.histogram(bpms, bins=bins, range=(30, 250))
        bin_labels = [f"{int(edges[i])}-{int(edges[i+1])}" for i in range(len(edges) - 1)]

        chart = {
            "data": [
                {
                    "type": "bar",
                    "x": bin_labels,
                    "y": counts.tolist(),
                    "marker": {"color": "#6366f1"},
                    "name": "Samples",
                }
            ],
            "layout": {
                "title": f"BPM Distribution ({len(bpms)} samples)",
                "xaxis": {"title": "BPM Range"},
                "yaxis": {"title": "Count"},
                "bargap": 0.05,
                "template": "plotly_dark",
            },
        }
        return JSONResponse(chart)
    except ImportError:
        # Fallback without numpy
        bpm_ints = [int(b // 10) * 10 for b in bpms]
        counts_dict = Counter(bpm_ints)
        sorted_keys = sorted(counts_dict.keys())
        chart = {
            "data": [
                {
                    "type": "bar",
                    "x": [str(k) for k in sorted_keys],
                    "y": [counts_dict[k] for k in sorted_keys],
                    "marker": {"color": "#6366f1"},
                }
            ],
            "layout": {"title": "BPM Distribution", "template": "plotly_dark"},
        }
        return JSONResponse(chart)


@router.get("/key-heatmap")
async def key_heatmap() -> JSONResponse:
    """
    Musical key usage heatmap.

    Returns Plotly heatmap with keys on x-axis and major/minor on y-axis.
    """
    samples = _get_samples_from_index()
    key_counts: Counter = Counter()
    for s in samples:
        if s.get("key"):
            key_counts[s["key"]] += 1

    if not key_counts:
        return JSONResponse({"data": [], "layout": {"title": "No key data available"}})

    # Separate major / minor
    note_order = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    major_counts = [key_counts.get(n, 0) for n in note_order]
    minor_counts = [key_counts.get(f"{n}m", 0) for n in note_order]

    chart = {
        "data": [
            {
                "type": "heatmap",
                "z": [major_counts, minor_counts],
                "x": note_order,
                "y": ["Major", "Minor"],
                "colorscale": "Viridis",
                "showscale": True,
            }
        ],
        "layout": {
            "title": f"Key Distribution ({sum(key_counts.values())} samples)",
            "xaxis": {"title": "Key"},
            "yaxis": {"title": "Mode"},
            "template": "plotly_dark",
        },
    }
    return JSONResponse(chart)


@router.get("/genre-breakdown")
async def genre_breakdown(top_n: int = 20) -> JSONResponse:
    """
    Top genre label distribution as a horizontal bar chart.
    """
    samples = _get_samples_from_index()
    genre_counter: Counter = Counter()
    for s in samples:
        for genre in s.get("genre_labels") or []:
            genre_counter[genre] += 1

    if not genre_counter:
        return JSONResponse({"data": [], "layout": {"title": "No genre data available"}})

    top = genre_counter.most_common(top_n)
    labels = [g for g, _ in top]
    values = [c for _, c in top]

    chart = {
        "data": [
            {
                "type": "bar",
                "x": values,
                "y": labels,
                "orientation": "h",
                "marker": {"color": "#a78bfa"},
            }
        ],
        "layout": {
            "title": f"Top {top_n} Genres ({len(genre_counter)} unique)",
            "xaxis": {"title": "Count"},
            "yaxis": {"autorange": "reversed"},
            "template": "plotly_dark",
        },
    }
    return JSONResponse(chart)


@router.get("/energy-breakdown")
async def energy_breakdown() -> JSONResponse:
    """
    Energy level distribution as a pie chart.
    """
    samples = _get_samples_from_index()
    energy_counts = Counter(
        (s.get("energy") or "unknown").lower() for s in samples
    )

    if not energy_counts:
        return JSONResponse({"data": [], "layout": {"title": "No energy data available"}})

    labels = list(energy_counts.keys())
    values = list(energy_counts.values())
    colors = {"low": "#60a5fa", "mid": "#34d399", "high": "#f87171", "unknown": "#94a3b8"}

    chart = {
        "data": [
            {
                "type": "pie",
                "labels": labels,
                "values": values,
                "marker": {"colors": [colors.get(l, "#94a3b8") for l in labels]},
                "hole": 0.4,
            }
        ],
        "layout": {
            "title": f"Energy Distribution ({sum(values)} samples)",
            "template": "plotly_dark",
        },
    }
    return JSONResponse(chart)


@router.get("/summary")
async def library_summary() -> JSONResponse:
    """
    High-level library statistics summary.

    Returns key metrics without chart data for quick display in dashboards.
    """
    samples = _get_samples_from_index()
    n = len(samples)

    if n == 0:
        return JSONResponse({
            "total_samples": 0,
            "indexed": False,
            "message": "Run `samplemind index rebuild` to index your library.",
        })

    bpms = [s["bpm"] for s in samples if s.get("bpm")]
    energy_counts = Counter((s.get("energy") or "unknown").lower() for s in samples)
    genre_counter: Counter = Counter()
    for s in samples:
        for g in s.get("genre_labels") or []:
            genre_counter[g] += 1

    top_genres = [g for g, _ in genre_counter.most_common(5)]
    keys = [s["key"] for s in samples if s.get("key")]
    key_counter = Counter(keys)
    top_keys = [k for k, _ in key_counter.most_common(5)]

    return JSONResponse({
        "total_samples": n,
        "indexed": True,
        "bpm": {
            "min": min(bpms) if bpms else None,
            "max": max(bpms) if bpms else None,
            "avg": round(sum(bpms) / len(bpms), 1) if bpms else None,
        },
        "energy_distribution": {
            "low": energy_counts.get("low", 0),
            "mid": energy_counts.get("mid", 0),
            "high": energy_counts.get("high", 0),
        },
        "top_genres": top_genres,
        "top_keys": top_keys,
        "unique_keys": len(key_counter),
        "unique_genres": len(genre_counter),
    })
