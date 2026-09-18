import pandas as pd
from pathlib import Path
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


def evaluate_threshold(data, threshold):
    actual = data["failure_next"]

    predictions = (
        data["warning_count_last_3"] >= threshold
    ).astype(int)

    accuracy = accuracy_score(actual, predictions)

    precision = precision_score(
        actual,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        actual,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        actual,
        predictions,
        zero_division=0
    )

    matrix = confusion_matrix(
        actual,
        predictions
    )

    return accuracy, precision, recall, f1, matrix


def main():
    data = pd.read_csv(DATASET_FILE)

    threshold = 2

    accuracy, precision, recall, f1, matrix = (
        evaluate_threshold(
            data,
            threshold
        )
    )

    print("Rule-Based Threshold Baseline")
    print("-----------------------------")

    print(
        f"Rule: warning_count_last_3 >= "
        f"{threshold}"
    )

    print(f"\nAccuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")

    print("\nConfusion Matrix")
    print(matrix)


if __name__ == "__main__":
    main()