from flask import Flask, jsonify, request
import pandas as pd
import glob
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000)
