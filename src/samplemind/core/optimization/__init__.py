"""SampleMind AI Optimization Module"""

from .numba_utils import (
    correlate_chroma_with_profile,
    find_best_key_match,
    compute_spectral_centroid_batch,
    compute_zero_crossing_rate_batch,
    fast_normalize_columns,
    fast_cosine_similarity,
    fast_rolling_mean,
    compute_onset_strength,
    find_peaks_simple,
    fast_clip,
    fast_matrix_multiply_transpose,
    get_numba_stats,
)

from .batch_processor import (
    BatchAudioProcessor,
    AdaptiveBatchProcessor,
    BatchResult,
    process_audio_batch,
    get_optimal_worker_count,
)

__all__ = [
    "correlate_chroma_with_profile",
    "find_best_key_match",
    "compute_spectral_centroid_batch",
    "compute_zero_crossing_rate_batch",
    "fast_normalize_columns",
    "fast_cosine_similarity",
    "fast_rolling_mean",
    "compute_onset_strength",
    "find_peaks_simple",
    "fast_clip",
    "fast_matrix_multiply_transpose",
    "get_numba_stats",
    "BatchAudioProcessor",
    "AdaptiveBatchProcessor",
    "BatchResult",
    "process_audio_batch",
    "get_optimal_worker_count",
]
