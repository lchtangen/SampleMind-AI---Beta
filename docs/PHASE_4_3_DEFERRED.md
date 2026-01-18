# Phase 4.3: Neural Audio Generation - DEFERRED PLAN

**Status:** Planning/Deferred
**Date:** January 18, 2026
**Reason for Deferral:** Resource constraints and lower immediate user priority
**Estimated Implementation:** Phase 4.3 (6-8 weeks when resources available)

---

## Executive Summary

Phase 4.3 would implement neural audio generation capabilities using MusicGen and AudioLDM models. However, this phase is **intentionally deferred** in favor of Phase 4.1 and 4.2 completion, which provide more immediate user value with realistic resource requirements.

### Why Deferred

| Factor | Impact | Notes |
|--------|--------|-------|
| **Model Size** | 3.5GB+ per model | Makes CLI distribution impractical |
| **GPU Requirement** | ~30s/sample without GPU | CPU performance unacceptable |
| **Integration Complexity** | High (new inference pipeline) | Significant refactoring needed |
| **User Priority** | Lower than audio analysis | Classification/mastering more valuable now |
| **Resource Efficiency** | Low for realistic outcomes | Better ROI from optimization work |

### Comparison with Phase 4.1+4.2

**Phase 4.1+4.2 (Implemented):**
- ✅ Audio analysis & enhancement
- ✅ <600MB model footprint
- ✅ CPU-ready (no GPU needed)
- ✅ Immediate user value
- ✅ Shipped in Phase 4.1 timeframe

**Phase 4.3 (Deferred):**
- ⏳ Audio generation
- ❌ 3.5GB+ model footprint
- ❌ GPU-dependent
- ⏳ Experimental features
- ⏳ Would take 6-8 additional weeks

---

## Architecture Plan (For Future Implementation)

### Models to Integrate

#### 1. MusicGen (Meta)

```python
# Hypothetical architecture (deferred)

from transformers import AutoProcessor, MusicgenForConditionalGeneration

class MusicGenerationEngine:
    """Generate background music and stems"""

    def __init__(self, model_id="facebook/musicgen-small"):
        # Models: musicgen-small (600MB), medium (1.5GB), large (3.5GB)
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = MusicgenForConditionalGeneration.from_pretrained(model_id)

    async def generate(
        self,
        prompt: str,
        duration_seconds: float = 30.0,
        temperature: float = 1.0,
    ) -> np.ndarray:
        """
        Generate music from text description.

        Args:
            prompt: Text description (e.g., "upbeat electronic dance music")
            duration_seconds: Length of generated audio
            temperature: Creativity (0.0=deterministic, 1.0=creative)

        Returns:
            Generated audio (16kHz mono)
        """
        inputs = self.processor(
            text=[prompt],
            padding=True,
            return_tensors="pt"
        )

        # Generate with 2x duration to account for synthesis
        audio_values = self.model.generate(
            **inputs,
            max_length=int(duration_seconds * 16000 * 2 / 320),  # Token scaling
            temperature=temperature,
        )

        return audio_values[0].cpu().numpy()
```

**Advantages:**
- Text-to-music generation
- Fine-tuned models available
- Fast inference (~5-10s for 30s audio)

**Drawbacks:**
- Text description quality critical
- Limited control over structure
- 3.5GB model footprint

---

#### 2. AudioLDM (Stability AI)

```python
# Hypothetical architecture (deferred)

from audiocraft import load_model

class AudioLDMEngine:
    """Generate sound effects and ambient audio"""

    def __init__(self, model_id="audioldm-medium-v10"):
        # Models available at different sizes
        self.model = load_model(model_id)

    async def generate(
        self,
        prompt: str,
        duration_seconds: float = 10.0,
        num_inference_steps: int = 50,
    ) -> np.ndarray:
        """
        Generate sound effects from text.

        Args:
            prompt: Text description (e.g., "rain on metal roof")
            duration_seconds: Audio length
            num_inference_steps: Diffusion steps (more = better quality but slower)

        Returns:
            Generated audio (16kHz mono)
        """
        # Diffusion-based generation
        output = self.model.generate(
            prompt,
            duration=duration_seconds,
            num_inference_steps=num_inference_steps,
            guidance_scale=7.5,  # How much to follow text description
        )

        return output.cpu().numpy()
```

