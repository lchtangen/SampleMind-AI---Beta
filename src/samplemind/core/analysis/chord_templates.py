"""
Chord Templates for Music Theory Analysis

Provides pitch class profiles (chroma templates) for chord recognition
based on music theory. Templates are 12-dimensional vectors representing
the relative strength of each pitch class in a chord.

References:
- Krumhansl, C. L. (1990). Cognitive Foundations of Musical Pitch
- Fujishima, T. (1999). Realtime Chord Recognition of Musical Sound
"""

from typing import Dict, List, Tuple
import numpy as np

# Note names in order of pitch class (C=0, C#=1, ..., B=11)
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTE_NAMES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

# Mapping from note name to pitch class
NOTE_TO_PC = {name: i for i, name in enumerate(NOTE_NAMES)}
NOTE_TO_PC.update({name: i for i, name in enumerate(NOTE_NAMES_FLAT)})
NOTE_TO_PC.update({
    'Cb': 11, 'B#': 0, 'E#': 5, 'Fb': 4,  # Enharmonic spellings
})


def _create_template(intervals: List[int]) -> np.ndarray:
    """
    Create a 12-dimensional chord template from intervals.

    Args:
        intervals: List of semitone intervals from root (e.g., [0, 4, 7] for major)

    Returns:
        Normalized 12-dimensional template vector
    """
    template = np.zeros(12)
    for interval in intervals:
        template[interval % 12] = 1.0
    # Normalize
    if np.sum(template) > 0:
        template = template / np.linalg.norm(template)
    return template


# Chord type intervals (from root)
CHORD_INTERVALS = {
    # Triads
    'major': [0, 4, 7],          # Root, M3, P5
    'minor': [0, 3, 7],          # Root, m3, P5
    'diminished': [0, 3, 6],     # Root, m3, d5
    'augmented': [0, 4, 8],      # Root, M3, A5
    'sus2': [0, 2, 7],           # Root, M2, P5
    'sus4': [0, 5, 7],           # Root, P4, P5

    # Seventh chords
    'major7': [0, 4, 7, 11],     # Root, M3, P5, M7
    'minor7': [0, 3, 7, 10],     # Root, m3, P5, m7
    'dominant7': [0, 4, 7, 10],  # Root, M3, P5, m7
    'diminished7': [0, 3, 6, 9], # Root, m3, d5, d7
    'half_diminished7': [0, 3, 6, 10],  # Root, m3, d5, m7
    'minor_major7': [0, 3, 7, 11],      # Root, m3, P5, M7
    'augmented7': [0, 4, 8, 10],        # Root, M3, A5, m7
    'augmented_major7': [0, 4, 8, 11],  # Root, M3, A5, M7

    # Extended chords (simplified - only key tones)
    'add9': [0, 4, 7, 14],       # Root, M3, P5, M9
    'minor_add9': [0, 3, 7, 14], # Root, m3, P5, M9
    '6': [0, 4, 7, 9],           # Root, M3, P5, M6
    'minor6': [0, 3, 7, 9],      # Root, m3, P5, M6
}

# Generate chord templates for all chord types
CHORD_TEMPLATES: Dict[str, np.ndarray] = {
    name: _create_template(intervals)
    for name, intervals in CHORD_INTERVALS.items()
}


# Chord quality symbols for display
CHORD_SYMBOLS = {
    'major': '',
    'minor': 'm',
    'diminished': 'dim',
    'augmented': 'aug',
    'sus2': 'sus2',
    'sus4': 'sus4',
    'major7': 'maj7',
    'minor7': 'm7',
    'dominant7': '7',
    'diminished7': 'dim7',
    'half_diminished7': 'm7b5',
    'minor_major7': 'mM7',
    'augmented7': 'aug7',
    'augmented_major7': 'augM7',
    'add9': 'add9',
    'minor_add9': 'madd9',
    '6': '6',
    'minor6': 'm6',
}


# Scale degree Roman numerals for major and minor keys
SCALE_DEGREES = {
    'major': {
        0: 'I',    # Tonic
        2: 'ii',   # Supertonic
        4: 'iii',  # Mediant
        5: 'IV',   # Subdominant
        7: 'V',    # Dominant
        9: 'vi',   # Submediant
        11: 'vii°', # Leading tone
    },
    'minor': {
        0: 'i',    # Tonic
        2: 'ii°',  # Supertonic
        3: 'III',  # Mediant
        5: 'iv',   # Subdominant
        7: 'v',    # Dominant (natural minor)
        8: 'VI',   # Submediant
        10: 'VII', # Subtonic
        11: 'vii°', # Leading tone (harmonic minor)
    }
}


