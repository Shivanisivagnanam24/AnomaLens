import re
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

RAW_LOG_FILE = DATA_DIR / "prediction_raw_logs.txt"
MANIFEST_FILE = DATA_DIR / "sequence_manifest.csv"

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


def load_log_events():
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
                events.append(event_type)

    return events


def load_manifest_events():
    events = []

    with open(MANIFEST_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            events.append(row["event_type"])

    return events


def main():
    log_events = load_log_events()
    manifest_events = load_manifest_events()

    print("Experiment Data Verification")
    print("----------------------------")

    print(f"Kubernetes log events: {len(log_events)}")
    print(f"Manifest events: {len(manifest_events)}")

    log_normal = log_events.count("normal")
    log_warning = log_events.count("warning")
    log_error = log_events.count("error")

    manifest_normal = manifest_events.count("normal")
    manifest_warning = manifest_events.count("warning")
    manifest_error = manifest_events.count("error")

    print("\nKubernetes logs:")
    print(f"Normal: {log_normal}")
    print(f"Warning: {log_warning}")
    print(f"Error: {log_error}")

    print("\nExperiment manifest:")
    print(f"Normal: {manifest_normal}")
    print(f"Warning: {manifest_warning}")
    print(f"Error: {manifest_error}")

    if log_events == manifest_events:
        print("\nVERIFICATION PASSED")
        print("Kubernetes logs match the experiment manifest.")
    else:
        print("\nVERIFICATION FAILED")

        mismatch_count = 0

        for index, (log_event, manifest_event) in enumerate(
            zip(log_events, manifest_events),
            start=1
        ):
            if log_event != manifest_event:
                mismatch_count += 1

                if mismatch_count <= 5:
                    print(
                        f"Mismatch at event {index}: "
                        f"log={log_event}, "
                        f"manifest={manifest_event}"
                    )

        print(f"Event mismatches found: {mismatch_count}")


if __name__ == "__main__":
    main()