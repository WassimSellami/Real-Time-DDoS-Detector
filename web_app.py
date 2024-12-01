from flask import Flask, jsonify, request
import pandas as pd
import glob
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    try:
        # Get the latest prediction file
        prediction_files = glob.glob("output/prediction_*.csv")
        if not prediction_files:
            return jsonify({"status": "success", "data": []})

        # Read the most recent file
        latest_file = max(prediction_files, key=os.path.getctime)
        df = pd.read_csv(latest_file)

        # Group by source IP, destination IP, ports and Label
        grouped_data = (
            df.groupby(["src_ip", "src_port", "dst_ip", "dst_port", "Label"])
            .size()
            .reset_index(name="count")
        )

        # Convert DataFrame to dictionary format
        data = grouped_data.to_dict(orient="records")

        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


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
