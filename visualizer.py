import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
import logging
from constants import *


class TrafficVisualizer:
    def __init__(self):
        self.fig_traffic = go.Figure()
        self.initialize_figure()
        logging.basicConfig(level=logging.INFO)

    def initialize_figure(self):
        """Initialize the figure with default layout"""
        self.fig_traffic.update_layout(
            title=TITLE_TEXT,
            xaxis_title=X_AXIS_TITLE,
            yaxis_title=Y_AXIS_TITLE,
            showlegend=True,
            height=GRAPH_HEIGHT,
            margin=dict(l=0, r=0, t=40, b=40),  # Remove margins
        )

    def update_traffic_plot(self, csv_files):
        """Updates the traffic visualization plot"""
        combined_data = []

        for file in csv_files:
            if not os.path.exists(file):
                continue

            try:
                df = pd.read_csv(file)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                combined_data.append(df)
            except Exception as e:
                logging.error(f"Error processing file {file}: {e}")
                continue

        if not combined_data:
            return

        # Combine all data and sort by timestamp
        df_all = pd.concat(combined_data, ignore_index=True)
        df_all = df_all.sort_values("timestamp")

        # Update the current time for continuous plotting
        current_time = datetime.now().replace(microsecond=0)

        # Filter last 2 minutes of data
        two_minutes_ago = current_time - TIME_WINDOW
        df_recent = df_all[df_all["timestamp"] >= two_minutes_ago].copy()

        if len(df_recent) == 0:
            return

        # Create fixed 5-second intervals
        time_range = pd.date_range(
            start=two_minutes_ago,
            end=current_time + timedelta(seconds=UPDATE_INTERVAL),
            freq=INTERVAL_FREQ,
        )

        # Create bins for the intervals
        df_recent["interval"] = pd.cut(
            df_recent["timestamp"],
            bins=time_range,
            labels=time_range[:-1],
            include_lowest=True,
            right=False,
        )

        df_recent["interval"] = (
            df_recent["interval"].astype(str).astype("datetime64[ns]")
        )

        # Count total packets per interval
        total_counts = df_recent.groupby("interval").size().reset_index(name="total")

        # Find intervals containing attack traffic
        attack_intervals = df_recent[df_recent["Label"] != BENIGN_LABEL][
            "interval"
        ].unique()

        # Create new figure
        self.fig_traffic = go.Figure()

        # Prepare data for continuous plotting
        normal_x = []
        normal_y = []
        attack_x = []
        attack_y = []

        for idx, row in total_counts.iterrows():
            interval = row["interval"]
            count = row["total"]

            if interval in attack_intervals:
                # Add to attack data
                attack_x.append(interval)
                attack_y.append(count)
            else:
                # Add to normal data
                normal_x.append(interval)
                normal_y.append(count)

        # Plot normal traffic (always show)
        self.fig_traffic.add_trace(
            go.Scatter(
                x=normal_x if normal_x else [two_minutes_ago],
                y=normal_y if normal_y else [0],
                mode="lines",
                line=dict(width=LINE_WIDTH, color=NORMAL_TRAFFIC_COLOR),
                name=NORMAL_TRAFFIC_LABEL,
                fill="tozeroy",
                fillcolor=NORMAL_TRAFFIC_FILL,
            )
        )

        # Plot attack traffic (always show)
        self.fig_traffic.add_trace(
            go.Scatter(
                x=attack_x if attack_x else [two_minutes_ago],
                y=attack_y if attack_y else [0],
                mode="lines",
                line=dict(width=LINE_WIDTH, color=ATTACK_TRAFFIC_COLOR),
                name=ATTACK_TRAFFIC_LABEL,
                fill="tozeroy",
                fillcolor=ATTACK_TRAFFIC_FILL,
            )
        )

        # Update layout with fixed y-axis range and no vertical lines
        self.fig_traffic.update_layout(
            title=dict(
                text=TITLE_TEXT,
                font=dict(size=TITLE_FONT_SIZE, color="black"),
                y=TITLE_Y_POSITION,
                x=TITLE_X_POSITION,
                xanchor="center",
                yanchor="top",
            ),
            xaxis_title=dict(
                text=X_AXIS_TITLE,
                font=dict(size=AXIS_TITLE_FONT_SIZE, color="black"),
            ),
            yaxis_title=dict(
                text=Y_AXIS_TITLE,
                font=dict(size=AXIS_TITLE_FONT_SIZE, color="black"),
            ),
            showlegend=True,
            height=GRAPH_HEIGHT,
            hovermode="x unified",
            xaxis=dict(
                showgrid=False,  # Disable vertical grid lines
                range=[two_minutes_ago, current_time],
                tickfont=dict(size=TICK_FONT_SIZE),
            ),
            yaxis=dict(
                showgrid=True,  # Enable horizontal grid lines
                gridwidth=GRID_WIDTH,
                gridcolor=GRID_COLOR,
                type="log",  # Set y-axis to logarithmic
                tickvals=[1, 2, 5, 10, 20, 50, 100],  # Custom tick values
                ticktext=["1", "2", "5", "10", "20", "50", "100"],  # Custom tick labels
                range=[0, 2],  # log10(1) = 0, log10(100) ≈ 2
                tickfont=dict(size=TICK_FONT_SIZE),
            ),
            legend=dict(
                font=dict(size=LEGEND_FONT_SIZE),
                yanchor="top",
                y=1.1,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(255, 255, 255, 0)",
                bordercolor="rgba(255, 255, 255, 0)",
            ),
            plot_bgcolor=PLOT_BGCOLOR,
        )

    def get_plots(self):
        """Returns the current figure"""
        return self.fig_traffic
