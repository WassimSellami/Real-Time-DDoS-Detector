from datetime import timedelta


class Constants:
    GRAPH_HEIGHT = 800
    TITLE_FONT_SIZE = 32
    AXIS_TITLE_FONT_SIZE = 18
    TICK_FONT_SIZE = 14
    LEGEND_FONT_SIZE = 20
    Y_AXIS_MAX = 20
    Y_AXIS_TICK_INTERVAL = 2
    GRID_WIDTH = 1
    GRID_COLOR = "LightGrey"
    PLOT_BGCOLOR = "white"
    TITLE_Y_POSITION = 0.95
    TITLE_X_POSITION = 0.5
    NORMAL_TRAFFIC_COLOR = "green"
    NORMAL_TRAFFIC_FILL = "rgba(0, 255, 0, 0.3)"
    ATTACK_TRAFFIC_COLOR = "red"
    ATTACK_TRAFFIC_FILL = "rgba(255, 0, 0, 0.3)"
    LINE_WIDTH = 2
    TIME_WINDOW = timedelta(minutes=2)
    UPDATE_INTERVAL = 5
    INTERVAL_FREQ = "5s"
    TITLE_TEXT = "Live DDoS Network Traffic Classification"
    X_AXIS_TITLE = "Time"
    Y_AXIS_TITLE = "Packet Count"
    NORMAL_TRAFFIC_LABEL = "Normal Traffic"
    ATTACK_TRAFFIC_LABEL = "DDoS Traffic"
    BENIGN_LABEL = "BENIGN"
    INPUT_FOLDER = "input"
    OUTPUT_FOLDER = "output"
    CLASSIFIER_INPUT_FILE = "./input/classifier_input.csv"
    PREDICTION_FILE_PREFIX = "prediction"
    SCALER_PATH = "pickle/scaler.pkl"
    MODEL_PATH = "pickle/ddos_decision_tree_model.pkl"
