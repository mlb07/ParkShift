from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from parkshift.features import FEATURE_COLUMNS, build_labeled_feature_row, feature_vector
from parkshift.models import BattedBall, ParkProfile
from parkshift.translator import source_park_for_ball


@dataclass(frozen=True)
class TrainingDataset:
    rows: pd.DataFrame
    skipped_rows: int


def build_training_dataset(
    balls: list[BattedBall], parks: dict[str, ParkProfile]
) -> TrainingDataset:
    rows = []
    skipped = 0
    for ball in balls:
        source_park = source_park_for_ball(ball, parks)
        if source_park is None:
            skipped += 1
            continue
        row = build_labeled_feature_row(ball, source_park)
        if row is None:
            skipped += 1
            continue
        rows.append(row)
    return TrainingDataset(rows=pd.DataFrame(rows), skipped_rows=skipped)


def train_xhr_classifier(rows: pd.DataFrame):
    try:
        from sklearn.ensemble import HistGradientBoostingClassifier
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise RuntimeError(
            "ML training requires scikit-learn. Install with: "
            'python -m pip install -e ".[ml]"'
        ) from exc

    if rows.empty:
        raise ValueError("No training rows available.")
    labels = rows["label"].astype(int)
    if labels.nunique() < 2:
        raise ValueError("Training data must include both HR and non-HR examples.")

    model = make_pipeline(
        StandardScaler(),
        HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_iter=250,
            l2_regularization=0.05,
            random_state=42,
        ),
    )
    model.fit(rows[FEATURE_COLUMNS], labels)
    return model


def predict_xhr_probability(model, feature_row: dict[str, float]) -> float:
    probability = model.predict_proba([feature_vector(feature_row)])[0][1]
    return float(probability)
