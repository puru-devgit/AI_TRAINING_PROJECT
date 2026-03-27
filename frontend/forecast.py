import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.api_clients import get_forecast

st.header("📈 Demand Forecast")

data = get_forecast()
df = pd.DataFrame(data)

if df.empty:
    st.warning("No forecast data available")
else:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["predicted_demand"],
        mode="lines",
        name="Forecast"
    ))

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["upper"],
        mode="lines",
        name="Upper Bound",
        line=dict(dash='dot')
    ))

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["lower"],
        mode="lines",
        name="Lower Bound",
        line=dict(dash='dot')
    ))

    fig.update_layout(
        title="Demand Forecast",
        xaxis_title="Date",
        yaxis_title="Demand"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)