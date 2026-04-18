"""Tests for SmartAutoCategorizer."""

from __future__ import annotations

import numpy as np
import pytest

from samplemind.core.library.auto_categorizer import (
    CATEGORIES,
    CategoryResult,
    SmartAutoCategorizer,
)


class TestSmartAutoCategorizer:
    """Tests for SmartAutoCategorizer."""

    def test_init(self) -> None:
        categorizer = SmartAutoCategorizer()
        assert len(categorizer._compiled_patterns) > 0

    def test_categorize_by_filename_kick(self) -> None:
        categorizer = SmartAutoCategorizer()
        y = np.zeros(22050, dtype=np.float32)
        result = categorizer.categorize(y, 22050, filename="dark_trap_kick_808.wav")
        assert isinstance(result, CategoryResult)
        assert result.category == "drums" or result.category == "bass"

    def test_categorize_by_filename_snare(self) -> None:
        categorizer = SmartAutoCategorizer()
        y = np.zeros(22050, dtype=np.float32)
        result = categorizer.categorize(y, 22050, filename="punchy_snare_v2.wav")
        assert result.category == "drums"
        assert result.subcategory == "snare"

    def test_categorize_by_filename_pad(self) -> None:
        categorizer = SmartAutoCategorizer()
        y = np.zeros(22050, dtype=np.float32)
        result = categorizer.categorize(y, 22050, filename="warm_pad_c_minor.wav")
        assert result.category == "melodic"
        assert result.subcategory == "pad"

    def test_categorize_by_filename_hihat(self) -> None:
        categorizer = SmartAutoCategorizer()
        y = np.zeros(22050, dtype=np.float32)
        result = categorizer.categorize(y, 22050, filename="closed_hihat_tight.wav")
        assert result.category == "drums"

    def test_categorize_unknown(self) -> None:
        categorizer = SmartAutoCategorizer()
        y = np.zeros(22050, dtype=np.float32)
        result = categorizer.categorize(y, 22050, filename="random_name_xyz.wav")
        assert isinstance(result, CategoryResult)

    def test_categorize_no_filename(self) -> None:
        categorizer = SmartAutoCategorizer()
        y = np.zeros(22050, dtype=np.float32)
        result = categorizer.categorize(y, 22050)
        assert isinstance(result, CategoryResult)

    def test_confidence_range(self) -> None:
        categorizer = SmartAutoCategorizer()
        y = np.zeros(22050, dtype=np.float32)
        result = categorizer.categorize(y, 22050, filename="kick.wav")
        assert 0.0 <= result.confidence <= 1.0

    def test_tags_not_empty_for_known(self) -> None:
        categorizer = SmartAutoCategorizer()
        y = np.zeros(22050, dtype=np.float32)
        result = categorizer.categorize(y, 22050, filename="bright_snare_loop.wav")
        assert len(result.tags) > 0

    def test_suggested_path(self) -> None:
        categorizer = SmartAutoCategorizer()
        y = np.zeros(22050, dtype=np.float32)
        result = categorizer.categorize(y, 22050, filename="kick.wav")
        assert result.suggested_path != ""
        assert "/" in result.suggested_path or result.suggested_path == "Unsorted"

    def test_to_dict(self) -> None:
        result = CategoryResult(
            category="drums",
            subcategory="kick",
            confidence=0.75,
        )
        d = result.to_dict()
        assert d["category"] == "drums"
        assert d["subcategory"] == "kick"
        assert d["confidence"] == 0.75

    def test_energy_levels(self) -> None:
        categorizer = SmartAutoCategorizer()
        # Low energy signal
        y = np.zeros(22050, dtype=np.float32) + 0.001
        result = categorizer.categorize(y, 22050)
        assert result.energy_level in ("low", "mid", "high")

    def test_character_detection_from_filename(self) -> None:
        categorizer = SmartAutoCategorizer()
        y = np.zeros(22050, dtype=np.float32)
        result = categorizer.categorize(y, 22050, filename="dark_vintage_kick.wav")
        assert any(tag in result.character for tag in ["dark", "vintage"])

    def test_categories_structure(self) -> None:
        """Ensure CATEGORIES taxonomy is valid."""
        assert "drums" in CATEGORIES
        assert "bass" in CATEGORIES
        assert "melodic" in CATEGORIES
        assert "vocal" in CATEGORIES
        assert "fx" in CATEGORIES
        for cat, subcats in CATEGORIES.items():
            assert isinstance(subcats, list)
            assert len(subcats) > 0
