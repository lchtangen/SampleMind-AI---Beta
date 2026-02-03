import os
import sys

import numpy as np

# Add src to path
sys.path.append(os.path.abspath("src"))

from samplemind.ai.classification.classifier import AIClassifier
from samplemind.core.engine.audio_engine import AudioFeatures


def verify_classifier():
    print("🚀 Verifying AIClassifier V6 Extensions...")

    # Mock Features
    class MockFeatures:
        def __init__(self):
            self.spectral_centroid = [100.0]
            self.rms_energy = [0.21]
            self.zero_crossing_rate = [0.01]
            self.tempo = 140.0
            self.key_details = {"scale": "major"}
            self.duration = 5.0
            self.sample_rate = 44100
            self.bit_depth = 16
            self.spectral_bandwidth = [2000.0]
            self.path = "test.wav"

    features = MockFeatures()
    classifier = AIClassifier()

    # Test 1: Kick Drum / Techno / Energetic
    res1 = classifier.classify_audio(features)
    print(f"Test 1: {res1.instrument} / {res1.genre} / {res1.mood}")
    assert res1.instrument == "kick"
    assert res1.genre == "techno"
    assert res1.mood == "energetic"
    print("✅ Test 1 Passed")

    # Test 2: Hihat / HipHop
    features.path = "test2.wav"
    features.spectral_centroid = [6000.0]
    features.zero_crossing_rate = [0.2]
    features.tempo = 90.0
    res2 = classifier.classify_audio(features)
    print(f"Test 2: {res2.instrument} / {res2.genre}")
    assert res2.instrument == "hihat"
    assert res2.genre == "hiphop"
    print("✅ Test 2 Passed")

    # Test 3: DnB / Aggressive
    features.path = "test3.wav"
    features.tempo = 175.0
    features.key_details = {"scale": "minor"}
    features.rms_energy = [0.3] # High energy
    res3 = classifier.classify_audio(features)
    print(f"Test 3: {res3.genre} / {res3.mood}")
    assert res3.genre == "dnb"
    assert res3.mood == "aggressive"
    print("✅ Test 3 Passed")

    print("\n🎉 AI Verification Complete!")

if __name__ == "__main__":
    verify_classifier()
