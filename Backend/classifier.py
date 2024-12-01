import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import MinMaxScaler


def filter_and_rename_features(df, list1, list2):
    """Filters and renames features of a DataFrame based on provided lists.

    Args:
        df: The input DataFrame.
        list1: List of selected features from df.
        list2: List of corresponding feature names for renaming.

    Returns:
        A DataFrame with filtered and renamed features.
    """
    filtered_df = df[[col for col in df.columns if col in list1]]
    name_mapping = dict(zip(list1, list2))
    renamed_df = filtered_df.rename(columns=name_mapping)

    return renamed_df


# Load the scaler and model outside of the function to avoid multiple loads
with open("pickle/scaler.pkl", "rb") as scaler_file:
    loaded_scaler = pickle.load(scaler_file)

list1 = [
    "totlen_fwd_pkts",
    "fwd_pkt_len_max",
    "fwd_pkt_len_mean",
    "bwd_pkt_len_max",
    "bwd_pkt_len_min",
    "bwd_pkt_len_mean",
    "bwd_pkt_len_std",
    "bwd_iat_tot",
    "pkt_len_min",
    "pkt_len_max",
    "pkt_len_mean",
    "pkt_len_std",
    "pkt_len_var",
    "urg_flag_cnt",
    "pkt_size_avg",
    "fwd_seg_size_avg",
    "bwd_seg_size_avg",
    "subflow_fwd_byts",
]
list2 = [
    "Total Length of Fwd Packet",
    "Fwd Packet Length Max",
    "Fwd Packet Length Mean",
    "Bwd Packet Length Max",
    "Bwd Packet Length Min",
    "Bwd Packet Length Mean",
    "Bwd Packet Length Std",
    "Bwd IAT Total",
    "Packet Length Min",
    "Packet Length Max",
    "Packet Length Mean",
    "Packet Length Std",
    "Packet Length Variance",
    "URG Flag Count",
    "Average Packet Size",
    "Fwd Segment Size Avg",
    "Bwd Segment Size Avg",
    "Subflow Fwd Bytes",
]


def classify_input_decision_tree(input_data, trained_model, scaler, selected_features):
    input_data = input_data.replace([np.inf, -np.inf], np.nan).dropna()
    input_data[selected_features] = scaler.transform(input_data[selected_features])
    predictions = trained_model.predict(input_data[selected_features])
    return predictions


def classify_input_cnn(df, model, scaler, feature_list):
    # Scale the features
    scaled_features = scaler.transform(df[feature_list])

    # Reshape the data for CNN input (samples, features, 1)
    reshaped_data = scaled_features.reshape(-1, scaled_features.shape[1], 1)

    # Get predictions
    predictions = model.predict(reshaped_data)

    # Convert predictions to labels
    predictions = (predictions > 0.5).astype(int)

    # Map numeric predictions to string labels
    label_mapping = {0: "BENIGN", 1: "DDoS"}
    string_predictions = np.array(
        [label_mapping[pred] for pred in predictions.flatten()]
    )

    return string_predictions
