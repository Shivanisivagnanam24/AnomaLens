import re
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

RAW_LOG_FILE = DATA_DIR / "raw_logs.txt"
OUTPUT_FILE = DATA_DIR / "processed_logs.csv"

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

LOG_PATTERN = re.compile(
    r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) "
    r"\| (INFO|WARNING|ERROR) \| (.*)$"
)


def clean_ansi(text):
    return ANSI_ESCAPE.sub("", text)


def classify_event(level, message):
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


def preprocess_logs():
    rows = []

    with open(RAW_LOG_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = clean_ansi(line.strip())

            match = LOG_PATTERN.match(line)

            if not match:
                continue

            timestamp, level, message = match.groups()

            event_type = classify_event(level, message)

            if event_type is None:
                continue

            rows.append([
                timestamp,
                level,
                message,
                event_type
            ])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "timestamp",
            "log_level",
            "message",
            "event_type"
        ])

        writer.writerows(rows)

    normal_count = sum(1 for row in rows if row[3] == "normal")
    warning_count = sum(1 for row in rows if row[3] == "warning")
    error_count = sum(1 for row in rows if row[3] == "error")

    print("Log preprocessing completed successfully.")
    print(f"Processed events: {len(rows)}")
    print(f"Normal events: {normal_count}")
    print(f"Warning events: {warning_count}")
    print(f"Error events: {error_count}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    preprocess_logs()