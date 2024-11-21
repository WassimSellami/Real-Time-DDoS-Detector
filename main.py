import time
from datetime import datetime
from pyflowmeter.sniffer import create_sniffer
from classifier import (
    classify_input,
    filter_and_rename_features,
    list1,
    list2,
)
import pandas as pd
import os
import pickle
import logging
from constants import Constants
from dashboard import app, update_dashboard_data
from threading import Thread
import shutil

SNIFTER_DURATION = 5


def get_timestamped_filename(base_path, prefix, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(base_path, f"{prefix}_{timestamp}{extension}")


def clear_output_folder(folder):
    """Clear all files in the output folder"""
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)


def main():
    logging.basicConfig(level=logging.INFO)

    input_folder = "input"
    output_folder = "output"

    # Clear and recreate the output folder
    clear_output_folder(output_folder)
    os.makedirs(input_folder, exist_ok=True)

    classifier_input_file = "./input/classifier_input.csv"

    with open("pickle/scaler.pkl", "rb") as scaler_file:
        loaded_scaler = pickle.load(scaler_file)

    with open("pickle/ddos_decision_tree_model.pkl", "rb") as model_file:
        loaded_model = pickle.load(model_file)

    try:
        while True:
            sniffer = create_sniffer(
                input_interface=Constants.NETWORK_INTERFACE,
                to_csv=True,
                output_file=classifier_input_file,
                verbose=True,
            )

            try:
                sniffer.start()
                logging.info(
                    f"Sniffing packets for {SNIFTER_DURATION} seconds... Saving to {classifier_input_file}"
                )

                time.sleep(SNIFTER_DURATION)

                sniffer.stop()
                logging.info("Sniffer stopped.")

                if (
                    os.path.exists(classifier_input_file)
                    and os.path.getsize(classifier_input_file) > 0
                ):
                    df = pd.read_csv(classifier_input_file)
                    logging.info("Successfully read classifier input file.")

                    renamed_df = filter_and_rename_features(df, list1, list2)

                    predictions = classify_input(
                        renamed_df, loaded_model, loaded_scaler, list2
                    )

                    output_file = get_timestamped_filename(
                        output_folder, "prediction", ".csv"
                    )
                    renamed_df["Label"] = predictions
                    renamed_df.to_csv(output_file, index=False)

                    # Update dashboard with new data
                    update_dashboard_data(renamed_df)

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
                if sniffer is not None:
                    sniffer.stop()
                continue

    except KeyboardInterrupt:
        logging.info("Sniffer interrupted. Exiting...")
    finally:
        if sniffer is not None and sniffer.running:
            sniffer.stop()


if __name__ == "__main__":
    # Start the dashboard in a separate thread
    dashboard_thread = Thread(target=app.run_server, kwargs={"debug": False})
    dashboard_thread.daemon = True
    dashboard_thread.start()

    # Run your main packet capture and analysis
    main()
