from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)


@app.route("/")
def index():
    try:
        # Read the most recent prediction file
        # Assuming the prediction file path pattern matches your current setup
        df = pd.read_csv(
            "output/prediction_20241201_123620.csv"
        )  # You might want to make this dynamic

        # Group by source and destination IPs
        grouped_data = (
            df.groupby(["src_ip", "dst_ip", "label"]).size().reset_index(name="count")
        )

        # Convert DataFrame to dictionary format
        data = grouped_data.to_dict(orient="records")

        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)
