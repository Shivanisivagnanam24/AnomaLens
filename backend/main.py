
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import Event, Lock, Thread
import json
import re

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kubernetes import client, config
from kubernetes.stream import stream as k8s_stream


NAMESPACE = "default"
SELECTOR = "app=anomalens-app"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_FILE = PROJECT_ROOT / "ml" / "random_forest_model.pkl"
ALERT_FILE = PROJECT_ROOT / "data" / "alert_history.json"

FEATURES = [
    "normal_count_last_3",
    "warning_count_last_3",
    "error_count_last_3",
    "warning_rate_last_3",
    "error_rate_last_3",
]

MONITOR_INTERVAL_SECONDS = 2

state_lock = Lock()
stop_monitor = Event()

latest_prediction = None
monitor_thread = None
model = None


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def kubernetes_api():
    config.load_kube_config()
    return client.CoreV1Api()


def is_ready(pod):
    return any(
        condition.type == "Ready"
        and condition.status == "True"
        for condition in (pod.status.conditions or [])
    )


def get_pods(api):
    return api.list_namespaced_pod(
        namespace=NAMESPACE,
        label_selector=SELECTOR,
    ).items


def get_application_logs(api, tail_lines=500):
    pods = get_pods(api)

    if not pods:
        return None, ""

    pod = next(
        (item for item in pods if is_ready(item)),
        pods[0],
    )

    raw = api.read_namespaced_pod_log(
        name=pod.metadata.name,
        namespace=NAMESPACE,
        tail_lines=tail_lines,
        timestamps=True,
        _request_timeout=10,
    )

    return pod.metadata.name, raw


def parse_log_entries(raw):
    entries = []

    for line in raw.replace("\\n", "\n").splitlines():
        match = re.match(r"^(\S+)\s+(.*)$", line)

        if match:
            timestamp, message = match.groups()
        else:
            timestamp = ""
            message = line

        level_match = re.search(
            r"\b(ERROR|WARNING|WARN|INFO|DEBUG)\b",
            message,
            re.IGNORECASE,
        )

        level = (
            level_match.group(1).upper()
            if level_match
            else "OTHER"
        )

        if level == "WARN":
            level = "WARNING"

        entries.append(
            {
                "timestamp": timestamp,
                "level": level,
                "message": message,
            }
        )

    return entries


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


def load_alert_history():
    if not ALERT_FILE.exists():
        return []

    try:
        with ALERT_FILE.open("r", encoding="utf-8") as file:
            contents = json.load(file)

        return contents if isinstance(contents, list) else []

    except (OSError, json.JSONDecodeError):
        return []


def save_alert_history(alerts):
    ALERT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = ALERT_FILE.with_suffix(".json.tmp")

    with temporary_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            alerts,
            file,
            indent=2,
            ensure_ascii=False,
        )

    temporary_file.replace(ALERT_FILE)


def record_alert(prediction_result):
    with state_lock:
        alerts = load_alert_history()

        window = prediction_result["recent_events"]

        alert = {
            "id": (
                f"{prediction_result['pod']}:"
                f"{window[-1]['timestamp']}"
            ),
            "created_at": utc_now(),
            "pod": prediction_result["pod"],
            "prediction": 1,
            "prediction_label": "Failure-next predicted",
            "failure_probability": prediction_result[
                "failure_probability"
            ],
            "features": prediction_result["features"],
            "recent_events": window,
            "status": "recorded",
            "evaluation_context": "experimental",
        }

        # The same three-event window must not create
        # duplicate alerts on every monitoring cycle.
        if any(
            existing.get("id") == alert["id"]
            for existing in alerts
        ):
            return

        alerts.insert(0, alert)
        save_alert_history(alerts)


def calculate_prediction():
    if model is None:
        return {
            "status": "model_unavailable",
            "message": (
                "Trained Random Forest model not found "
                "or could not be loaded."
            ),
        }

    api = kubernetes_api()

    pod_name, raw = get_application_logs(
        api,
        tail_lines=500,
    )

    if pod_name is None:
        return {
            "status": "unavailable",
            "message": "No AnomaLens application pod found.",
        }

    recognized_events = []

    for entry in parse_log_entries(raw):
        event_type = classify_log_event(
            entry["message"]
        )

        if event_type is not None:
            recognized_events.append(
                {
                    "timestamp": entry["timestamp"],
                    "event_type": event_type,
                    "message": entry["message"],
                }
            )

    if len(recognized_events) < 3:
        return {
            "status": "insufficient_data",
            "pod": pod_name,
            "recognized_event_count": len(
                recognized_events
            ),
            "message": (
                "At least three recognized application "
                "events are required for prediction."
            ),
        }

    window = recognized_events[-3:]

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

    feature_values = {
        "normal_count_last_3": normal_count,
        "warning_count_last_3": warning_count,
        "error_count_last_3": error_count,
        "warning_rate_last_3": warning_count / 3,
        "error_rate_last_3": error_count / 3,
    }

    input_row = [
        [feature_values[name] for name in FEATURES]
    ]

    predicted_class = int(
        model.predict(input_row)[0]
    )

    failure_probability = None

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(
            input_row
        )[0]

        classes = list(model.classes_)

        if 1 in classes:
            failure_probability = float(
                probabilities[classes.index(1)]
            )

    return {
        "status": "success",
        "source": "live_application_logs",
        "evaluation_context": "experimental",
        "pod": pod_name,
        "model": "Random Forest",
        "prediction": predicted_class,
        "prediction_label": (
            "Failure-next predicted"
            if predicted_class == 1
            else "No immediate failure predicted"
        ),
        "failure_probability": failure_probability,
        "features": feature_values,
        "recent_events": window,
        "recognized_event_count": len(
            recognized_events
        ),
        "checked_at": utc_now(),
        "note": (
            "Experimental inference using the latest "
            "three recognized application events. "
            "The model was trained on controlled event "
            "sequences and is not validated for "
            "production failure forecasting."
        ),
    }


