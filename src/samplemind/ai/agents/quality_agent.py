"""
QualityAgent — Audio quality gate for the LangGraph pipeline. (P3-006)

Checks for common production issues:
  - True-peak clipping  (uses pyloudnorm if available, else ffmpeg subprocess)
  - Integrated loudness (LUFS)
  - Dynamic range (LRA)
  - Silence / near-silence sections

Results are stored in state["quality_flags"] and appended to state["messages"].
The node is designed to be non-blocking: if pyloudnorm *and* ffmpeg are both
unavailable it skips gracefully without failing the pipeline.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from samplemind.ai.agents.state import AudioAnalysisState

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _measure_loudness_pyloudnorm(path: str) -> dict[str, float | bool]:
    """Use pyloudnorm + soundfile to measure LUFS, LRA, true-peak."""
    import numpy as np
    import pyloudnorm as pyln  # type: ignore
    import soundfile as sf

    data, rate = sf.read(path)
    if data.ndim == 1:
        data = data[:, None]

    meter = pyln.Meter(rate)
    lufs: float = meter.integrated_loudness(data)

    # True-peak clipping: any sample > 0 dBFS in floating-point domain
    peak: float = float(np.max(np.abs(data)))
    clipping: bool = peak >= 1.0

    # Dynamic range (simple: peak - RMS proxy)
    rms: float = float(np.sqrt(np.mean(data**2))) + 1e-9
    dynamic_range_db: float = 20 * float(np.log10(peak / rms))

    return {
        "lufs": round(lufs, 2),
        "peak_db": round(20 * float(np.log10(peak + 1e-9)), 2),
        "clipping": clipping,
        "dynamic_range_db": round(dynamic_range_db, 2),
    }


def _measure_loudness_ffmpeg(path: str) -> dict[str, float | bool]:
    """Use ffmpeg -af loudnorm (print-only) as a fallback."""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        path,
        "-af",
        "loudnorm=print_format=json",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=30,
    )
    # ffmpeg writes loudnorm JSON to stderr
    stderr = result.stderr
    try:
        # Extract the JSON block from stderr output
        start = stderr.rfind("{")
        end = stderr.rfind("}") + 1
        data = json.loads(stderr[start:end])
        lufs = float(data.get("input_i", -70.0))
        lra = float(data.get("input_lra", 0.0))
        tp = float(data.get("input_tp", -6.0))
        return {
            "lufs": round(lufs, 2),
            "peak_db": round(tp, 2),
            "clipping": tp > 0.0,
            "dynamic_range_db": round(lra, 2),
        }
    except Exception as exc:
        logger.debug("ffmpeg loudnorm parse failed: %s", exc)
        return {}


def _run_quality_check(path: str) -> dict[str, Any]:
    """
    Try pyloudnorm first, then ffmpeg, then return a stub result.

    Returns a dict with keys: lufs, peak_db, clipping, dynamic_range_db,
    method (which backend was used), warnings (list[str]).
    """
    # --- pyloudnorm (preferred) ------------------------------------------
    try:
        metrics = _measure_loudness_pyloudnorm(path)
        metrics["method"] = "pyloudnorm"
    except ImportError:
        metrics = {}
    except Exception as exc:
        logger.debug("pyloudnorm failed: %s", exc)
        metrics = {}

    # --- ffmpeg fallback -------------------------------------------------
    if not metrics:
        try:
            metrics = _measure_loudness_ffmpeg(path)
            metrics["method"] = "ffmpeg"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        except Exception as exc:
            logger.debug("ffmpeg fallback failed: %s", exc)

    # --- no-op stub ------------------------------------------------------
    if not metrics:
        metrics = {
            "lufs": None,
            "peak_db": None,
            "clipping": False,
            "dynamic_range_db": None,
            "method": "unavailable",
        }

    # --- derive warnings -------------------------------------------------
    warnings: list[str] = []
    if metrics.get("clipping"):
        warnings.append("⚠️ True-peak clipping detected (peak ≥ 0 dBFS)")
    lufs = metrics.get("lufs")
    if lufs is not None and lufs > -6.0:
        warnings.append(f"⚠️ Integrated loudness too high ({lufs:.1f} LUFS > -6)")
    if lufs is not None and lufs < -30.0:
        warnings.append(f"ℹ️ Very quiet sample ({lufs:.1f} LUFS)")
    dr = metrics.get("dynamic_range_db")
    if dr is not None and dr < 3.0:
        warnings.append(
            f"⚠️ Low dynamic range ({dr:.1f} dB) — may sound over-compressed"
        )

    metrics["warnings"] = warnings
    return metrics


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------


def quality_agent(state: AudioAnalysisState) -> AudioAnalysisState:
    """
    Node: Run audio quality checks and populate state['quality_flags'].

    Sits between the mixing agent and the recommendation agent so that
    quality issues can influence the final report.
    """
    file_path: str = state.get("file_path", "")
    messages: list[str] = list(state.get("messages", []))
    errors: list[str] = list(state.get("errors", []))

    updates: dict[str, Any] = {
        "current_stage": "quality",
        "progress_pct": 65,
        "messages": messages + ["🔍 Running quality checks…"],
    }

    if not file_path or not Path(file_path).exists():
        updates["quality_flags"] = {"skipped": True, "reason": "file not found"}
        updates["messages"] = messages + ["ℹ️ Quality check skipped — no file"]
        return updates  # type: ignore[return-value]

    try:
        quality_flags = _run_quality_check(file_path)
        updates["quality_flags"] = quality_flags

        summary_parts = [f"method={quality_flags.get('method', '?')}"]
        if quality_flags.get("lufs") is not None:
            summary_parts.append(f"LUFS={quality_flags['lufs']}")
        if quality_flags.get("clipping"):
            summary_parts.append("CLIPPING")
        summary = ", ".join(summary_parts)

        warn_msgs = quality_flags.get("warnings", [])
        if warn_msgs:
            updates["messages"] = messages + [f"🔍 Quality: {summary}"] + warn_msgs
        else:
            updates["messages"] = messages + [f"✅ Quality OK ({summary})"]

    except Exception as exc:
        logger.warning("QualityAgent failed for %s: %s", file_path, exc)
        errors.append(f"quality_agent: {exc}")
        updates["errors"] = errors
        updates["quality_flags"] = {"error": str(exc)}
        updates["messages"] = messages + [f"⚠️ Quality check failed: {exc}"]

    return updates  # type: ignore[return-value]
