from flask import Flask, jsonify, request
import pandas as pd
import glob
import os
from flask_cors import CORS
import threading
from sniffer_controller import start_sniffing, stop_sniffing
import shutil

app = Flask(__name__)
CORS(app)

# Global variable to track the sniffing process
sniffing_active = False
sniffing_process = None


@app.route("/control", methods=["POST"])
def control_sniffing():
    global sniffing_active, sniffing_process

    action = request.json.get("action")

    if action == "start":
        if not sniffing_active:
            try:
                sniffing_active = True
                sniffing_process = threading.Thread(target=start_sniffing)
                sniffing_process.daemon = True
                sniffing_process.start()
                return jsonify({"status": "success", "message": "Sniffing started"})
            except Exception as e:
                sniffing_active = False
                return jsonify(
                    {"status": "error", "message": f"Failed to start: {str(e)}"}
                )
        return jsonify({"status": "warning", "message": "Already running"})

    elif action == "stop":
        if sniffing_active:
            try:
                sniffing_active = False
                stop_sniffing()
                if sniffing_process and sniffing_process.is_alive():
                    sniffing_process.join(timeout=2)
                return jsonify({"status": "success", "message": "Sniffing stopped"})
            except Exception as e:
                return jsonify(
                    {"status": "error", "message": f"Failed to stop: {str(e)}"}
                )
        return jsonify({"status": "warning", "message": "Already stopped"})

    return jsonify({"status": "error", "message": "Invalid action"})


@app.route("/status")
def get_status():
    return jsonify({"status": "success", "sniffing": sniffing_active})


@app.route("/")
def index():
    # Get all prediction files
    prediction_files = glob.glob("output/prediction_*.csv")

    if not prediction_files:
        return jsonify({"status": "error", "message": "No data available"})

    try:
        # Get the most recent file based on creation time
        latest_file = max(prediction_files, key=os.path.getctime)

        # Read only the latest file
        df = pd.read_csv(latest_file)

        # Sort by timestamp (newest first)
        df = df.sort_values("timestamp", ascending=False)

        # Convert to list of dictionaries for JSON response
        traffic_data = df[
            ["src_ip", "src_port", "dst_ip", "dst_port", "Label", "timestamp"]
        ].to_dict("records")

        return jsonify({"status": "success", "data": traffic_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/traffic", methods=["GET", "POST"])
def get_traffic():
    if request.method == "POST":
        try:
            data = request.get_json()
            return jsonify({"status": "success", "received": data})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    try:
        prediction_files = glob.glob("output/prediction_*.csv")
        if not prediction_files:
            return jsonify([])

        latest_file = max(prediction_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)
        last_prediction = df.iloc[-1:].to_dict("records")

        return jsonify(last_prediction)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/clear", methods=["POST"])
def clear_data():
    try:
        output_folder = "output"
        # Remove the entire output folder and recreate it
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder)
        return jsonify({"status": "success", "message": "Data cleared successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000)
