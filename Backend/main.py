from threading import Thread
import logging
from server import app as flask_app
import time


def start_flask():
    flask_app.run(host="127.0.0.1", port=3000)


if __name__ == "__main__":
    flask_thread = Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Keep the server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
