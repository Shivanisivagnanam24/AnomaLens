from flask import Flask, jsonify
import logging
import time

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

@app.route("/")
def home():
    logging.info("Home endpoint accessed successfully")
    return jsonify({
        "status": "healthy",
        "message": "AnomaLens sample application is running"
    })


@app.route("/health")
def health():
    logging.info("Health check completed successfully")
    return jsonify({
        "status": "healthy"
    })


@app.route("/warning")
def warning():
    logging.warning("High response time detected")
    time.sleep(2)

    return jsonify({
        "status": "warning",
        "message": "Application response was delayed"
    })


@app.route("/error")
def error():
    logging.error("Simulated application error detected")

    return jsonify({
        "status": "error",
        "message": "Simulated application failure"
    }), 500


if __name__ == "__main__":
    logging.info("Starting AnomaLens sample application")
    app.run(host="0.0.0.0", port=5000)