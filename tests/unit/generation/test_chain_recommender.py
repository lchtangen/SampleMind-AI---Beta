from pathlib import Path
from unittest.mock import patch

import pytest

from samplemind.core.generation.chain_recommender import (
    ChainContext,
    ChainRecommender,
    ChainSlot,
)


class TestChainRecommender:

    @pytest.fixture
    def mock_library_path(self, tmp_path):
        # Create a fake library structure
        lib = tmp_path / "library"
        lib.mkdir()

        # Create some fake audio files
        (lib / "kick_01.wav").touch()
        (lib / "snare_01.wav").touch()
        (lib / "hat_01.wav").touch()
        (lib / "bass_01.mp3").touch()
        (lib / "random_file.txt").touch()

        return lib

    @pytest.fixture
    def recommender(self, mock_library_path):
        return ChainRecommender(library_path=mock_library_path)

    def test_initialization(self, recommender, mock_library_path):
        assert recommender.library_path == mock_library_path
        assert "standard_kit" in recommender.KIT_TEMPLATES

    def test_find_candidates(self, recommender, mock_library_path):
        # Test finding snares
        slot = ChainSlot("Snare", ["snare", "clap"])
        candidates = recommender._find_candidates(slot, [mock_library_path])

        assert len(candidates) == 1
        assert candidates[0].name == "snare_01.wav"

        # Test finding hats
        slot_hat = ChainSlot("Hat", ["hat"])
        candidates_hat = recommender._find_candidates(slot_hat, [mock_library_path])
        assert len(candidates_hat) == 1
        assert candidates_hat[0].name == "hat_01.wav"

    def test_build_chain_simple(self, recommender, mock_library_path):
        # Seed is the kick
        seed = mock_library_path / "kick_01.wav"

        # We need to ensure _pick_best_candidate works or is mocked if we want deterministic results
        # But for now the simple implementation just picks random, which is fine since we have only 1 of each

        chain = recommender.build_chain(
            seed_sample=seed,
            template_name="standard_kit",
            search_paths=[mock_library_path]
        )

        # Standard kit has 4 slots: Kick, Snare, Hat, Perc
        # Perc might be missing in our fake library?
        # Our fake library has: kick, snare, hat, bass.
        # "standard_kit" defines Perc keywords: ["perc", "tom", ...]. None match "bass".
        # So we expect Kick(Seed) + Snare + Hat. Perc will be skipped.

        assert len(chain.nodes) == 3 # Kick + Snare + Hat

        node_names = [n.slot_name for n in chain.nodes]
        assert "Kick" in node_names
        assert "Snare" in node_names
        assert "HiHat" in node_names
        assert "Perc" not in node_names

    @patch("samplemind.core.generation.chain_recommender.random.choice")
    def test_pick_best_candidate(self, mock_choice, recommender):
        candidates = [Path("a.wav"), Path("b.wav")]
        mock_choice.return_value = Path("a.wav")

        context = ChainContext(Path("seed.wav"))
        slot = ChainSlot("Test", ["test"])

        node = recommender._pick_best_candidate(candidates, context, slot, 0.5)

        assert node is not None
        assert node.file_path == Path("a.wav")
        assert node.slot_name == "Test"
