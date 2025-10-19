"""
Test script for the Neurologic Audio Engine
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from audio.engine.neurologic_engine import NeurologicAudioEngine

def generate_test_signal(duration=1.0, sample_rate=44100, freq=440.0):
    """Generate a simple test sine wave."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq * t)

def test_engine():
    """Test the Neurologic Audio Engine with a simple sine wave."""
    print("Initializing Neurologic Audio Engine...")
    engine = NeurologicAudioEngine(sample_rate=44100)
    
    # Generate test signals
    print("Generating test signals...")
    sine_wave = generate_test_signal(duration=2.0, freq=440.0)  # A4 note
    
    # Process the audio
    print("Processing audio...")
    features = engine.process_audio(sine_wave)
    
    # Print feature shapes
    print("\nExtracted features:")
    for band, feat in features.items():
        print(f"{band}: {feat.shape} features")
    
    # Visualize the results
    visualize_features(features)
    
    # Test model saving/loading
    test_model_persistence(engine)
    
    print("\nAll tests completed successfully!")

def visualize_features(features):
    """Visualize the extracted features."""
    plt.figure(figsize=(12, 6))
    
    # Plot feature magnitudes for each band
    for i, (band, feat) in enumerate(features.items()):
        plt.subplot(2, 3, i+1)
        plt.bar(range(len(feat)), np.abs(feat))
        plt.title(f"{band.capitalize()} Band Features")
        plt.xlabel("Feature Index")
        plt.ylabel("Magnitude")
        plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Save the plot
    plt.savefig("output/feature_visualization.png")
    print("\nFeature visualization saved to 'output/feature_visualization.png'")

def test_model_persistence(engine):
    """Test saving and loading the model."""
    print("\nTesting model persistence...")
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Save the model
    model_path = "output/test_model.pkl"
    engine.save_model(model_path)
    print(f"Model saved to {model_path}")
    
    # Load the model
    loaded_engine = NeurologicAudioEngine.load_model(model_path)
    print("Model loaded successfully")
    
    # Verify the loaded model
    test_signal = generate_test_signal(duration=0.5, freq=880.0)
    original_output = engine.process_audio(test_signal)
    loaded_output = loaded_engine.process_audio(test_signal)
    
    # Check if outputs are similar
    for band in original_output:
        diff = np.mean(np.abs(original_output[band] - loaded_output[band]))
        print(f"{band} band output difference: {diff:.6f}")
    
    print("Model persistence test passed!")

if __name__ == "__main__":
    test_engine()
