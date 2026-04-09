"""
Unit-test conftest — patches broken/unavailable imports before collection.

auto_tagger.py uses `callable | None` which is invalid on Python 3.13
because `callable` is a builtin function, not a type. Stub it out so
tests that don't exercise AutoTagger can still collect and run.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock


def _stub_module(name: str) -> MagicMock:
    """Insert a MagicMock into sys.modules under *name* (if not already present)."""
    if name not in sys.modules:
        sys.modules[name] = MagicMock()
    return sys.modules[name]


# ── Stub broken / optional heavy deps before any test file is collected ────────

# auto_tagger.py has `callable | None` which triggers TypeError on Python 3.13
_stub_module("samplemind.ai.classification.auto_tagger")

# google-genai may not be installed in CI
_stub_module("google.genai")

# faiss-cpu may not be installed in CI
_stub_module("faiss")

# transformers (CLAP model) may not be installed in CI
_stub_module("transformers")
