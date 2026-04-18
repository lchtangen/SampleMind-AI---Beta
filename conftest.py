"""
Root-level pytest conftest — loaded BEFORE any test-directory conftest.py.

Purpose:
    Stub out heavy or optional dependencies that are not installed in every
    environment (e.g. CI runners without GPU libraries) so that ``import``
    chains don't blow up with ``ImportError`` before tests even start.

Stubs registered here:
    • google.genai        — Google GenAI SDK (used by google_ai_integration.py)
    • faiss               — Facebook AI Similarity Search (optional ML dep)
    • transformers        — Hugging Face Transformers (optional ML dep)
    • samplemind.ai.classification.auto_tagger — uses ``callable | None``
      union syntax that is invalid at runtime on Python 3.13

If you add a new optional heavy dependency, register it here with ``_stub()``.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock


def _stub(name: str) -> MagicMock:
    """Register a MagicMock under *name* in sys.modules if not already present."""
    if name not in sys.modules:
        m = MagicMock()
        sys.modules[name] = m
    return sys.modules[name]


# google-genai (google_ai_integration.py imports `from google import genai`)
google_mod = sys.modules.get("google") or MagicMock()
google_mod.genai = MagicMock()  # type: ignore[attr-defined]
sys.modules.setdefault("google", google_mod)
_stub("google.genai")

# auto_tagger uses `callable | None` annotation — invalid at runtime on Py 3.13
_stub("samplemind.ai.classification.auto_tagger")

# Optional heavy ML deps
_stub("faiss")
_stub("transformers")
