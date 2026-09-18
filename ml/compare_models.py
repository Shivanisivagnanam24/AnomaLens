import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

DATASET_FILE = DATA_DIR / "prediction_dataset.csv"

FEATURES = [
    "normal_count_last_3",
    "warning_count_last_3",
    "error_count_last_3",
    "warning_rate_last_3",
    "error_rate_last_3"
]

TARGET = "failure_next"


def calculate_metrics(actual, predicted):
    return {
        "accuracy": accuracy_score(actual, predicted),
        "precision": precision_score(
            actual,
            predicted,
            zero_division=0
        ),
        "recall": recall_score(
            actual,
            predicted,
            zero_division=0
        ),
        "f1": f1_score(
            actual,
            predicted,
            zero_division=0
        ),
        "matrix": confusion_matrix(
            actual,
            predicted
        )
    }


def main():
    data = pd.read_csv(DATASET_FILE)

    sequence_labels = (
        data.groupby("sequence_id")[TARGET]
        .max()
        .reset_index()
    )

    train_sequences, test_sequences = train_test_split(
        sequence_labels,
        test_size=0.30,
        random_state=42,
        stratify=sequence_labels[TARGET]
    )

    train_ids = train_sequences["sequence_id"]
    test_ids = test_sequences["sequence_id"]

    train_data = data[
        data["sequence_id"].isin(train_ids)
    ]

    test_data = data[
        data["sequence_id"].isin(test_ids)
    ]

    X_train = train_data[FEATURES]
    y_train = train_data[TARGET]

    X_test = test_data[FEATURES]
    y_test = test_data[TARGET]

    model = LogisticRegression(
        class_weight="balanced",
        random_state=42,
        max_iter=1000
    )

    model.fit(X_train, y_train)

    ml_predictions = model.predict(X_test)

    threshold_predictions = (
        test_data["warning_count_last_3"] >= 2
    ).astype(int)

    ml_metrics = calculate_metrics(
        y_test,
        ml_predictions
    )

    baseline_metrics = calculate_metrics(
        y_test,
        threshold_predictions
    )

    print("FAIR MODEL COMPARISON")
    print("=====================")

    print(f"\nTest sequences: {len(test_sequences)}")
    print(f"Test samples: {len(test_data)}")
    print(
        f"Actual failure samples: "
        f"{(y_test == 1).sum()}"
    )

    print("\nLogistic Regression")
    print("-------------------")
    print(
        f"Accuracy : "
        f"{ml_metrics['accuracy']:.4f}"
    )
    print(
        f"Precision: "
        f"{ml_metrics['precision']:.4f}"
    )
    print(
        f"Recall   : "
        f"{ml_metrics['recall']:.4f}"
    )
    print(
        f"F1-score : "
        f"{ml_metrics['f1']:.4f}"
    )
    print("Confusion Matrix:")
    print(ml_metrics["matrix"])

    print("\nRule-Based Threshold")
    print("--------------------")
    print("Rule: warning_count_last_3 >= 2")
    print(
        f"Accuracy : "
        f"{baseline_metrics['accuracy']:.4f}"
    )
    print(
        f"Precision: "
        f"{baseline_metrics['precision']:.4f}"
    )
    print(
        f"Recall   : "
        f"{baseline_metrics['recall']:.4f}"
    )
    print(
        f"F1-score : "
        f"{baseline_metrics['f1']:.4f}"
    )
    print("Confusion Matrix:")
    print(baseline_metrics["matrix"])


if __name__ == "__main__":
    main()