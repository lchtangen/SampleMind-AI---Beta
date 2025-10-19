# Audio Processing API

## Overview
The Audio Processing API provides advanced audio feature extraction and processing capabilities, including tempo detection, key detection, spectral analysis, and harmonic/percussive source separation.

## Audio Features Endpoints

### Extract Audio Features
- `POST /api/audio/features`
  - Extracts various audio features from the provided audio data.
  
  **Request Body:**
  ```json
  {
    "audio_data": "base64_encoded_audio_data",
    "sample_rate": 44100,
    "features": ["tempo", "key", "spectral", "mfcc"]
  }
  ```
  
  **Response:**
  ```json
  {
    "tempo": 120.5,
    "key": "C",
    "mode": "major",
    "spectral": {
      "centroid": [0.1, 0.2, ...],
      "bandwidth": [0.05, 0.06, ...],
      "rolloff": [0.8, 0.82, ...],
      "zero_crossing_rate": [0.01, 0.012, ...],
      "rms_energy": [0.5, 0.48, ...]
    },
    "mfcc": {
      "coefficients": [
        [1.0, 0.5, ...],
        [1.1, 0.6, ...],
        ...
      ],
      "delta": [...],
      "delta2": [...]
    }
  }
  ```

### Harmonic/Percussive Separation
- `POST /api/audio/separate`
  - Separates the harmonic and percussive components of an audio signal.
  
  **Request Body:**
  ```json
  {
    "audio_data": "base64_encoded_audio_data",
    "sample_rate": 44100,
    "margin": 2.0
  }
  ```
  
  **Response:**
  ```json
  {
    "harmonic": "base64_encoded_harmonic_audio",
    "percussive": "base64_encoded_percussive_audio"
  }
  ```

## Python Client Example

```python
import base64
import requests
import numpy as np
import soundfile as sf

# Load audio file
audio, sr = sf.read('example.wav')

# Encode audio to base64
audio_base64 = base64.b64encode(audio.tobytes()).decode('utf-8')

# Extract audio features
response = requests.post(
    'http://localhost:8000/api/audio/features',
    json={
        'audio_data': audio_base64,
        'sample_rate': sr,
        'features': ['tempo', 'key', 'spectral', 'mfcc']
    }
)

features = response.json()
print(f"Detected tempo: {features['tempo']} BPM")
print(f"Detected key: {features['key']} {features['mode']}")
```

## Error Handling

The API returns appropriate HTTP status codes and error messages in the following format:

```json
{
  "detail": "Error message describing the issue"
}
```

### Common Error Codes
- `400 Bad Request`: Invalid input data or missing required fields
- `422 Unprocessable Entity`: Validation error in the request body
- `500 Internal Server Error`: Server-side error during processing

## Rate Limiting

- 60 requests per minute per IP address
- 1000 requests per day per API key (if authentication is enabled)

## Authentication

For production use, include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```
