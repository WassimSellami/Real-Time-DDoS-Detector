import sys
import ctypes
from threading import Thread
import logging
import time
from filter import cleanup_rules
from server import APP_HOST, APP_PORT, app as flask_app


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":
    from server import app as flask_app
    from sniffer_controller import SnifferController

    sniffer_controller = SnifferController()

    def start_flask():
        flask_app.run(host=APP_HOST, port=APP_PORT)

    flask_thread = Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
        cleanup_rules()
