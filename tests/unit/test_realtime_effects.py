"""
Tests for RealtimeEffectsChain (P1-014)

Tests the pedalboard-based effects chain with mocked pedalboard imports.
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from samplemind.core.processing.realtime_effects import (
    EFFECT_DEFAULTS,
    EffectSlot,
    ProcessingResult,
    RealtimeEffectsChain,
)


class TestEffectSlot:
    def test_defaults(self):
        slot = EffectSlot(name="reverb")
        assert slot.enabled is True
        assert slot.params == {}

    def test_to_dict(self):
        slot = EffectSlot(name="compressor", params={"threshold_db": -20})
        d = slot.to_dict()
        assert d["name"] == "compressor"
        assert d["params"]["threshold_db"] == -20


class TestEffectDefaults:
    def test_all_effects_have_defaults(self):
        expected = {
            "eq",
            "compressor",
            "reverb",
            "delay",
            "chorus",
            "distortion",
            "limiter",
            "gain",
            "highpass",
            "lowpass",
        }
        assert set(EFFECT_DEFAULTS.keys()) == expected

    def test_compressor_defaults(self):
        d = EFFECT_DEFAULTS["compressor"]
        assert d["threshold_db"] == -20.0
        assert d["ratio"] == 4.0

    def test_reverb_defaults(self):
        d = EFFECT_DEFAULTS["reverb"]
        assert d["room_size"] == 0.5
        assert d["wet_level"] == 0.3


class TestRealtimeEffectsChain:
    def test_init(self):
        chain = RealtimeEffectsChain()
        assert chain.effects == []

    def test_add_effect(self):
        chain = RealtimeEffectsChain()
        slot = chain.add_effect("compressor", threshold_db=-15)
        assert slot.name == "compressor"
        assert slot.params["threshold_db"] == -15
        assert len(chain.effects) == 1

    def test_add_multiple_effects(self):
        chain = RealtimeEffectsChain()
        chain.add_effect("compressor")
        chain.add_effect("reverb")
        chain.add_effect("limiter")
        assert len(chain.effects) == 3

    def test_remove_effect(self):
        chain = RealtimeEffectsChain()
        chain.add_effect("compressor")
        chain.add_effect("reverb")
        removed = chain.remove_effect(0)
        assert removed.name == "compressor"
        assert len(chain.effects) == 1
        assert chain.effects[0].name == "reverb"

    def test_remove_invalid_index(self):
        chain = RealtimeEffectsChain()
        assert chain.remove_effect(5) is None

    def test_move_effect(self):
        chain = RealtimeEffectsChain()
        chain.add_effect("compressor")
        chain.add_effect("reverb")
        chain.add_effect("limiter")
        assert chain.move_effect(0, 2)
        assert chain.effects[0].name == "reverb"

    def test_toggle_effect(self):
        chain = RealtimeEffectsChain()
        chain.add_effect("compressor")
        assert chain.effects[0].enabled is True
        chain.toggle_effect(0)
        assert chain.effects[0].enabled is False
        chain.toggle_effect(0)
        assert chain.effects[0].enabled is True

    def test_update_params(self):
        chain = RealtimeEffectsChain()
        chain.add_effect("compressor")
        chain.update_params(0, threshold_db=-30, ratio=8)
        assert chain.effects[0].params["threshold_db"] == -30
        assert chain.effects[0].params["ratio"] == 8

    def test_clear(self):
        chain = RealtimeEffectsChain()
        chain.add_effect("compressor")
        chain.add_effect("reverb")
        chain.clear()
        assert len(chain.effects) == 0

    def test_to_dict(self):
        chain = RealtimeEffectsChain()
        chain.add_effect("compressor", threshold_db=-20)
        chain.add_effect("reverb", room_size=0.8)
        data = chain.to_dict()
        assert len(data) == 2
        assert data[0]["name"] == "compressor"
        assert data[1]["name"] == "reverb"

    def test_from_dict(self):
        data = [
            {"name": "compressor", "enabled": True, "params": {"threshold_db": -20}},
            {"name": "reverb", "enabled": False, "params": {"room_size": 0.8}},
        ]
        chain = RealtimeEffectsChain.from_dict(data)
        assert len(chain.effects) == 2
        assert chain.effects[0].name == "compressor"
        assert chain.effects[1].enabled is False

    def test_roundtrip_serialisation(self):
        chain = RealtimeEffectsChain()
        chain.add_effect("compressor", threshold_db=-15)
        chain.add_effect("reverb", room_size=0.6)
        chain.add_effect("limiter")
        data = chain.to_dict()

        restored = RealtimeEffectsChain.from_dict(data)
        assert len(restored.effects) == 3
        assert restored.effects[0].params["threshold_db"] == -15

    def test_available_effects(self):
        effects = RealtimeEffectsChain.available_effects()
        assert "compressor" in effects
        assert "reverb" in effects
        assert len(effects) == 10

    def test_process_buffer_passthrough(self):
        """Without pedalboard, buffer should pass through."""
        chain = RealtimeEffectsChain()
        chain._pedalboard_available = False
        audio = np.ones(1000, dtype=np.float32) * 0.5
        result = chain.process_buffer(audio, 44100)
        np.testing.assert_array_equal(result, audio)

    def test_process_buffer_no_effects(self):
        """Empty chain should pass through."""
        chain = RealtimeEffectsChain()
        chain._pedalboard_available = False
        audio = np.random.randn(1000).astype(np.float32)
        result = chain.process_buffer(audio, 44100)
        np.testing.assert_array_equal(result, audio)
