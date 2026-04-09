"""
Root conftest — stubs broken/optional heavy dependencies BEFORE any
test-directory conftest.py is imported.

This prevents ImportError cascade from:
  • google-genai  — not installed in base CI
  • faiss-cpu     — optional ML dep
  • transformers  — optional ML dep
  • auto_tagger   — uses `callable | None` (invalid on Python 3.13)
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
