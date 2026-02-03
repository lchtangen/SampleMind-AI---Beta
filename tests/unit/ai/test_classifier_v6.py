import pytest

from samplemind.ai.classification.classifier import AIClassifier
from samplemind.core.engine.audio_engine import AudioFeatures


@pytest.fixture
def mock_features():
    # Helper to create a dummy features object
    class MockFeatures(AudioFeatures):
        pass

    # We cheat a bit by passing None for most things,
    # but the rule-based system needs specific attributes
    # We will mock the attributes the classifier looks for
    features = MockFeatures(
        path="test.wav", duration=5.0, sample_rate=44100,
        channels=2, format="wav"
    )
    features.tempo = 140.0
    features.key_details = {"scale": "major"}
    # The classifier calls np.mean on these
    features.spectral_centroid = [100.0, 100.0] # Low centroid for bass/kick
    features.rms_energy = [0.2, 0.2] # High energy
    features.zero_crossing_rate = [0.01, 0.01]
    return features

def test_rule_based_classification_kick(mock_features):
    classifier = AIClassifier()
    # Low centroid (<150), high energy (>0.15) -> Kick
    mock_features.spectral_centroid = [100.0]
    mock_features.rms_energy = [0.2]

    result = classifier.classify_audio(mock_features)
    assert result.instrument == "kick"
    assert result.genre == "techno" # 140 bpm
    assert result.mood == "energetic" # Major + high energy

def test_rule_based_classification_hihat(mock_features):
    classifier = AIClassifier()
    # High centroid, high ZCR -> Hihat
    mock_features.spectral_centroid = [6000.0]
    mock_features.zero_crossing_rate = [0.2]
    mock_features.rms_energy = [0.1]

    result = classifier.classify_audio(mock_features)
    assert result.instrument == "hihat"

def test_rule_based_classification_tempo(mock_features):
    classifier = AIClassifier()
    mock_features.tempo = 85.0
    result = classifier.classify_audio(mock_features)
    assert result.genre == "hiphop"
