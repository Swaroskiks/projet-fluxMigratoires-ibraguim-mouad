from dash import html, dcc
import pandas as pd

def create_timeline(df: pd.DataFrame) -> html.Div:
    return html.Div([
        dcc.Slider(
            id="timeline-slider",
            min=0,
            max=len(df) - 1,
            step=1,
            value=0,
            marks={i: str(df["timestamp"].iloc[i].date()) for i in range(0, len(df), max(1, len(df) // 10))},
            className="mt-3"
        )
    ])
