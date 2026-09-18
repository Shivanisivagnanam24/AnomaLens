import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from sklearn.model_selection import train_test_split
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ML_DIR = PROJECT_ROOT / "ml"

DATASET_FILE = DATA_DIR / "prediction_dataset.csv"
MODEL_FILE = ML_DIR / "logistic_regression_model.pkl"

FEATURES = [
    "normal_count_last_3",
    "warning_count_last_3",
    "error_count_last_3",
    "warning_rate_last_3",
    "error_rate_last_3"
]

TARGET = "failure_next"


def load_dataset():
    return pd.read_csv(DATASET_FILE)


def split_by_sequence(data):
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

    return train_data, test_data


def prepare_features(train_data, test_data):
    X_train = train_data[FEATURES]
    y_train = train_data[TARGET]

    X_test = test_data[FEATURES]
    y_test = test_data[TARGET]

    return X_train, X_test, y_train, y_test


def train_model(X_train, y_train):
    model = LogisticRegression(
        class_weight="balanced",
        random_state=42,
        max_iter=1000
    )

    model.fit(X_train, y_train)

    return model


def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    matrix = confusion_matrix(
        y_test,
        predictions
    )

    print("\nModel Evaluation")
    print("----------------")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")

    print("\nConfusion Matrix")
    print(matrix)

    print("\nClassification Report")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    return predictions


def main():
    data = load_dataset()

    train_data, test_data = split_by_sequence(data)

    X_train, X_test, y_train, y_test = prepare_features(
        train_data,
        test_data
    )

    print("Dataset loaded successfully.")
    print(f"Total samples: {len(data)}")

    print("\nSequence-level split")
    print(
        f"Training sequences: "
        f"{train_data['sequence_id'].nunique()}"
    )
    print(
        f"Testing sequences: "
        f"{test_data['sequence_id'].nunique()}"
    )

    print("\nTraining samples")
    print(f"Total: {len(train_data)}")
    print(
        f"No-failure: "
        f"{(y_train == 0).sum()}"
    )
    print(
        f"Failure-next: "
        f"{(y_train == 1).sum()}"
    )

    print("\nTesting samples")
    print(f"Total: {len(test_data)}")
    print(
        f"No-failure: "
        f"{(y_test == 0).sum()}"
    )
    print(
        f"Failure-next: "
        f"{(y_test == 1).sum()}"
    )

    model = train_model(
        X_train,
        y_train
    )

    evaluate_model(
        model,
        X_test,
        y_test
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    print(
        f"\nModel saved to: {MODEL_FILE}"
    )


if __name__ == "__main__":
    main()