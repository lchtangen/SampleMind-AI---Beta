from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

# Ensure we can import the module.
# We assume dependencies are installed or we handle the ImportError case inside the module.
from samplemind.core.search.vector_engine import VectorSearchEngine


class TestVectorSearchEngine:

    @patch("samplemind.core.search.vector_engine.chromadb")
    @patch("samplemind.core.search.vector_engine.ClapModel")
    @patch("samplemind.core.search.vector_engine.ClapProcessor")
    @patch("samplemind.core.search.vector_engine.torch")
    @patch("samplemind.core.search.vector_engine.librosa")
    def test_search_integration(self, mock_librosa, mock_torch, mock_proc_cls, mock_model_cls, mock_chroma):
        """Test the full flow with mocks"""

        # Setup Chroma Mock
        mock_client = MagicMock()
        mock_coll = MagicMock()
        mock_chroma.PersistentClient.return_value = mock_client
        mock_client.get_or_create_collection.return_value = mock_coll

        # Setup Model Mocks
        # ClapProcessor.from_pretrained() returns a processor instance
        mock_processor_inst = MagicMock()
        mock_proc_cls.from_pretrained.return_value = mock_processor_inst

        # ClapModel.from_pretrained() returns a model instance
        mock_model_inst = MagicMock()
        mock_model_cls.from_pretrained.return_value = mock_model_inst
        mock_model_inst.to.return_value = mock_model_inst # handle .to(device)

        # Setup Librosa
        # librosa.load returns (audio, sr)
        mock_librosa.load.return_value = (np.zeros(10), 48000)

        # Setup Embedding generation return values
        # processor(...) returns an object that has .to(), which returns a dict (inputs)
        mock_inputs = {"input_ids": MagicMock()}
        mock_processor_output = MagicMock()
        mock_processor_output.to.return_value = mock_inputs
        mock_processor_inst.return_value = mock_processor_output

        # model.get_audio_features(**inputs) returns something.
        # The code does: outputs = self.model.get_audio_features(**inputs)
        # embedding = outputs[0].cpu().numpy().tolist()

        mock_tensor = MagicMock()
        mock_tensor.cpu.return_value.numpy.return_value.tolist.return_value = [0.1, 0.2, 0.3]

        # If code uses outputs[0], we need get_audio_features to return something indexable
        mock_outputs = MagicMock()
        mock_outputs.__getitem__.return_value = mock_tensor
        mock_model_inst.get_audio_features.return_value = mock_outputs
        mock_model_inst.get_text_features.return_value = mock_outputs

        file_path = Path("kick.wav")
        engine = VectorSearchEngine(persistent_path="./test_db")

        # 1. Initialize
        engine.initialize_db()
        mock_chroma.PersistentClient.assert_called_with(path="./test_db")
        assert engine.chroma_client is not None

        # 2. Index File
        engine.index_file(file_path)

        # Check calls
        mock_proc_cls.from_pretrained.assert_called()
        mock_model_cls.from_pretrained.assert_called()
        mock_librosa.load.assert_called_with(str(file_path), sr=48000, duration=10.0)

        # Verify upsert
        # upsert(ids=[...], embeddings=[...], metadatas=[...])
        assert mock_coll.upsert.called
        call_kwargs = mock_coll.upsert.call_args[1]
        assert call_kwargs['embeddings'] == [[0.1, 0.2, 0.3]]
        assert call_kwargs['metadatas'][0]['filename'] == 'kick.wav'

        # 3. Search
        # Mock query result
        mock_coll.query.return_value = {
            'ids': [['id1']],
            'metadatas': [[{'path': '/abs/kick.wav', 'filename': 'kick.wav'}]],
            'distances': [[0.1]]
        }

        results = engine.search("punchy kick")

        assert len(results) == 1
        assert results[0]['filename'] == 'kick.wav'
