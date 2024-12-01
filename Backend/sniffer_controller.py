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
import os
import pickle
import logging
from constants import Constants
import shutil

SNIFTER_DURATION = 5

# Global variables for control
running = False
current_sniffer = None


def get_timestamped_filename(base_path, prefix, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(base_path, f"{prefix}_{timestamp}{extension}")


def clear_output_folder(folder):
    """Clear all files in the output folder"""
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)


def start_sniffing():
    global running, current_sniffer
    running = True

    logging.basicConfig(level=logging.INFO)

    input_folder = "input"
    output_folder = "output"

    clear_output_folder(output_folder)
    os.makedirs(input_folder, exist_ok=True)

    classifier_input_file = "./input/classifier_input.csv"

    with open("pickle/scaler.pkl", "rb") as scaler_file:
        loaded_scaler = pickle.load(scaler_file)

    with open("pickle/ddos_decision_tree_model.pkl", "rb") as model_file:
        loaded_model = pickle.load(model_file)

    try:
        while running:
            current_sniffer = create_sniffer(
                input_interface=Constants.NETWORK_INTERFACE,
                to_csv=True,
                output_file=classifier_input_file,
                verbose=True,
            )

            try:
                current_sniffer.start()
                logging.info(
                    f"Sniffing packets for {SNIFTER_DURATION} seconds... Saving to {classifier_input_file}"
                )

                time.sleep(SNIFTER_DURATION)

                current_sniffer.stop()
                logging.info("Sniffer stopped.")

                if not running:
                    break

                if (
                    os.path.exists(classifier_input_file)
                    and os.path.getsize(classifier_input_file) > 0
                ):
                    df = pd.read_csv(classifier_input_file)
                    logging.info("Successfully read classifier input file.")

                    renamed_df = filter_and_rename_features(df, list1, list2)
                    network_details = df[["src_ip", "src_port", "dst_ip", "dst_port"]]
                    predictions = classify_input_decision_tree(
                        renamed_df, loaded_model, loaded_scaler, list2
                    )

                    output_df = pd.concat([network_details, renamed_df], axis=1)
                    output_df["Label"] = predictions
                    output_df["timestamp"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    output_file = get_timestamped_filename(
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
                if current_sniffer is not None:
                    current_sniffer.stop()
                if not running:
                    break
                continue

    except KeyboardInterrupt:
        logging.info("Sniffer interrupted. Exiting...")
    finally:
        if current_sniffer is not None and current_sniffer.running:
            current_sniffer.stop()


def stop_sniffing():
    global running, current_sniffer
    running = False
    if current_sniffer is not None and current_sniffer.running:
        current_sniffer.stop()
