from flask import Flask, render_template
import requests
import logging
import os

app = Flask(__name__, template_folder=os.path.abspath("templates"))
logging.basicConfig(level=logging.DEBUG)


@app.route("/")
def index():
    try:
        # Fetch data from the API
        logging.debug("Attempting to fetch data from API...")
        response = requests.get("http://127.0.0.1:3000/")
        data = response.json()
        logging.debug(f"Received data: {data}")

        if data["status"] == "success":
            logging.debug("Rendering template with traffic data...")
            return render_template("display.html", traffic_data=data["data"])
        else:
            logging.error(f"API returned error: {data['message']}")
            return render_template("display.html", error=data["message"])

    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return render_template("display.html", error=str(e))


if __name__ == "__main__":
    template_dir = os.path.abspath("templates")
    logging.info(f"Template directory: {template_dir}")
    logging.info("Starting display app on port 5000...")
    app.run(host="127.0.0.1", port=5000, debug=True)
