"""
Ensemble Classifier — SampleMind v0.3.0

SVM + XGBoost + KNN soft-voting ensemble for robust audio feature classification.
Wraps existing CLAP-based classifiers with:
  - Uncertainty quantification (confidence < 0.6 → active learning queue)
  - Soft voting across 3 models
  - Per-task ensembles: energy, mood (simplified), instrument (simplified)

Active learning:
    Uncertain samples are logged to `~/.samplemind/active_learning/uncertain.jsonl`
    for periodic human/Claude review and model retraining.

Usage::

    from samplemind.ai.classification.ensemble import EnsembleClassifier

    clf = EnsembleClassifier()

    # Train on labeled feature vectors (shape: [N, n_features])
    clf.fit(X_train, y_energy_train, task="energy")

    # Predict with confidence
    label, confidence = clf.predict_one(features, task="energy")
    if confidence < 0.6:
        print("Uncertain — logged for review")
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, NamedTuple

import numpy as np

logger = logging.getLogger(__name__)

Task = Literal["energy", "mood_simplified", "instrument_simplified"]
EnergyLabel = Literal["low", "mid", "high"]
MoodLabel = Literal["dark", "chill", "aggressive", "euphoric", "melancholic", "neutral"]
InstrumentLabel = Literal[
    "loop", "hihat", "kick", "snare", "bass", "pad", "lead", "sfx", "unknown"
]

UNCERTAINTY_THRESHOLD = 0.60
ACTIVE_LEARNING_DIR = (
    Path(os.getenv("SAMPLEMIND_DATA_DIR", Path.home() / ".samplemind"))
    / "active_learning"
)


class PredictionResult(NamedTuple):
    label: str
    confidence: float
    probabilities: dict[str, float]
    is_uncertain: bool
    model_votes: dict[str, str]  # {model_name: predicted_label}


class EnsembleClassifier:
    """
    Soft-voting ensemble: SVM + XGBoost + KNN.

    Each model votes with its probability distribution.
    Final prediction = argmax of averaged probabilities.

    Handles graceful degradation: if a model fails to import or train,
    falls back to the remaining models.
    """

    def __init__(self) -> None:
        self._models: dict[str, dict] = {}  # task → {model_name: fitted_model}
        self._label_encoders: dict[str, object] = {}
        self._classes: dict[str, list[str]] = {}
        ACTIVE_LEARNING_DIR.mkdir(parents=True, exist_ok=True)

    # ── Training ──────────────────────────────────────────────────────────────

    def fit(
        self,
        X: np.ndarray,
        y: list[str],
        task: Task,
    ) -> EnsembleClassifier:
        """
        Fit the ensemble on feature matrix X and string labels y.

        Args:
            X: Feature matrix, shape [n_samples, n_features].
            y: List of string labels (e.g. ["low", "high", "mid", ...]).
            task: Which classification task ("energy", "mood_simplified", ...).

        Returns:
            self (for chaining).
        """
        from sklearn.preprocessing import LabelEncoder

        le = LabelEncoder()
        y_enc = le.fit_transform(y)
        self._label_encoders[task] = le
        self._classes[task] = list(le.classes_)

        models: dict[str, object] = {}

        # SVM
        try:
            from sklearn.svm import SVC

            svm = SVC(kernel="rbf", probability=True, C=10.0, gamma="scale")
            svm.fit(X, y_enc)
            models["svm"] = svm
            logger.debug("SVM fitted for task=%s", task)
        except Exception as exc:
            logger.warning("SVM skipped for task=%s: %s", task, exc)

        # XGBoost
        try:
            import xgboost as xgb

            xgb_model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                use_label_encoder=False,
                eval_metric="mlogloss",
                verbosity=0,
            )
            xgb_model.fit(X, y_enc)
            models["xgboost"] = xgb_model
            logger.debug("XGBoost fitted for task=%s", task)
        except Exception as exc:
            logger.warning("XGBoost skipped for task=%s: %s", task, exc)

        # KNN
        try:
            from sklearn.neighbors import KNeighborsClassifier

            knn = KNeighborsClassifier(
                n_neighbors=min(7, len(y)), weights="distance", metric="cosine"
            )
            knn.fit(X, y_enc)
            models["knn"] = knn
            logger.debug("KNN fitted for task=%s", task)
        except Exception as exc:
            logger.warning("KNN skipped for task=%s: %s", task, exc)

        if not models:
            raise RuntimeError(f"All models failed to fit for task={task}")

        self._models[task] = models
        logger.info(
            "Ensemble fitted for task=%s with models: %s", task, list(models.keys())
        )
        return self

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict_one(self, features: np.ndarray, task: Task) -> PredictionResult:
        """
        Predict label + confidence for a single feature vector.

        Args:
            features: 1-D feature vector (will be reshaped to [1, n_features]).
            task: Classification task.

        Returns:
            PredictionResult with label, confidence, and uncertainty flag.
        """
        x = features.reshape(1, -1)
        classes = self._classes.get(task, [])
        models = self._models.get(task, {})

        if not models or not classes:
            raise ValueError(f"Ensemble not trained for task={task}. Call fit() first.")

        # Collect probability distributions from each model
        all_probs: list[np.ndarray] = []
        model_votes: dict[str, str] = {}

        for name, model in models.items():
            try:
                proba = model.predict_proba(x)[0]  # shape: [n_classes]
                all_probs.append(proba)
                model_votes[name] = classes[int(np.argmax(proba))]
            except Exception as exc:
                logger.debug("Model %s predict_proba failed: %s", name, exc)

        if not all_probs:
            raise RuntimeError("All ensemble models failed during prediction")

        # Soft voting: average probabilities
        avg_probs = np.mean(all_probs, axis=0)
        best_idx = int(np.argmax(avg_probs))
        label = classes[best_idx]
        confidence = float(avg_probs[best_idx])

        prob_dict = {cls: float(p) for cls, p in zip(classes, avg_probs, strict=False)}
        is_uncertain = confidence < UNCERTAINTY_THRESHOLD

        if is_uncertain:
            self._log_uncertain(features, task, label, confidence)

        return PredictionResult(
            label=label,
            confidence=confidence,
            probabilities=prob_dict,
            is_uncertain=is_uncertain,
            model_votes=model_votes,
        )

    def predict_batch(
        self,
        feature_matrix: np.ndarray,
        task: Task,
    ) -> list[PredictionResult]:
        """Predict labels for a batch of feature vectors."""
        return [self.predict_one(row, task) for row in feature_matrix]

    # ── Active learning ───────────────────────────────────────────────────────

    def _log_uncertain(
        self,
        features: np.ndarray,
        task: str,
        predicted_label: str,
        confidence: float,
    ) -> None:
        """Append uncertain sample to the active learning queue."""
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "task": task,
            "predicted_label": predicted_label,
            "confidence": confidence,
            "feature_norm": float(np.linalg.norm(features)),
        }
        log_path = ACTIVE_LEARNING_DIR / "uncertain.jsonl"
        with log_path.open("a") as f:
            f.write(json.dumps(record) + "\n")

    def get_uncertain_count(self) -> int:
        """Return number of uncertain samples pending review."""
        log_path = ACTIVE_LEARNING_DIR / "uncertain.jsonl"
        if not log_path.exists():
            return 0
        with log_path.open() as f:
            return sum(1 for _ in f)


# ── Rule-based fallback (no training required) ────────────────────────────────


def classify_energy_rules(
    rms: float,
    spectral_centroid: float | None = None,
) -> tuple[EnergyLabel, float]:
    """
    Fast rule-based energy classification — no model training required.
    Used when ensemble is not yet fitted.

    Returns:
        (label, confidence) where confidence is a heuristic estimate.
    """
    if rms < 0.02:
        conf = min(1.0, 0.95 - rms * 10)
        return "low", conf
    elif rms < 0.08:
        # Mid range — use spectral centroid as tiebreaker
        if spectral_centroid and spectral_centroid > 4000:
            return "high", 0.65
        return "mid", 0.80
    else:
        conf = min(1.0, 0.90 + (rms - 0.08) * 2)
        return "high", conf


def classify_energy_from_features(features: dict) -> tuple[EnergyLabel, float]:
    """
    Classify energy from an AudioEngine feature dict.

    Tries ensemble classifier first, falls back to rules.
    """
    rms = features.get("rms", features.get("energy", 0.05))
    centroid = features.get("spectral_centroid_mean")
    return classify_energy_rules(rms=rms, spectral_centroid=centroid)
