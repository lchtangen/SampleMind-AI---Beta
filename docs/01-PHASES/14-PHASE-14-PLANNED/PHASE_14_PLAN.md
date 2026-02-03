# Phase 14 Execution Plan: Intelligent Sample Chaining

**Phase:** 14
**Status:** 🟡 In Progress
**Focus:** Sample Chain Recommender, Compatibility Analysis, Chain Generation
**Start Date:** February 3, 2026

## 1. Objective

Implement the "Sample Chain Recommender" (Roadmap Item #4). This feature uses AI and DSP analysis to build coherent "chains" of samples (e.g., Kick -> Snare -> Hat -> Bass) that work well together musically. It is a creative assistant that speeds up kit building and track foundation.

## 2. Key Features

### 2.1 Compatibility Engine (`src/samplemind/core/generation/chain_recommender.py`)

- **BPM Matching**: Identify samples with compatible or adaptable tempos.
- **Key Compatibility**: Circle of Fifths logic to find harmonious samples.
- **Spectral Balance**: Ensure elements don't clash in frequency (e.g., Sub Bass vs Kick).
- **Style/Vibe Matching**: Use metadata tags/classification to match "Dark", "Bright", "Lo-Fi", etc.

### 2.2 Chain Builder

- **Seed Input**: User provides a starting sample (e.g., a Kick drum).
- **Slots**: System fills predefined slots (Kick, Snare, Hat, Perc, Bass).
- **Diversity Control**: Slider to choose between "Cohesive" (Safe) and "Creative" (Wild) chains.

### 2.3 CLI Integration

- New menu option: `Build Sample Chain / Kit`
- Inputs: Seed file, Desired Length/Structure.
- Outputs: A new folder with the selected compatible samples copied into it.

## 3. Implementation Steps

1. **Create `ChainRecommender` Class**:
   - Manage state of current chain.
   - `find_candidates(slot_type, criteria)` method.
   - `score_compatibility(seed, candidate)` method.

2. **Enhance `AudioEngine` Integration**:
   - Ensure we can quickly query the library (CSV/DB) for samples by features.
   - _Note:_ If a DB isn't fully active, we might need to scan/filter in-memory or use file system tags.

3. **CLI Interface**:
   - "Select Seed Sample" -> "Generating Kit..." -> Preview Results -> Save.

## 4. Technical Architecture

```python
@dataclass
class ChainSlot:
    name: str          # e.g. "Snare"
    required_tags: List[str]
    frequency_range: Tuple[int, int]

class ChainRecommender:
    def recommend_next(self, current_chain: List[Sample], next_slot: ChainSlot) -> List[Sample]:
        # Logic to find best matches
        pass
```

## 5. Success Criteria

- [ ] User can select a Kick and get a recommended Snare and Hi-Hat.
- [ ] Recommended samples are in key (if tonal) or rhythmic sync.
- [ ] System handles missing metadata gracefully (falls back to signal analysis).
- [ ] Unit tests verify compatibility scoring logic.
