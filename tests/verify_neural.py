import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np

# Ensure src is in path
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from samplemind.core.engine.audio_engine import AudioEngine, AudioFeatures
    from samplemind.core.engine.neural_engine import NeuralFeatureExtractor
except ImportError:
    print("Failed to import engines. Check python path.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NeuralVerifier")

def create_dummy_audio(filename="test_audio.wav"):
    """Create a dummy WAV file for testing"""
    import soundfile as sf
    sr = 44100
    t = np.linspace(0, 1, sr) # 1 second is enough
    y = 0.5 * np.sin(2 * np.pi * 440 * t)
    sf.write(filename, y, sr)
    return Path(filename)

def test_standalone_neural():
    logger.info("--- Testing NeuralFeatureExtractor Standalone ---")
    dummy_path = create_dummy_audio("neural_test.wav")

    # Test Mock Mode explicitly
    extractor = NeuralFeatureExtractor(use_mock=True)
    embedding = extractor.generate_embedding(dummy_path)
    logger.info(f"Mock Embedding Length: {len(embedding)}")
    assert len(embedding) == 512, "Mock embedding should be 512 floats"

    # Test Text Embedding
    text_emb = extractor.generate_text_embedding("funky guitar riff")
    logger.info(f"Mock Text Embedding Length: {len(text_emb)}")
    assert len(text_emb) == 512

def test_integrated_pipeline():
    logger.info("\n--- Testing Integrated Pipeline ---")
    dummy_path = create_dummy_audio("integration_test.wav")

    engine = AudioEngine(max_workers=1)

    # ⚠️ PATCH: Mock out the slow librosa/numba parts
    # We only care about ensuring the neural engine is CALLED and result STORED
    engine.feature_extractor.extract_tonal_features = MagicMock(return_value={
        'chroma_features': [], 'key': 'C', 'mode': 'major', 'pitch_class_distribution': []
    })
    engine.feature_extractor.extract_rhythmic_features = MagicMock(return_value={
        'tempo': 120, 'beats': [], 'onset_times': [], 'rhythm_pattern': []
    })
    engine.feature_extractor.extract_spectral_features = MagicMock(return_value={
        'spectral_centroid': [], 'spectral_bandwidth': [], 'spectral_rolloff': [],
        'zero_crossing_rate': [], 'mfccs': [], 'rms_energy': [0.5]
    })
