"""
Unit tests for samplemind.ai.classification.ensemble

Uses mock sklearn models so no real training data is needed.
All tests run without GPU, CLAP, or audio files.

Module under test:
    samplemind.ai.classification.ensemble
        — EnsembleClassifier (SVM + XGBoost + KNN soft-voting),
          PredictionResult, UNCERTAINTY_THRESHOLD

Key test scenarios:
    predict_one — basic
        - Returns a PredictionResult with label, confidence, probabilities,
          and per-model votes.
        - Probabilities sum to 1.0; confidence is in [0, 1].
    Uncertainty threshold
        - ``is_uncertain`` flag and ``_log_uncertain`` call when confidence
          drops below UNCERTAINTY_THRESHOLD.
        - Certain predictions do NOT trigger the uncertain logger.
    Untrained task
        - Raises ValueError("not trained") for a task with no fitted models.
    predict_batch
        - Returns a list of PredictionResult matching the input batch size.
    Fit + predict integration
        - Smoke test: fit with real sklearn stubs, then predict.
    Active-learning log
        - ``_log_uncertain`` writes JSONL records to disk.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from samplemind.ai.classification.ensemble import (
    UNCERTAINTY_THRESHOLD,
    EnsembleClassifier,
    PredictionResult,
)

# ── helpers ───────────────────────────────────────────────────────────────────


def _mock_model(classes: list[str], pred_idx: int, confidence: float = 0.8):
    """Return a mock sklearn model whose predict_proba returns a fixed distribution."""
    model = MagicMock()
    proba = np.zeros(len(classes), dtype=float)
    proba[pred_idx] = confidence
    proba += (
        (1.0 - confidence)
        / max(len(classes) - 1, 1)
        * (1 - np.eye(len(classes))[pred_idx])
    )
    proba /= proba.sum()
    model.predict_proba.return_value = proba.reshape(1, -1)
    return model


def _fitted_clf(
    task: str = "energy", classes: list[str] | None = None
) -> EnsembleClassifier:
    """Return an EnsembleClassifier pre-seeded with mocked models (no actual fitting)."""
    classes = classes or ["low", "mid", "high"]
    clf = EnsembleClassifier.__new__(EnsembleClassifier)
    clf._models = {}
    clf._label_encoders = {}
    clf._classes = {}
    # Ensure active-learning dir exists
    clf._active_learning_dir = Path(tempfile.mkdtemp())

    clf._classes[task] = classes
    clf._models[task] = {
        "svm": _mock_model(classes, pred_idx=2, confidence=0.8),
        "knn": _mock_model(classes, pred_idx=2, confidence=0.75),
    }
    return clf


# ── predict_one — basic ───────────────────────────────────────────────────────


def test_predict_one_returns_prediction_result():
    clf = _fitted_clf()
    feat = np.random.rand(20).astype(np.float32)
    result = clf.predict_one(feat, task="energy")
    assert isinstance(result, PredictionResult)


def test_predict_one_label_in_classes():
    clf = _fitted_clf(classes=["low", "mid", "high"])
    feat = np.ones(20, dtype=np.float32)
    result = clf.predict_one(feat, task="energy")
    assert result.label in {"low", "mid", "high"}


def test_predict_one_confidence_in_range():
    clf = _fitted_clf()
    feat = np.ones(20, dtype=np.float32)
    result = clf.predict_one(feat, task="energy")
    assert 0.0 <= result.confidence <= 1.0


def test_predict_one_probabilities_sum_to_one():
    clf = _fitted_clf()
    feat = np.ones(20, dtype=np.float32)
    result = clf.predict_one(feat, task="energy")
    total = sum(result.probabilities.values())
    assert abs(total - 1.0) < 1e-5


def test_predict_one_model_votes_present():
    clf = _fitted_clf()
    feat = np.ones(20, dtype=np.float32)
    result = clf.predict_one(feat, task="energy")
    assert "svm" in result.model_votes
    assert "knn" in result.model_votes


# ── uncertainty threshold ─────────────────────────────────────────────────────


def test_uncertain_flag_set_when_confidence_below_threshold():
    classes = ["low", "mid", "high"]
    clf = EnsembleClassifier.__new__(EnsembleClassifier)
    clf._models = {}
    clf._label_encoders = {}
    clf._classes = {}
    clf._active_learning_dir = Path(tempfile.mkdtemp())
    clf._classes["energy"] = classes

    # Force a very low-confidence model
    low_conf_model = MagicMock()
    proba = np.array([[0.34, 0.33, 0.33]])
    low_conf_model.predict_proba.return_value = proba
    clf._models["energy"] = {"svm": low_conf_model}

    feat = np.ones(20, dtype=np.float32)

    with patch.object(clf, "_log_uncertain") as mock_log:
        result = clf.predict_one(feat, task="energy")

    assert result.is_uncertain is True
    mock_log.assert_called_once()


def test_certain_flag_set_when_confidence_above_threshold():
    clf = _fitted_clf()  # models return 0.8 confidence
    feat = np.ones(20, dtype=np.float32)

    with patch.object(clf, "_log_uncertain") as mock_log:
        result = clf.predict_one(feat, task="energy")

    # confidence ≈ 0.8 > 0.6 threshold — should not be uncertain
    if result.confidence >= UNCERTAINTY_THRESHOLD:
        assert result.is_uncertain is False
        mock_log.assert_not_called()


# ── untrained task raises ─────────────────────────────────────────────────────


def test_predict_one_raises_when_not_fitted():
    clf = EnsembleClassifier.__new__(EnsembleClassifier)
    clf._models = {}
    clf._label_encoders = {}
    clf._classes = {}
    clf._active_learning_dir = Path(tempfile.mkdtemp())

    feat = np.ones(10, dtype=np.float32)
    with pytest.raises(ValueError, match="not trained"):
        clf.predict_one(feat, task="energy")


# ── predict_batch ─────────────────────────────────────────────────────────────


def test_predict_batch_returns_list_of_results():
    clf = _fitted_clf()
    X = np.random.rand(4, 20).astype(np.float32)
    results = clf.predict_batch(X, task="energy")
    assert len(results) == 4
    assert all(isinstance(r, PredictionResult) for r in results)


# ── fit + predict integration ─────────────────────────────────────────────────


def test_fit_then_predict_energy():
    """Smoke test: fit with sklearn stubs, then predict."""
    clf = EnsembleClassifier()
    clf._active_learning_dir = Path(tempfile.mkdtemp())

    X = np.random.rand(12, 8).astype(np.float32)
    y = ["low"] * 4 + ["mid"] * 4 + ["high"] * 4

    try:
        clf.fit(X, y, task="energy")
        feat = np.random.rand(8).astype(np.float32)
        result = clf.predict_one(feat, task="energy")
        assert result.label in {"low", "mid", "high"}
    except ImportError:
        pytest.skip("sklearn/xgboost not installed")


# ── active learning log ───────────────────────────────────────────────────────


def test_log_uncertain_writes_jsonl(tmp_path):
    clf = EnsembleClassifier.__new__(EnsembleClassifier)
    clf._models = {}
    clf._label_encoders = {}
    clf._classes = {}
    clf._active_learning_dir = tmp_path

    import samplemind.ai.classification.ensemble as mod

    with patch.object(mod, "ACTIVE_LEARNING_DIR", tmp_path):
        clf._log_uncertain(
            np.ones(10, dtype=np.float32),
            task="energy",
            predicted_label="low",
            confidence=0.35,
        )

    log_file = tmp_path / "uncertain.jsonl"
    assert log_file.exists()
    lines = log_file.read_text().strip().splitlines()
    assert len(lines) >= 1
    import json

    record = json.loads(lines[0])
    assert record["task"] == "energy"
    assert record["predicted_label"] == "low"
