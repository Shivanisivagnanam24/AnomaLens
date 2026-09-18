import subprocess
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

LOG_FILE = DATA_DIR / "raw_logs.txt"
TIMESTAMP_FILE = DATA_DIR / "last_collection.txt"

DATA_DIR.mkdir(exist_ok=True)


def get_last_collection_time():
    if TIMESTAMP_FILE.exists():
        return TIMESTAMP_FILE.read_text(encoding="utf-8").strip()

    return None


def save_collection_time(timestamp):
    TIMESTAMP_FILE.write_text(timestamp, encoding="utf-8")


def collect_logs():
    collection_time = datetime.now(timezone.utc).isoformat()

    command = [
        "kubectl",
        "logs",
        "deployment/anomalens-app"
    ]

    last_collection = get_last_collection_time()

    if last_collection:
        command.extend(["--since-time", last_collection])

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        logs = result.stdout

        if logs.strip():
            with open(LOG_FILE, "a", encoding="utf-8") as file:
                file.write(
                    f"\n--- Collection Time: {datetime.now()} ---\n"
                )
                file.write(logs)
                file.write("\n")

            print("New Kubernetes logs collected successfully.")

        else:
            print("No new Kubernetes logs found.")

        save_collection_time(collection_time)

        print(f"Log file: {LOG_FILE}")

    except subprocess.CalledProcessError as error:
        print("Failed to collect Kubernetes logs.")
        print(error.stderr)

    except FileNotFoundError:
        print(
            "kubectl was not found. "
            "Make sure kubectl is installed and available in PATH."
        )


if __name__ == "__main__":
    collect_logs()