**Advantages:**
- Sound effect generation
- High audio quality
- Fine-grained control

**Drawbacks:**
- Slower than MusicGen (2-3x)
- Memory intensive (4GB+ during inference)
- Requires CUDA 11.8+

---

### Integration Points

#### 1. Audio Engine Extension

```python
# Future integration

class AudioEngineWithGeneration(AudioEngine):
    """Extended audio engine with generation capabilities"""

    async def generate_background_music(
        self,
        style: str,
        duration: float,
    ) -> AudioFeatures:
        """Generate background music matching style"""
        engine = MusicGenerationEngine()
        audio = await engine.generate(style, duration)
        return await self.analyze_audio_async(audio)

    async def generate_sound_effect(
        self,
        description: str,
        duration: float,
    ) -> AudioFeatures:
        """Generate sound effect matching description"""
        engine = AudioLDMEngine()
        audio = await engine.generate(description, duration)
        return await self.analyze_audio_async(audio)
```

#### 2. TUI Screens

```python
# Future TUI implementation

class AudioGenerationScreen(Screen):
    """Generation UI with preview and parameters"""

    def __init__(self, engine: AudioEngineWithGeneration):
        self.engine = engine
        self.generation_in_progress = False
        self.preview_audio: Optional[np.ndarray] = None

    def compose(self):
        yield Header()

        # Input section
        with Vertical(id="input_section"):
            yield Static("Music Style: ")
            yield Input(id="style_input")
            yield Static("Duration: ")
            yield Input(id="duration_input")
            yield Button("Generate", id="generate_btn")

        # Progress
        yield ProgressBar(id="generation_progress")

        # Waveform display
        yield Static("Preview:", id="preview_label")
        yield WaveformWidget(id="waveform")

        # Controls
        with Horizontal():
            yield Button("Play", id="play_btn")
            yield Button("Regenerate", id="regenerate_btn")
            yield Button("Export", id="export_btn")

        yield Footer()
```

---

### Resource Requirements

#### Hardware

| Component | Min | Recommended | Ideal |
|-----------|-----|-------------|-------|
| GPU VRAM | 8GB | 24GB | 48GB |
| System RAM | 16GB | 32GB | 64GB |
| Storage | 10GB (models) | 20GB | 50GB |
| CPU Cores | 4 | 8 | 16 |

#### Inference Time (Single Sample)

| Model | GPU (RTX 4090) | GPU (RTX 3080) | CPU Only |
|-------|----------------|----------------|----------|
| MusicGen-Small | 2-3s | 5-8s | 5-10min |
| MusicGen-Medium | 4-6s | 10-15s | 15-30min |
| AudioLDM | 8-15s | 20-40s | Not practical |

**Note:** CPU-only generation is impractical for interactive use.

---

### Implementation Strategy (When Resources Available)

#### Phase 4.3a: Foundation (Weeks 1-2)

1. **Model Downloading**
   - Implement model caching system
   - Create download progress tracking
   - Handle model versioning

2. **Inference Pipeline**
   - Create async generation workers
   - Implement quality/speed tradeoffs
   - Setup memory management

3. **Testing**
   - Unit tests for generation (mocked)
   - Integration tests with actual models (GPU CI)
   - Performance benchmarks

#### Phase 4.3b: TUI Integration (Weeks 3-4)

1. **Generation Screen**
   - Input for prompts and parameters
   - Real-time progress display
   - Waveform preview and playback

2. **Model Selection**
   - UI for choosing models
   - Resource monitoring
   - Fallback recommendations

3. **Export Integration**
   - Save generated audio
   - Batch generation support
   - Playlist creation

#### Phase 4.3c: Advanced Features (Weeks 5-6)

