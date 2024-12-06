import os
import socket
import time
from datetime import datetime
from pyflowmeter.sniffer import create_sniffer
from classifier import (
    classify_input_decision_tree,
    filter_and_rename_features,
    list1,
    list2,
)
import pandas as pd
import pickle
import logging
from constants import Constants
import shutil
import ipaddress
import psutil  # Add this import to use psutil for network information

SNIFTER_DURATION = 5


class SnifferController:
    def __init__(self):
        self.running = False
        self.current_sniffer = None
        self.my_network_ip = socket.gethostbyname(socket.gethostname())
        self.subnet_mask = self.get_local_subnet_mask()

    def get_timestamped_filename(self, base_path, prefix, extension):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(base_path, f"{prefix}_{timestamp}{extension}")

    def clear_output_folder(self, folder):
        """Clear all files in the output folder"""
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

    def is_running(self):
        return self.running

    def get_local_subnet_mask(self):
        """Retrieve the subnet mask of the local network interface."""
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    return addr.netmask
        return None

    def is_local_ip(self, ip):
        """Check if a given IP address is in the same network as the local IP."""
        network = ipaddress.ip_network(
            f"{self.my_network_ip}/{self.subnet_mask}", strict=False
        )
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj in network

    def start_sniffing(self, interface="Ethernet"):
        self.running = True

        logging.basicConfig(level=logging.INFO)

        input_folder = "input"
        output_folder = "output"

        self.clear_output_folder(output_folder)
        os.makedirs(input_folder, exist_ok=True)

        classifier_input_file = "./input/classifier_input.csv"

        # Ensure the input directory exists
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)

        with open("pickle/scaler.pkl", "rb") as scaler_file:
            loaded_scaler = pickle.load(scaler_file)

        with open("pickle/ddos_decision_tree_model.pkl", "rb") as model_file:
            loaded_model = pickle.load(model_file)

        blocked_ips = set()  # Set to store blocked IPs
        blocked_ips_file = "blocked_ips.txt"  # File to store blocked IPs

        # Load previously blocked IPs from file
        if os.path.exists(blocked_ips_file):
            with open(blocked_ips_file, "r") as f:
                blocked_ips.update(f.read().splitlines())

        try:
            while self.running:
                self.current_sniffer = create_sniffer(
                    input_interface=interface,
                    to_csv=True,
                    output_file=classifier_input_file,
                    verbose=True,
                )

                try:
                    self.current_sniffer.start()
                    logging.info(
                        f"Sniffing packets for {SNIFTER_DURATION} seconds... Saving to {classifier_input_file}"
                    )

                    time.sleep(SNIFTER_DURATION)

                    if self.current_sniffer.running:
                        self.current_sniffer.stop()
                    logging.info("Sniffer stopped.")

                    if not self.running:
                        break

                    if (
                        os.path.exists(classifier_input_file)
                        and os.path.getsize(classifier_input_file) > 0
                    ):
                        df = pd.read_csv(classifier_input_file)
                        logging.info("Successfully read classifier input file.")

                        renamed_df = filter_and_rename_features(df, list1, list2)
                        network_details = df[
                            ["src_ip", "src_port", "dst_ip", "dst_port"]
                        ]
                        predictions = classify_input_decision_tree(
                            renamed_df, loaded_model, loaded_scaler, list2
                        )

                        output_df = pd.concat([network_details, renamed_df], axis=1)
                        output_df["Label"] = predictions
                        output_df["timestamp"] = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

                        # Identify DDoS IPs that are inbound
                        ddos_ips = output_df.loc[
                            (output_df["Label"] == "BENIGN")
                            & ~output_df["src_ip"].apply(self.is_local_ip),
                            "src_ip",
                        ].unique()

                        ddos_ips_set = set(ddos_ips)
                        new_ddos_ips = ddos_ips_set - blocked_ips

                        if new_ddos_ips:
                            from filter import block_ips, cleanup_rules

                            block_ips(new_ddos_ips)
                            logging.info(f"Blocked new IPs: {new_ddos_ips}")

                            # Update the blocked_ips set
                            blocked_ips.update(new_ddos_ips)

                            # Save the updated blocked IPs to file
                            with open(blocked_ips_file, "w") as f:
                                for ip in blocked_ips:
                                    f.write(f"{ip}\n")

                        output_file = self.get_timestamped_filename(
                            output_folder, "prediction", ".csv"
                        )
                        output_df.to_csv(output_file, index=False)

                        logging.info(
                            f"Classification complete. Predictions saved to {output_file}"
                        )
                    else:
                        logging.warning(
                            f"Input file {classifier_input_file} is empty or does not exist."
                        )

                except ZeroDivisionError:
                    logging.error(
                        "Encountered ZeroDivisionError during packet processing. Retrying..."
                    )
                    if (
                        self.current_sniffer is not None
                        and self.current_sniffer.running
                    ):
                        self.current_sniffer.stop()
                    if not self.running:
                        break
                    continue

        except KeyboardInterrupt:
            logging.info("Sniffer interrupted. Exiting...")
        finally:
            if self.current_sniffer is not None and self.current_sniffer.running:
                self.current_sniffer.stop()
            # Clean up firewall rules
            from filter import cleanup_rules

            cleanup_rules()
            logging.info("Cleaned up firewall rules.")

    def stop_sniffing(self):
        self.running = False
        if self.current_sniffer is not None and self.current_sniffer.running:
            self.current_sniffer.stop()
