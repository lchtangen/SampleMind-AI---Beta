# SampleMind AI - Product Overview

## Purpose
SampleMind AI is a hybrid AI-powered music production platform that provides advanced audio processing, analysis, and intelligent sample organization for music producers and audio engineers.

## Core Value Proposition
- **Advanced Audio Analysis**: Deep feature extraction including tempo, key, mood, genre, energy, spectral features, and MFCC
- **AI-Powered Insights**: Music analysis using Google Gemini 2.5 Pro, Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o, and local Ollama models
- **Intelligent Organization**: Automatic sample categorization and similarity search using vector embeddings
- **Real-Time Processing**: Local AI models provide <100ms response times for instant feedback
- **Multi-Platform Support**: Works on Linux, macOS, and Windows with cross-platform file picker

## Key Features

### Audio Processing Engine
- Comprehensive feature extraction (tempo, key, mode, chroma, spectral features, MFCC)
- Harmonic/percussive separation to isolate melodic and rhythmic elements
- Rhythm analysis with beat tracking, onset detection, and groove extraction
- Performance optimized with multi-level caching and SHA-256 file hashing
- Robust edge case handling for silence, impulses, and short audio clips

### Hybrid AI Architecture
| Provider | Model | Priority | Specialization | Response Time |
|----------|-------|----------|----------------|---------------|
| Local AI (Ollama) | Phi3, Qwen2.5 | 0 (Instant) | Ultra-fast caching | <100ms |
| Google Gemini | Gemini 2.5 Pro | 1 (Primary) | Audio analysis, genre classification | ~2-3s |
| Anthropic Claude | Claude 3.5 Sonnet | 2 (Specialist) | Production coaching, creative suggestions | ~3-5s |
| OpenAI GPT | GPT-4o | 3 (Fallback) | Emergency backup | ~2-5s |

### DAW Integration
- FL Studio support
- Ableton Live support
- Logic Pro support

### Interfaces
- **CLI**: Interactive terminal interface with rich formatting using Typer, Rich, and Textual
- **REST API**: FastAPI-powered async web service with comprehensive endpoints
- **Web UI**: React/Next.js frontend (in development)

## Target Users
- Music producers seeking intelligent sample organization
- Audio engineers requiring advanced audio analysis
- Sound designers looking for creative AI assistance
- DAW users wanting enhanced workflow automation
- Music production teams needing collaborative tools

## Use Cases
1. **Sample Library Management**: Automatically analyze and categorize large sample collections
2. **Creative Exploration**: Get AI-powered suggestions for complementary samples and production techniques
3. **Audio Analysis**: Extract detailed technical features from audio files for mixing and mastering
4. **Similarity Search**: Find samples similar to a reference track using vector embeddings
5. **Genre Classification**: Automatically identify and tag samples by genre and mood
6. **Production Coaching**: Receive AI-driven feedback on arrangements and sound design

## Development Status
- **Version**: 2.0.0-beta
- **License**: MIT
- **Test Coverage**: 81 tests passing, 30% overall coverage
- **Core Components**: Audio Engine (72% coverage), AI Manager (76% coverage)
- **Status**: Active development with stable core features