1. **Refinement**
   - Iterative generation with feedback
   - Style mixing and blending
   - Controllable audio duration

2. **Optimization**
   - Model quantization for smaller footprint
   - Batch processing
   - Caching of generation results

3. **Documentation**
   - Usage guides
   - Prompt engineering tips
   - Performance tuning

---

## Alternative Approaches

### Option 1: Cloud-Based Generation (Not Recommended)

Use cloud APIs (Replicate, RunwayML) instead of local models.

**Pros:**
- ✅ No local GPU needed
- ✅ Simpler integration
- ✅ Always latest models

**Cons:**
- ❌ Requires internet (breaks offline-first philosophy)
- ❌ API costs ($0.10-1.00 per generation)
- ❌ Latency issues (2-5s network delay)
- ❌ Privacy concerns (data sent to cloud)

**Verdict:** Not aligned with SampleMind's offline-first design.

### Option 2: Lightweight Models Only

Use only smallest models (musicgen-small, audioldm-tiny)

**Pros:**
- ✅ Smaller footprint (~800MB)
- ✅ Faster inference (~5s)
- ✅ Feasible on consumer hardware

**Cons:**
- ❌ Lower quality output
- ❌ Limited model diversity
- ❌ Reduced user control

**Verdict:** Possible middle ground if MVP prioritized.

### Option 3: Defer to Phase 5+

Skip audio generation, focus on web UI and cloud sync first.

**Pros:**
- ✅ Focuses on immediate needs
- ✅ Web UI benefits all users
- ✅ Better ROI for development time

**Cons:**
- ❌ Generation feature pushed back further
- ❌ Some users may want generation

**Verdict:** Recommended approach for realistic timeline.

---

## Success Criteria (If/When Implemented)

- [ ] Generate 30-second background music in <10s (GPU)
- [ ] Generate 10-second sound effects in <5s (GPU)
- [ ] TUI allows parameter control (style, duration, temperature)
- [ ] Preview playback before export
- [ ] Batch generation for multiple prompts
- [ ] Memory efficient (<2GB peak during generation)
- [ ] 30 tests passing with GPU CI
- [ ] Comprehensive documentation
- [ ] Example prompts and results

---

## Dependencies

```toml
# Not added to current phase

[tool.poetry.dependencies]
# Audio generation (optional, GPU-required)
musicgen = { version = ">=0.1.0", optional = true }
audiocraft = { version = ">=1.0.0", optional = true }
transformers = { version = ">=4.30.0", optional = true }
torch = { version = ">=2.0.0", optional = true }
torchaudio = { version = ">=2.0.0", optional = true }

[tool.poetry.extras]
generation = ["musicgen", "audiocraft", "transformers", "torch", "torchaudio"]
```

---

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| GPU memory limits | High | Can't run inference | Implement memory monitoring, warn users |
| Model versioning conflicts | Medium | Incompatible APIs | Pin exact model versions, versioning tests |
| Performance unacceptable | Medium | Feature unusable | Start with smallest models, provide benchmarks |
| User confusion with outputs | Medium | Low satisfaction | Provide example prompts, quality guidance |

---

## Related Documentation

- PHASE_4_IMPLEMENTATION.md - Completed Phase 4.1 and 4.2
- Advanced features and audio forensics
- Real-time spectral analysis
- Stem separation (Demucs v4)

---

## Decision: Defer to Future Phase

**Recommendation:** Implement Phase 4.3 after Phase 5 (Web UI) is complete, if user demand warrants.

**Reasoning:**
1. Phase 4.1+4.2 deliver immediate value (analysis and enhancement)
2. Phase 4.3 requires GPU infrastructure (not available to all users)
3. Web UI (Phase 5) benefits broader audience
4. Better to have stable core features than experimental generation

**Revisit Criteria:**
- User demand for generation features
- Availability of GPU-capable servers
- Resolution of resource constraints
- Completion of Phase 5 and web UI

---

**Document prepared:** January 18, 2026
**Next phase:** Phase 5 - Web UI & Cloud Sync Architecture

---
