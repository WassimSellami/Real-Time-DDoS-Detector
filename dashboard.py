import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import glob
import os
import pandas as pd
from datetime import datetime
from constants import Constants

app = dash.Dash(__name__)

# Create a global variable to store the latest data
latest_data = None


def update_dashboard_data(df):
    """Updates the dashboard with new data"""
    global latest_data
    # Add timestamp to the dataframe with exact capture time
    capture_time = datetime.now()
    df["timestamp"] = capture_time
    latest_data = df

    # Save latest_data to a temporary CSV file with timestamp in filename
    temp_file = f"output/prediction_{capture_time.strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(temp_file, index=False)


app.layout = html.Div(
    [
        html.H1(Constants.TITLE_TEXT, style={"textAlign": "center"}),
        html.Div(
            [
                dash_table.DataTable(
                    id="traffic-table",
                    columns=[
                        {"name": "Time", "id": "timestamp"},
                        {"name": "Source IP", "id": "src_ip"},
                        {"name": "Destination IP", "id": "dst_ip"},
                        {"name": "Protocol", "id": "protocol"},
                        {"name": "Traffic Type", "id": "Label"},
                        # Add any other columns you want to display
                    ],
                    style_table={
                        "height": f"{Constants.GRAPH_HEIGHT}px",
                        "overflowY": "auto",
                    },
                    style_cell={"textAlign": "center", "padding": "10px"},
                    style_header={
                        "backgroundColor": "rgb(230, 230, 230)",
                        "fontWeight": "bold",
                        "fontSize": f"{Constants.TICK_FONT_SIZE}px",
                    },
                    style_data_conditional=[
                        {
                            "if": {"filter_query": '{Label} != "BENIGN"'},
                            "backgroundColor": Constants.ATTACK_TRAFFIC_FILL,
                            "color": "black",
                        },
                        {
                            "if": {"filter_query": '{Label} = "BENIGN"'},
                            "backgroundColor": Constants.NORMAL_TRAFFIC_FILL,
                            "color": "black",
                        },
                    ],
                )
            ]
        ),
        dcc.Interval(
            id="interval-component",
            interval=Constants.UPDATE_INTERVAL
            * 1000,  # Convert seconds to milliseconds
            n_intervals=0,
        ),
    ]
)


@app.callback(
    Output("traffic-table", "data"), Input("interval-component", "n_intervals")
)
def update_table(n):
    # Use only the CSV files from the output directory
    csv_files = glob.glob("output/prediction_*.csv")

    if not csv_files:
        return []

    # Read and combine all CSV files
    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            dfs.append(df)
        except Exception as e:
            continue

    if not dfs:
        return []

    # Combine all data
    combined_df = pd.concat(dfs, ignore_index=True)

    # Sort by timestamp (newest first)
    combined_df = combined_df.sort_values("timestamp", ascending=False)

    # Format timestamp for display
    combined_df["timestamp"] = combined_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Return all rows, no grouping
    return combined_df.to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)