# Key profiles for major and minor (Krumhansl-Kessler)
# These represent the perceptual "fit" of each pitch class in a key
KEY_PROFILES = {
    'major': np.array([
        6.35,  # C (tonic)
        2.23,  # C#
        3.48,  # D
        2.33,  # D#
        4.38,  # E
        4.09,  # F
        2.52,  # F#
        5.19,  # G
        2.39,  # G#
        3.66,  # A
        2.29,  # A#
        2.88,  # B
    ]),
    'minor': np.array([
        6.33,  # C (tonic)
        2.68,  # C#
        3.52,  # D
        5.38,  # D# (minor third)
        2.60,  # E
        3.53,  # F
        2.54,  # F#
        4.75,  # G (fifth)
        3.98,  # G#
        2.69,  # A
        3.34,  # A#
        3.17,  # B
    ]),
}

# Normalize key profiles
for mode in KEY_PROFILES:
    KEY_PROFILES[mode] = KEY_PROFILES[mode] / np.linalg.norm(KEY_PROFILES[mode])


def get_chord_template(root: int, quality: str) -> np.ndarray:
    """
    Get the chord template for a specific root and quality.

    Args:
        root: Root pitch class (0-11, where C=0)
        quality: Chord quality (e.g., 'major', 'minor', 'dominant7')

    Returns:
        12-dimensional template rotated to the correct root
    """
    if quality not in CHORD_TEMPLATES:
        raise ValueError(f"Unknown chord quality: {quality}")

    template = CHORD_TEMPLATES[quality]
    # Rotate template to root
    return np.roll(template, root)


def get_chord_name(root: int, quality: str, use_flats: bool = False) -> str:
    """
    Get the chord name string.

    Args:
        root: Root pitch class (0-11)
        quality: Chord quality
        use_flats: Use flat notation instead of sharps

    Returns:
        Chord name (e.g., "Am7", "Gmaj7")
    """
    note_names = NOTE_NAMES_FLAT if use_flats else NOTE_NAMES
    root_name = note_names[root % 12]
    symbol = CHORD_SYMBOLS.get(quality, quality)
    return f"{root_name}{symbol}"


def get_roman_numeral(
    chord_root: int,
    key_root: int,
    key_mode: str = 'major',
    chord_quality: str = 'major',
) -> str:
    """
    Get the Roman numeral analysis for a chord in a key.

    Args:
        chord_root: Chord root pitch class (0-11)
        key_root: Key root pitch class (0-11)
        key_mode: 'major' or 'minor'
        chord_quality: Chord quality

    Returns:
        Roman numeral (e.g., "IV", "vi", "V7")
    """
    # Calculate scale degree
    scale_degree = (chord_root - key_root) % 12

    # Get base Roman numeral
    degrees = SCALE_DEGREES.get(key_mode, SCALE_DEGREES['major'])
    roman = degrees.get(scale_degree, '?')

    # Add quality modifier if needed
    if chord_quality in ['dominant7', 'major7', 'minor7']:
        if '7' not in roman:
            roman = roman.rstrip('°') + '7'

    return roman


def detect_key_from_chroma(
    chroma: np.ndarray,
    mode: str = None,
) -> Tuple[int, str, float]:
    """
    Detect key from chroma features using Krumhansl-Kessler profiles.

    Args:
        chroma: 12-dimensional chroma vector (mean across time)
        mode: Force 'major' or 'minor', or None to detect

    Returns:
        Tuple of (key_root, mode, confidence)
    """
    # Normalize chroma
    chroma = chroma / (np.linalg.norm(chroma) + 1e-8)

    best_key = 0
    best_mode = 'major'
    best_correlation = -1

    modes_to_check = [mode] if mode else ['major', 'minor']

    for check_mode in modes_to_check:
        profile = KEY_PROFILES[check_mode]

        for root in range(12):
            # Rotate profile to this key
            rotated_profile = np.roll(profile, root)

            # Calculate correlation
            correlation = np.dot(chroma, rotated_profile)

            if correlation > best_correlation:
                best_correlation = correlation
                best_key = root
                best_mode = check_mode

    # Convert correlation to confidence (0-1)
    confidence = (best_correlation + 1) / 2

    return best_key, best_mode, confidence
