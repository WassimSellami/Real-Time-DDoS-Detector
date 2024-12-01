import sys
import os
import ctypes
from threading import Thread
import logging
import time
import subprocess
from filter import block_ips, cleanup_rules


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":
    if not is_admin():
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

    # Import after admin check to avoid import errors
    from server import app as flask_app

    def start_flask():
        flask_app.run(host="127.0.0.1", port=3000)

    flask_thread = Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Block IPs
    block_ips()
    print("IPs have been blocked. Press Ctrl+C to unblock.")

    # Keep the server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
        cleanup_rules()
