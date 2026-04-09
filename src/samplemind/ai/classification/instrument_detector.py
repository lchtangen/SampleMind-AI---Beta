"""
Instrument Detector — 128-class GM Standard (Step 18) — SampleMind v3.0

Classifies the dominant instrument(s) in an audio sample using a
multi-label approach across the full 128-class General MIDI (GM) standard.

Detection stages:
  1. Heuristic: spectral centroid, zero-crossing rate, MFCC + onset patterns
     → maps to instrument families (percussion, bass, lead, pad, etc.)
  2. CLAP embeddings (optional): semantic text-audio similarity against
     GM instrument name prompts for fine-grained disambiguation.

The result includes:
  - Top-k instrument names (GM names, e.g. "Acoustic Grand Piano")
  - Instrument family (e.g. "Keyboard", "Percussion", "Bass")
  - MIDI program number (0-127) for DAW integration

Usage::

    detector = InstrumentDetector()
    result = detector.detect(y, sr)
    print(result.primary_instrument, result.midi_program)

    result = detector.detect_file("kick.wav")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

# ── GM Instrument table (program 0-127) ───────────────────────────────────────
# Format: (program_number, name, family)

GM_INSTRUMENTS: list[tuple[int, str, str]] = [
    # Piano (0-7)
    (0, "Acoustic Grand Piano", "Piano"),
    (1, "Bright Acoustic Piano", "Piano"),
    (2, "Electric Grand Piano", "Piano"),
    (3, "Honky-tonk Piano", "Piano"),
    (4, "Electric Piano 1", "Piano"),
    (5, "Electric Piano 2", "Piano"),
    (6, "Harpsichord", "Piano"),
    (7, "Clavi", "Piano"),
    # Chromatic Percussion (8-15)
    (8, "Celesta", "Chromatic Percussion"),
    (9, "Glockenspiel", "Chromatic Percussion"),
    (10, "Music Box", "Chromatic Percussion"),
    (11, "Vibraphone", "Chromatic Percussion"),
    (12, "Marimba", "Chromatic Percussion"),
    (13, "Xylophone", "Chromatic Percussion"),
    (14, "Tubular Bells", "Chromatic Percussion"),
    (15, "Dulcimer", "Chromatic Percussion"),
    # Organ (16-23)
    (16, "Drawbar Organ", "Organ"),
    (17, "Percussive Organ", "Organ"),
    (18, "Rock Organ", "Organ"),
    (19, "Church Organ", "Organ"),
    (20, "Reed Organ", "Organ"),
    (21, "Accordion", "Organ"),
    (22, "Harmonica", "Organ"),
    (23, "Tango Accordion", "Organ"),
    # Guitar (24-31)
    (24, "Acoustic Guitar (nylon)", "Guitar"),
    (25, "Acoustic Guitar (steel)", "Guitar"),
    (26, "Electric Guitar (jazz)", "Guitar"),
    (27, "Electric Guitar (clean)", "Guitar"),
    (28, "Electric Guitar (muted)", "Guitar"),
    (29, "Overdriven Guitar", "Guitar"),
    (30, "Distortion Guitar", "Guitar"),
    (31, "Guitar harmonics", "Guitar"),
    # Bass (32-39)
    (32, "Acoustic Bass", "Bass"),
    (33, "Electric Bass (finger)", "Bass"),
    (34, "Electric Bass (pick)", "Bass"),
    (35, "Fretless Bass", "Bass"),
    (36, "Slap Bass 1", "Bass"),
    (37, "Slap Bass 2", "Bass"),
    (38, "Synth Bass 1", "Bass"),
    (39, "Synth Bass 2", "Bass"),
    # Strings (40-47)
    (40, "Violin", "Strings"),
    (41, "Viola", "Strings"),
    (42, "Cello", "Strings"),
    (43, "Contrabass", "Strings"),
    (44, "Tremolo Strings", "Strings"),
    (45, "Pizzicato Strings", "Strings"),
    (46, "Orchestral Harp", "Strings"),
    (47, "Timpani", "Strings"),
    # Ensemble (48-55)
    (48, "String Ensemble 1", "Ensemble"),
    (49, "String Ensemble 2", "Ensemble"),
    (50, "SynthStrings 1", "Ensemble"),
    (51, "SynthStrings 2", "Ensemble"),
    (52, "Choir Aahs", "Ensemble"),
    (53, "Voice Oohs", "Ensemble"),
    (54, "Synth Voice", "Ensemble"),
    (55, "Orchestra Hit", "Ensemble"),
    # Brass (56-63)
    (56, "Trumpet", "Brass"),
    (57, "Trombone", "Brass"),
    (58, "Tuba", "Brass"),
    (59, "Muted Trumpet", "Brass"),
    (60, "French Horn", "Brass"),
    (61, "Brass Section", "Brass"),
    (62, "SynthBrass 1", "Brass"),
    (63, "SynthBrass 2", "Brass"),
    # Reed (64-71)
    (64, "Soprano Sax", "Reed"),
    (65, "Alto Sax", "Reed"),
    (66, "Tenor Sax", "Reed"),
    (67, "Baritone Sax", "Reed"),
    (68, "Oboe", "Reed"),
    (69, "English Horn", "Reed"),
    (70, "Bassoon", "Reed"),
    (71, "Clarinet", "Reed"),
    # Pipe (72-79)
    (72, "Piccolo", "Pipe"),
    (73, "Flute", "Pipe"),
    (74, "Recorder", "Pipe"),
    (75, "Pan Flute", "Pipe"),
    (76, "Blown Bottle", "Pipe"),
    (77, "Shakuhachi", "Pipe"),
    (78, "Whistle", "Pipe"),
    (79, "Ocarina", "Pipe"),
    # Synth Lead (80-87)
    (80, "Lead 1 (square)", "Synth Lead"),
    (81, "Lead 2 (sawtooth)", "Synth Lead"),
    (82, "Lead 3 (calliope)", "Synth Lead"),
    (83, "Lead 4 (chiff)", "Synth Lead"),
    (84, "Lead 5 (charang)", "Synth Lead"),
    (85, "Lead 6 (voice)", "Synth Lead"),
    (86, "Lead 7 (fifths)", "Synth Lead"),
    (87, "Lead 8 (bass + lead)", "Synth Lead"),
    # Synth Pad (88-95)
    (88, "Pad 1 (new age)", "Synth Pad"),
    (89, "Pad 2 (warm)", "Synth Pad"),
    (90, "Pad 3 (polysynth)", "Synth Pad"),
    (91, "Pad 4 (choir)", "Synth Pad"),
    (92, "Pad 5 (bowed)", "Synth Pad"),
    (93, "Pad 6 (metallic)", "Synth Pad"),
    (94, "Pad 7 (halo)", "Synth Pad"),
    (95, "Pad 8 (sweep)", "Synth Pad"),
    # Synth Effects (96-103)
    (96, "FX 1 (rain)", "Synth FX"),
    (97, "FX 2 (soundtrack)", "Synth FX"),
    (98, "FX 3 (crystal)", "Synth FX"),
    (99, "FX 4 (atmosphere)", "Synth FX"),
    (100, "FX 5 (brightness)", "Synth FX"),
    (101, "FX 6 (goblins)", "Synth FX"),
    (102, "FX 7 (echoes)", "Synth FX"),
    (103, "FX 8 (sci-fi)", "Synth FX"),
    # Ethnic (104-111)
    (104, "Sitar", "Ethnic"),
    (105, "Banjo", "Ethnic"),
    (106, "Shamisen", "Ethnic"),
    (107, "Koto", "Ethnic"),
    (108, "Kalimba", "Ethnic"),
    (109, "Bag pipe", "Ethnic"),
    (110, "Fiddle", "Ethnic"),
    (111, "Shanai", "Ethnic"),
    # Percussive (112-119)
    (112, "Tinkle Bell", "Percussive"),
    (113, "Agogo", "Percussive"),
    (114, "Steel Drums", "Percussive"),
    (115, "Woodblock", "Percussive"),
    (116, "Taiko Drum", "Percussive"),
    (117, "Melodic Tom", "Percussive"),
    (118, "Synth Drum", "Percussive"),
    (119, "Reverse Cymbal", "Percussive"),
    # Sound Effects (120-127)
    (120, "Guitar Fret Noise", "Sound Effects"),
    (121, "Breath Noise", "Sound Effects"),
    (122, "Seashore", "Sound Effects"),
    (123, "Bird Tweet", "Sound Effects"),
    (124, "Telephone Ring", "Sound Effects"),
    (125, "Helicopter", "Sound Effects"),
    (126, "Applause", "Sound Effects"),
    (127, "Gunshot", "Sound Effects"),
]

# Build lookup tables
_GM_BY_PROGRAM: dict[int, tuple[str, str]] = {
    prog: (name, family) for prog, name, family in GM_INSTRUMENTS
}
_CLAP_PROMPTS: list[str] = [
    f"a {name} instrument sound" for _, name, _ in GM_INSTRUMENTS
]

# ── Feature-based family mapping ──────────────────────────────────────────────
# Each family entry: (centroid_lo, centroid_hi, rms_lo, rms_hi, zcr_lo, zcr_hi)
# None means "any value accepted"

_FAMILY_HEURISTICS: list[tuple[str, dict]] = [
    ("Percussion", {"is_percussive": True}),
    ("Bass", {"centroid_hi": 1500, "rms_lo": 0.05}),
    ("Synth Lead", {"centroid_lo": 2000, "zcr_lo": 0.08}),
    (
        "Synth Pad",
        {"centroid_lo": 1000, "centroid_hi": 4000, "rms_hi": 0.10, "zcr_hi": 0.06},
    ),
    ("Piano", {"centroid_lo": 1200, "centroid_hi": 4000, "zcr_lo": 0.05}),
    ("Guitar", {"centroid_lo": 1500, "centroid_hi": 5000, "zcr_lo": 0.07}),
    ("Strings", {"centroid_lo": 1000, "centroid_hi": 6000, "rms_lo": 0.03}),
    ("Brass", {"centroid_lo": 1500, "rms_lo": 0.08}),
    ("Reed", {"centroid_lo": 1200, "zcr_lo": 0.06}),
]


# ── Result dataclass ──────────────────────────────────────────────────────────


@dataclass
class InstrumentResult:
    """128-class GM instrument detection result."""

    # Ordered by confidence
    instruments: list[str] = field(default_factory=list)
    families: list[str] = field(default_factory=list)
    midi_programs: list[int] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)

    # Top-1 convenience
    primary_instrument: str = "Unknown"
    primary_family: str = "Unknown"
    midi_program: int = 0
    confidence: float = 0.0

    method: str = "heuristic"


# ── Detector ──────────────────────────────────────────────────────────────────


class InstrumentDetector:
    """
    128-class GM instrument detector.

    Uses heuristic spectral rules + optional CLAP embedding for fine-grained
    instrument classification across all 128 GM program slots.
    """

    def __init__(self, top_k: int = 5, use_clap: bool = True) -> None:
        self.top_k = top_k
        self.use_clap = use_clap
        self._clap = None  # lazy-loaded

    # ── Public API ────────────────────────────────────────────────────────────

    def detect(self, y: np.ndarray, sr: int) -> InstrumentResult:
        """Detect instrument(s) from an audio signal."""
        result = InstrumentResult()

        # Heuristic family detection
        family_scores = self._heuristic_families(y, sr)

        # CLAP fine-grained (optional)
        clap_scores: dict[int, float] = {}
        if self.use_clap:
            clap_scores = self._clap_instrument_scores(y, sr)

        if clap_scores:
            # Blend: 65% CLAP, 35% heuristic (boosted toward heuristic family)
            final_scores = self._blend_scores(clap_scores, family_scores)
            result.method = "ensemble"
        else:
            # Convert family scores to per-instrument scores
            final_scores = self._family_to_instrument_scores(family_scores)

        # Sort and pick top-k
        sorted_progs = sorted(final_scores, key=lambda p: final_scores[p], reverse=True)
        top_progs = sorted_progs[: self.top_k]

        for prog in top_progs:
            name, family = _GM_BY_PROGRAM.get(prog, (f"Program {prog}", "Unknown"))
            result.instruments.append(name)
            result.families.append(family)
            result.midi_programs.append(prog)
            result.scores[name] = round(final_scores[prog], 4)

        if result.instruments:
            result.primary_instrument = result.instruments[0]
            result.primary_family = result.families[0]
            result.midi_program = result.midi_programs[0]
            result.confidence = result.scores.get(result.primary_instrument, 0.0)

        return result

    def detect_file(
        self, file_path: str | Path, sample_rate: int = 22050
    ) -> InstrumentResult:
        """Load and detect instrument from an audio file."""
        try:
            import librosa

            y, sr = librosa.load(str(file_path), sr=sample_rate, mono=True)
            return self.detect(y, sr)
        except Exception as exc:
            logger.error("InstrumentDetector failed for %s: %s", file_path, exc)
            return InstrumentResult()

    # ── Heuristic ─────────────────────────────────────────────────────────────

    @staticmethod
    def _heuristic_families(y: np.ndarray, sr: int) -> dict[str, float]:
        """
        Estimate instrument family scores from spectral features.
        Returns dict of family → score (0–1).
        """
        try:
            import librosa

            centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            rms = float(np.mean(librosa.feature.rms(y=y)))
            zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))

            # Percussive detection via onset/harmonic separation
            y_harm, y_perc = librosa.effects.hpss(y)
            perc_energy = float(np.mean(librosa.feature.rms(y=y_perc)))
            harm_energy = float(np.mean(librosa.feature.rms(y=y_harm)))
            is_percussive = perc_energy > 0.7 * (perc_energy + harm_energy + 1e-9)

        except Exception as exc:
            logger.warning("Heuristic feature extraction failed: %s", exc)
            return {"Synth Pad": 0.5}

        scores: dict[str, float] = {}

        if is_percussive:
            scores["Percussion"] = 0.9
            scores["Percussive"] = 0.7

        if centroid < 1500 and rms > 0.05:
            scores["Bass"] = 0.8

        if centroid > 2000 and zcr > 0.08 and not is_percussive:
            scores["Synth Lead"] = 0.7
            scores["Reed"] = 0.55

        if 1000 < centroid < 4000 and rms < 0.10 and zcr < 0.06:
            scores["Synth Pad"] = 0.75
            scores["Strings"] = 0.55
            scores["Ensemble"] = 0.45

        if 1200 < centroid < 4000 and zcr > 0.05 and not is_percussive:
            scores["Piano"] = 0.6
            scores["Guitar"] = 0.5

        if centroid > 1500 and rms > 0.08 and zcr > 0.04:
            scores["Brass"] = 0.55

        # Normalise
        max_s = max(scores.values()) if scores else 1.0
        return {f: s / max(max_s, 1e-9) for f, s in scores.items()}

    def _clap_instrument_scores(self, y: np.ndarray, sr: int) -> dict[int, float]:
        """
        Score GM programs using CLAP audio-text similarity.

        Returns dict of program_number → score, or empty dict if unavailable.
        For efficiency, only evaluates families detected heuristically.
        """
        if self._clap is None:
            self._clap = _load_clap()
        if self._clap is None:
            return {}

        try:
            processor, model = self._clap
            import librosa
            import torch

            y_48k = librosa.resample(y, orig_sr=sr, target_sr=48000)

            # Evaluate all 128 prompts in one batch
            audio_inputs = processor(
                audios=[y_48k], sampling_rate=48000, return_tensors="pt", padding=True
            )
            text_inputs = processor(
                text=_CLAP_PROMPTS, return_tensors="pt", padding=True
            )

            with torch.no_grad():
                audio_emb = model.get_audio_features(**audio_inputs)
                text_emb = model.get_text_features(**text_inputs)

            audio_emb = audio_emb / audio_emb.norm(dim=-1, keepdim=True)
            text_emb = text_emb / text_emb.norm(dim=-1, keepdim=True)
            sims = (audio_emb @ text_emb.T).squeeze(0).tolist()

            return {
                prog: float(sims[i]) for i, (prog, _, _) in enumerate(GM_INSTRUMENTS)
            }

        except Exception as exc:
            logger.warning("CLAP instrument detection failed: %s", exc)
            return {}

    @staticmethod
    def _family_to_instrument_scores(
        family_scores: dict[str, float],
    ) -> dict[int, float]:
        """Convert family confidence to per-program scores for the representative instrument."""
        instrument_scores: dict[int, float] = {}
        # Map family name → representative GM programs
        family_representatives: dict[str, list[int]] = {
            "Percussion": [116, 117, 118],  # Taiko, Melodic Tom, Synth Drum
            "Percussive": [112, 113, 114],
            "Bass": [32, 33, 38, 39],  # Acoustic, Electric, Synth Bass
            "Synth Lead": [80, 81, 82],  # square, saw, calliope
            "Synth Pad": [88, 89, 90],  # new age, warm, polysynth
            "Piano": [0, 4, 5],  # Grand, Elec Piano 1+2
            "Guitar": [24, 25, 29, 30],  # Acoustic, Overdriven, Distortion
            "Strings": [40, 48, 50],  # Violin, String Ens, SynthStrings
            "Ensemble": [48, 49, 52],
            "Brass": [56, 60, 61],  # Trumpet, French Horn, Brass Section
            "Reed": [64, 65, 66],  # Sax family
        }
        for family, score in family_scores.items():
            for prog in family_representatives.get(family, []):
                instrument_scores[prog] = max(instrument_scores.get(prog, 0.0), score)
        return instrument_scores

    @staticmethod
    def _blend_scores(
        clap_scores: dict[int, float],
        family_scores: dict[str, float],
    ) -> dict[int, float]:
        """Blend CLAP program scores with heuristic family scores."""
        # Build a family boost mask from heuristic family scores
        family_representatives: dict[str, list[int]] = {
            "Percussion": list(range(112, 120)),
            "Percussive": list(range(112, 120)),
            "Bass": list(range(32, 40)),
            "Synth Lead": list(range(80, 88)),
            "Synth Pad": list(range(88, 96)),
            "Piano": list(range(0, 8)),
            "Guitar": list(range(24, 32)),
            "Strings": list(range(40, 56)),
            "Ensemble": list(range(48, 56)),
            "Brass": list(range(56, 64)),
            "Reed": list(range(64, 72)),
        }
        heuristic_prog_scores: dict[int, float] = {}
        for family, fam_score in family_scores.items():
            for prog in family_representatives.get(family, []):
                heuristic_prog_scores[prog] = max(
                    heuristic_prog_scores.get(prog, 0.0), fam_score
                )

        blended: dict[int, float] = {}
        all_progs = set(clap_scores) | set(heuristic_prog_scores)
        for prog in all_progs:
            blended[prog] = 0.65 * clap_scores.get(
                prog, 0.0
            ) + 0.35 * heuristic_prog_scores.get(prog, 0.0)
        return blended


# ── Loader ────────────────────────────────────────────────────────────────────


def _load_clap():
    """Lazy-load CLAP model. Returns (processor, model) or None."""
    try:
        from transformers import ClapModel, ClapProcessor

        model_id = "laion/clap-htsat-unfused"
        processor = ClapProcessor.from_pretrained(model_id)
        model = ClapModel.from_pretrained(model_id)
        model.eval()
        return processor, model
    except Exception as exc:
        logger.info("CLAP not available for instrument: %s", exc)
        return None
