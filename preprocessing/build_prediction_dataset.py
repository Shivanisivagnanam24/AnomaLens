import re
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

RAW_LOG_FILE = DATA_DIR / "prediction_raw_logs.txt"
MANIFEST_FILE = DATA_DIR / "sequence_manifest.csv"
OUTPUT_FILE = DATA_DIR / "prediction_dataset.csv"

ANSI_ESCAPE = re.compile(
    r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
)

LOG_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) "
    r"\| (INFO|WARNING|ERROR) \| (.*)$"
)


def clean_ansi(text):
    return ANSI_ESCAPE.sub("", text)


def classify_log_event(message):
    if "High response time detected" in message:
        return "warning"

    if "Simulated application error detected" in message:
        return "error"

    if (
        "Home endpoint accessed successfully" in message
        or "Health check completed successfully" in message
    ):
        return "normal"

    return None


def load_kubernetes_events():
    events = []

    with open(RAW_LOG_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = clean_ansi(line.strip())

            match = LOG_PATTERN.match(line)

            if not match:
                continue

            timestamp, level, message = match.groups()

            event_type = classify_log_event(message)

            if event_type is not None:
                events.append({
                    "timestamp": timestamp,
                    "log_level": level,
                    "event_type": event_type
                })

    return events


def load_manifest():
    rows = []

    with open(MANIFEST_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)

    return rows


def combine_data(log_events, manifest_rows):
    if len(log_events) != len(manifest_rows):
        raise ValueError(
            "Kubernetes log count does not match manifest count."
        )

    sequences = {}

    for log_event, manifest_row in zip(
        log_events,
        manifest_rows
    ):
        if log_event["event_type"] != manifest_row["event_type"]:
            raise ValueError(
                "Kubernetes logs do not match manifest event order."
            )

        sequence_id = int(manifest_row["sequence_id"])

        if sequence_id not in sequences:
            sequences[sequence_id] = []

        sequences[sequence_id].append({
            "timestamp": log_event["timestamp"],
            "log_level": log_event["log_level"],
            "event_type": log_event["event_type"],
            "event_position": int(
                manifest_row["event_position"]
            )
        })

    return sequences


def build_dataset(sequences, window_size=3):
    rows = []

    for sequence_id, events in sequences.items():

        events.sort(
            key=lambda event: event["event_position"]
        )

        for i in range(window_size, len(events)):
            window = events[i - window_size:i]
            next_event = events[i]

            normal_count = sum(
                event["event_type"] == "normal"
                for event in window
            )

            warning_count = sum(
                event["event_type"] == "warning"
                for event in window
            )

            error_count = sum(
                event["event_type"] == "error"
                for event in window
            )

            warning_rate = (
                warning_count / window_size
            )

            error_rate = (
                error_count / window_size
            )

            failure_next = (
                1
                if next_event["event_type"] == "error"
                else 0
            )

            rows.append([
                sequence_id,
                window[-1]["timestamp"],
                normal_count,
                warning_count,
                error_count,
                round(warning_rate, 4),
                round(error_rate, 4),
                failure_next
            ])

    return rows


def save_dataset(rows):
    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "sequence_id",
            "window_end_timestamp",
            "normal_count_last_3",
            "warning_count_last_3",
            "error_count_last_3",
            "warning_rate_last_3",
            "error_rate_last_3",
            "failure_next"
        ])

        writer.writerows(rows)


def main():
    log_events = load_kubernetes_events()
    manifest_rows = load_manifest()

    sequences = combine_data(
        log_events,
        manifest_rows
    )

    rows = build_dataset(sequences)

    failure_samples = sum(
        row[-1] for row in rows
    )

    no_failure_samples = (
        len(rows) - failure_samples
    )

    save_dataset(rows)

    print("Final prediction dataset created successfully.")
    print(
        f"Kubernetes events used: {len(log_events)}"
    )
    print(
        f"Sequences used: {len(sequences)}"
    )
    print(
        f"Prediction samples: {len(rows)}"
    )
    print(
        f"No-failure samples: {no_failure_samples}"
    )
    print(
        f"Failure-next samples: {failure_samples}"
    )
    print(
        f"Saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()