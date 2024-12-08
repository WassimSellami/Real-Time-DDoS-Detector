from flask import Flask, jsonify, request
import pandas as pd
import glob
import os
from flask_cors import CORS
import threading
from sniffer_controller import SnifferController
import shutil
from utils import get_active_interface

# Application Constants
APP_HOST = "0.0.0.0"
APP_PORT = 3000

app = Flask(__name__)
CORS(app)

# Track both the process and current interface
sniffing_process = None
current_interface = get_active_interface()  # Default value
sniffer_controller = SnifferController()  # Create an instance of SnifferController


@app.route("/status")
def get_status():
    # Get actual running state from sniffer_controller
    return jsonify({"status": "success", "sniffing": sniffer_controller.is_running()})


@app.route("/control", methods=["POST"])
def control_sniffing():
    global sniffing_process, current_interface
    data = request.json
    action = data.get("action")
    # interface = data.get("interface", "Ethernet")

    if action == "start":
        if not sniffer_controller.is_running():
            try:
                # current_interface = interface  # Update the current interface
                sniffing_process = threading.Thread(
                    target=sniffer_controller.start_sniffing,
                    args=(current_interface,),
                )
                sniffing_process.daemon = True
                sniffing_process.start()
                return jsonify({"status": "success", "message": "Sniffing started"})
            except Exception as e:
                return jsonify(
                    {"status": "error", "message": f"Failed to start: {str(e)}"}
                )
        return jsonify({"status": "warning", "message": "Already running"})

    elif action == "stop":
        if sniffer_controller.is_running():
            try:
                sniffer_controller.stop_sniffing()
                if sniffing_process and sniffing_process.is_alive():
                    sniffing_process.join(timeout=2)
                return jsonify({"status": "success", "message": "Sniffing stopped"})
            except Exception as e:
                return jsonify(
                    {"status": "error", "message": f"Failed to stop: {str(e)}"}
                )
        return jsonify({"status": "warning", "message": "Already stopped"})

    return jsonify({"status": "error", "message": "Invalid action"})


@app.route("/")
def index():
    # Get all prediction files
    prediction_files = glob.glob("output/prediction_*.csv")

    if not prediction_files:
        return jsonify({"status": "success", "data": []})

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
        return jsonify({"status": "success", "data": []})


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


@app.route("/get_interface")
def get_interface():
    try:
        interface = get_active_interface()  # Use the utility function
        return jsonify({"status": "success", "interface": interface or "Not detected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    app.run(host=APP_HOST, port=APP_PORT)
