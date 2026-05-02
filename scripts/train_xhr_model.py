from __future__ import annotations

import argparse
from pathlib import Path

from parkshift.ml import build_training_dataset, train_xhr_classifier
from parkshift.parks import load_parks
from parkshift.statcast import dataframe_to_batted_balls, load_statcast_csv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train an empirical xHR model from Baseball Savant CSV data."
    )
    parser.add_argument(
        "--csv",
        nargs="+",
        required=True,
        help="One or more Baseball Savant CSV exports.",
    )
    parser.add_argument(
        "--output",
        default="models/xhr_model.joblib",
        help="Where to write the trained model.",
    )
    args = parser.parse_args()

    try:
        import joblib
        from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
        from sklearn.model_selection import train_test_split
    except ImportError as exc:
        raise RuntimeError(
            "Training requires the ML extra. Install with: "
            'python -m pip install -e ".[ml]"'
        ) from exc

    parks = load_parks()
    balls = []
    for csv_path in args.csv:
        balls.extend(dataframe_to_batted_balls(load_statcast_csv(csv_path)))

    dataset = build_training_dataset(balls, parks)
    rows = dataset.rows
    labels = rows["label"].astype(int)
    train_rows, test_rows = train_test_split(
        rows,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )
    model = train_xhr_classifier(train_rows)
    probabilities = model.predict_proba(test_rows.drop(columns=["label"]))[:, 1]
    test_labels = test_rows["label"].astype(int)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_columns": [column for column in rows.columns if column != "label"],
        },
        output_path,
    )

    print(f"Training rows: {len(train_rows)}")
    print(f"Test rows: {len(test_rows)}")
    print(f"Skipped rows: {dataset.skipped_rows}")
    print(f"HR rate: {labels.mean():.3f}")
    print(f"ROC AUC: {roc_auc_score(test_labels, probabilities):.3f}")
    print(f"Log loss: {log_loss(test_labels, probabilities):.3f}")
    print(f"Brier score: {brier_score_loss(test_labels, probabilities):.3f}")
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
