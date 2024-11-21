import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import glob
import os
from visualizer import TrafficVisualizer
import pandas as pd
from datetime import datetime

app = dash.Dash(__name__)
visualizer = TrafficVisualizer()

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
        html.Div([dcc.Graph(id="traffic-graph", style={"height": "800px"})]),
        dcc.Interval(
            id="interval-component",
            interval=5 * 1000,  # Update every 5 seconds
            n_intervals=0,
        ),
    ]
)


@app.callback(
    Output("traffic-graph", "figure"),
    Input("interval-component", "n_intervals"),
)
def update_graphs(n):
    # Use only the CSV files from the output directory
    csv_files = glob.glob("output/prediction_*.csv")

    if csv_files:  # Only update if we have files to process
        visualizer.update_traffic_plot(csv_files)
        return visualizer.fig_traffic

    # Return empty figure if no data
    return {}


if __name__ == "__main__":
    app.run_server(debug=True)
