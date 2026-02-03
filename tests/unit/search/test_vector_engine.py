import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Mock chromadb, transformers, torch if not available or to start clean
with patch.dict(sys.modules, {
    "chromadb": MagicMock(),
    "chromadb.config": MagicMock(),
    "transformers": MagicMock(),
    "torch": MagicMock(),
    "librosa": MagicMock()
}):
    from samplemind.core.search.vector_engine import VectorSearchEngine

class TestVectorSearchEngine:

    @pytest.fixture
    def mock_deps(self):
        with patch.dict(sys.modules, {
            "chromadb": MagicMock(),
            "transformers": MagicMock(),
            "torch": MagicMock(),
            "librosa": MagicMock()
        }):
            # We need to re-import or simulate the module state where these are loaded
            # Because the module-level try/except block runs on import
            # We will patch the attributes on the VectorSearchEngine instance wrapper logic
            yield

    @patch("samplemind.core.search.vector_engine.chromadb")
    @patch("samplemind.core.search.vector_engine.ClapModel")
    @patch("samplemind.core.search.vector_engine.ClapProcessor")
    @patch("samplemind.core.search.vector_engine.torch")
    @patch("samplemind.core.search.vector_engine.librosa")
    def test_search_integration(self, mock_librosa, mock_torch, mock_proc, mock_model, mock_chroma):
        """Test the full flow with mocks"""
        engine = VectorSearchEngine(persistent_path="./test_db")

        # Setup Chroma Mock
        mock_client = MagicMock()
        mock_coll = MagicMock()
        mock_chroma.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_coll

        # Setup Model Mocks
        mock_processor_inst = MagicMock()
        mock_proc.from_pretrained.return_value = mock_processor_inst

        mock_model_inst = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_inst

        # Setup Librosa
        mock_librosa.load.return_value = (np.zeros(10), 48000)

        # Setup Embedding generation return values
        # processor returns dict of tensors
        mock_processor_inst.return_value = {"input_ids": "tensor"}

        # model returns object with .logits or .get_audio_features
        # We need to mock the outputs object
        mock_audio_outputs = MagicMock()
        # The code does outputs[0].cpu().numpy().tolist()
        # So outputs[0] should be a tensor
        mock_tensor = MagicMock()
        mock_tensor.cpu.return_value.numpy.return_value.tolist.return_value = [0.1, 0.2, 0.3]
        mock_audio_outputs.__getitem__.return_value = mock_tensor
        mock_model_inst.get_audio_features.return_value = mock_audio_outputs

        # Test Initialize
        engine.initialize_db()
        assert engine.chroma_client is not None

        # Test Indexing
        file_path = Path("kick.wav")
        engine.index_file(file_path)

        # Check if model was loaded
        mock_proc.from_pretrained.assert_called()
        mock_model.from_pretrained.assert_called()

        # Check if chroma upsert was called
        mock_coll.upsert.assert_called()
        args, kwargs = mock_coll.upsert.call_args
        assert kwargs['embeddings'] == [[0.1, 0.2, 0.3]]

        # Test Search
        # Setup text embedding return
        mock_text_outputs = MagicMock()
        mock_text_outputs.__getitem__.return_value = mock_tensor # Reuse same vector
        mock_model_inst.get_text_features.return_value = mock_text_outputs

        # Setup query result
        mock_coll.query.return_value = {
            'ids': [['id1']],
            'metadatas': [[{'path': '/abs/kick.wav', 'filename': 'kick.wav'}]],
            'distances': [[0.1]]
        }

        results = engine.search("punchy kick")

        assert len(results) == 1
        assert results[0]['filename'] == 'kick.wav'
        assert results[0]['score'] == 0.9 # 1.0 - 0.1