def monitor_predictions():
    global latest_prediction

    while not stop_monitor.is_set():
        try:
            result = calculate_prediction()

            with state_lock:
                latest_prediction = result

            if (
                result.get("status") == "success"
                and result.get("prediction") == 1
            ):
                record_alert(result)

        except Exception as exc:
            with state_lock:
                latest_prediction = {
                    "status": "error",
                    "message": str(exc),
                    "checked_at": utc_now(),
                }

        stop_monitor.wait(MONITOR_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app):
    global model
    global monitor_thread

    if MODEL_FILE.exists():
        try:
            model = joblib.load(MODEL_FILE)
        except Exception as exc:
            print(f"Model loading failed: {exc}")

    stop_monitor.clear()

    monitor_thread = Thread(
        target=monitor_predictions,
        daemon=True,
    )

    monitor_thread.start()

    yield

    stop_monitor.set()

    if monitor_thread is not None:
        monitor_thread.join(timeout=5)


app = FastAPI(
    title="AnomaLens API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/health")
def backend_health():
    return {
        "status": "running",
        "service": "AnomaLens API",
    }


@app.get("/api/infrastructure")
def infrastructure():
    try:
        pods = get_pods(kubernetes_api())

        details = [
            {
                "name": pod.metadata.name,
                "phase": pod.status.phase,
                "ready": is_ready(pod),
                "restart_count": sum(
                    container.restart_count or 0
                    for container in (
                        pod.status.container_statuses or []
                    )
                ),
            }
            for pod in pods
        ]

        return {
            "connected": True,
            "total_pods": len(details),
            "ready_pods": sum(
                item["ready"] for item in details
            ),
            "pods": details,
        }

    except Exception as exc:
        return {
            "connected": False,
            "error": str(exc),
            "total_pods": None,
            "ready_pods": None,
            "pods": [],
        }


@app.get("/api/application-health")
def application_health():
    try:
        api = kubernetes_api()

        pod = next(
            (
                item
                for item in get_pods(api)
                if is_ready(item)
            ),
            None,
        )

        if pod is None:
            return {
                "status": "unavailable",
                "responding": False,
                "message": "No ready AnomaLens pod was found.",
            }

        response = k8s_stream(
            api.connect_get_namespaced_pod_exec,
            pod.metadata.name,
            NAMESPACE,
            command=[
                "python",
                "-c",
                (
                    "import urllib.request; "
                    "r=urllib.request.urlopen("
                    "'http://127.0.0.1:5000/health',"
                    "timeout=5); "
                    "print(r.status)"
                ),
            ],
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
            _request_timeout=10,
        )

        if response.strip() == "200":
            return {
                "status": "healthy",
                "responding": True,
                "pod": pod.metadata.name,
                "http_status": 200,
            }

        return {
            "status": "unhealthy",
            "responding": False,
            "pod": pod.metadata.name,
            "message": response.strip(),
        }

    except Exception as exc:
        return {
            "status": "unknown",
            "responding": False,
            "message": str(exc),
        }


@app.get("/api/logs")
def logs():
    try:
        pod_name, raw = get_application_logs(
            kubernetes_api(),
            tail_lines=100,
        )

        return {
            "connected": True,
            "pod": pod_name,
            "entries": parse_log_entries(raw),
            "checked_at": utc_now(),
        }

    except Exception as exc:
        return {
            "connected": False,
            "entries": [],
            "error": str(exc),
        }


@app.get("/api/prediction")
def prediction():
    with state_lock:
        result = latest_prediction

    if result is None:
        return {
            "status": "initializing",
            "message": (
                "Background prediction monitor is starting."
            ),
        }

    return result


@app.get("/api/alerts")
def alerts():
    with state_lock:
        history = load_alert_history()

    return {
        "status": "success",
        "count": len(history),
        "alerts": history,
        "storage_file": str(ALERT_FILE),
        "checked_at": utc_now(),
    }