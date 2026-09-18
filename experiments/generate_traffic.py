import requests
import random
import time
import csv
from pathlib import Path

BASE_URL = "http://127.0.0.1:62575"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MANIFEST_FILE = DATA_DIR / "sequence_manifest.csv"


def send_request(endpoint):
    try:
        start_time = time.time()

        response = requests.get(
            BASE_URL + endpoint,
            timeout=5
        )

        response_time = time.time() - start_time

        print(
            f"{endpoint:<10} "
            f"Status: {response.status_code} "
            f"Time: {response_time:.2f}s"
        )

        return response.status_code, response_time

    except requests.RequestException as error:
        print(f"{endpoint:<10} Request failed: {error}")
        return 0, 0


def record_event(
    writer,
    sequence_id,
    sequence_type,
    event_position,
    endpoint,
    event_type,
    status_code,
    response_time
):
    writer.writerow([
        sequence_id,
        sequence_type,
        event_position,
        endpoint,
        event_type,
        status_code,
        round(response_time, 4)
    ])


def healthy_sequence(sequence_id, writer):
    print("\n--- HEALTHY SEQUENCE ---")

    for position in range(1, 6):
        endpoint = random.choice(["/", "/health"])

        status_code, response_time = send_request(endpoint)

        record_event(
            writer,
            sequence_id,
            "healthy",
            position,
            endpoint,
            "normal",
            status_code,
            response_time
        )

        time.sleep(random.uniform(0.1, 0.4))


def failure_sequence(sequence_id, writer):
    print("\n--- PRE-FAILURE SEQUENCE ---")

    position = 1

    for _ in range(2):
        endpoint = random.choice(["/", "/health"])

        status_code, response_time = send_request(endpoint)

        record_event(
            writer,
            sequence_id,
            "failure",
            position,
            endpoint,
            "normal",
            status_code,
            response_time
        )

        position += 1
        time.sleep(random.uniform(0.1, 0.4))

    for _ in range(3):
        status_code, response_time = send_request("/warning")

        record_event(
            writer,
            sequence_id,
            "failure",
            position,
            "/warning",
            "warning",
            status_code,
            response_time
        )

        position += 1
        time.sleep(random.uniform(0.1, 0.4))

    status_code, response_time = send_request("/error")

    record_event(
        writer,
        sequence_id,
        "failure",
        position,
        "/error",
        "error",
        status_code,
        response_time
    )


def generate_experiment(total_sequences=50):
    DATA_DIR.mkdir(exist_ok=True)

    healthy_count = 0
    failure_count = 0

    with open(
        MANIFEST_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "sequence_id",
            "sequence_type",
            "event_position",
            "endpoint",
            "event_type",
            "status_code",
            "response_time"
        ])

        for sequence_id in range(1, total_sequences + 1):

            sequence_type = random.choices(
                ["healthy", "failure"],
                weights=[60, 40],
                k=1
            )[0]

            print(
                f"\nSequence {sequence_id}/{total_sequences} "
                f"({sequence_type})"
            )

            if sequence_type == "healthy":
                healthy_count += 1
                healthy_sequence(sequence_id, writer)

            else:
                failure_count += 1
                failure_sequence(sequence_id, writer)

            file.flush()

            time.sleep(random.uniform(0.3, 0.7))

    print("\nExperiment completed.")
    print(f"Total sequences: {total_sequences}")
    print(f"Healthy sequences: {healthy_count}")
    print(f"Failure sequences: {failure_count}")
    print(f"Manifest saved to: {MANIFEST_FILE}")


if __name__ == "__main__":
    generate_experiment(total_sequences=50)