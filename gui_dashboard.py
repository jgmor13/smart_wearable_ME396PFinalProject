# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 09:00:22 2025

@author: jgmor
"""

# -*- coding: utf-8 -*-
from HR_Processing import HRProcessor
from HRV_Processing import HRVProcessor
from User_Profile import UserProfile
from Training_Zone import zones_karvonen, zone_label
from VO2_Max_Estimator import vo2max_uth
from Heart_Rate_Sim import Simulated_HR

from collections import deque
import time
import dash
from dash import html, dcc
from dash.dependencies import Input, Output

# ---------------------------
# Initialize user + processors
# ---------------------------
user = UserProfile(23, 5, 4, "F", 200)
hr_resting  = 62
hr_max = 192

hr_processor = HRProcessor()
hrv_processor = HRVProcessor()

hr_buffer = deque(maxlen=300)
rr_buffer = deque(maxlen=300)

sim_hr = Simulated_HR(start_hr=75)
step = 0

# Global variable to track steps
global_step = {"value": 0}

# ---------------------------
# Dash App
# ---------------------------
app = dash.Dash(__name__)

app.layout = html.Div(
    style={
        "fontFamily": "Arial",
        "textAlign": "center",
        "padding": "40px",
        "fontSize": "24px"
    },
    children=[
        html.H2("Live Heart Metrics Monitor"),
        html.Div(id="live-output", style={"marginTop": "40px"}),
        dcc.Interval(id="interval-component", interval=1000, n_intervals=0)  # 1 Hz
    ]
)


# ---------------------------
# Live callback
# ---------------------------
@app.callback(
    Output("live-output", "children"),
    Input("interval-component", "n_intervals")
)
def update_metrics(n):
    """Runs every second and updates the displayed HR metrics."""
    # Simulate HR
    step = global_step["value"]
    hr_raw = sim_hr.workout(step)
    global_step["value"] += 1

    # Process HR
    clean_hr = hr_processor.process(hr_raw)
    if clean_hr is None:
        return "Waiting for valid HR..."

    # Training zone
    zone = zones_karvonen(clean_hr, hr_max, hr_resting)
    label = zone_label(zone)

    # HRV
    rr = hrv_processor.add_beat(timestamp=time.time())
    rmssd_val = hrv_processor.get_rmssd()
    rmssd_display = f"{rmssd_val:.2f}" if rmssd_val else "N/A"

    # VO2 Max
    vo2_max = vo2max_uth(hr_max, hr_resting)

    # Output string
    output_str = (
        f"❤️ {clean_hr} BPM | "
        f"Zone: {label} | "
        f"RMSSD: {rmssd_display} ms | "
        f"VO2max: {vo2_max:.2f} mL/kg/min"
    )

    return output_str


# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8054)
