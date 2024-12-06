from flask import Flask, render_template, jsonify, request
import requests
import logging
import os
from urllib.parse import urljoin

# Application Constants
APP_HOST = "0.0.0.0"
APP_PORT = 5000
TEMPLATE_DIR = os.path.abspath("templates")

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:3000")
API_ENDPOINTS = {
    "data": "/",
    "control": "/control",
    "clear": "/clear",
    "status": "/status",
}

# Initialize Flask app
app = Flask(__name__, template_folder=TEMPLATE_DIR)
logging.basicConfig(level=logging.DEBUG)


def get_api_url(endpoint):
    """Helper function to construct API URLs"""
    return urljoin(API_BASE_URL, API_ENDPOINTS[endpoint])


@app.route("/")
def index():
    return render_template("display.html")


@app.route("/get_data")
def get_data():
    try:
        logging.debug("Attempting to fetch data from API...")
        response = requests.get(get_api_url("data"))
        data = response.json()
        logging.debug(f"Received data: {data}")
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})


@app.route("/control", methods=["POST"])
def control_sniffing():
    try:
        response = requests.post(get_api_url("control"), json=request.json)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/clear", methods=["POST"])
def clear_data():
    try:
        response = requests.post(get_api_url("clear"))
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/status")
def get_status():
    try:
        response = requests.get(get_api_url("status"))
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    logging.info(f"Template directory: {TEMPLATE_DIR}")
    logging.info(f"Starting display app on port {APP_PORT}...")
    app.run(host=APP_HOST, port=APP_PORT, debug=True)
