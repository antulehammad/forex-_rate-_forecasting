# app/dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objs as go

from utils import load_data

def render_dashboard(df):
    st.header("📊 Forex Dashboard")

    # ---- Single Currency Chart ----
    st.subheader("Historical Trend (Single Currency)")
    sel_currency = st.selectbox("Select currency", df.columns, index=0, key="single_currency")
    series = df[sel_currency].dropna()

    if not series.empty:
        fig_single = go.Figure()

        fig_single.add_trace(go.Scatter(
            x=series.index,
            y=series.values,
            mode='lines+markers',
            line=dict(color='royalblue', width=2),
            marker=dict(size=5, color='orange'),
            name=f"{sel_currency}"
        ))

        fig_single.update_layout(
            title=f"{sel_currency} Historical Trend",
            xaxis_title="Date",
            yaxis_title=f"Value ({sel_currency})",
            template="plotly_dark",
            hovermode="x unified"
        )

        st.plotly_chart(fig_single, use_container_width=True)
    else:
        st.warning("No data available for this currency.")

    st.markdown("---")

    # ---- Currency Pair Chart ----
    st.subheader("Exchange Rate Between Two Currencies")
    col1, col2 = st.columns(2)
    with col1:
        from_curr = st.selectbox("From Currency", df.columns, index=0, key="from_curr_dash")
    with col2:
        to_curr = st.selectbox("To Currency", df.columns, index=1, key="to_curr_dash")

    pair_series = (df[from_curr] / df[to_curr]).dropna()

    if not pair_series.empty:
        fig_pair = go.Figure()

        fig_pair.add_trace(go.Scatter(
            x=pair_series.index,
            y=pair_series.values,
            mode='lines+markers',
            line=dict(color='green', width=2),
            marker=dict(size=5, color='red'),
            name=f"{from_curr}/{to_curr}"
        ))

        fig_pair.update_layout(
            title=f"1 {from_curr} = ? {to_curr}",
            xaxis_title="Date",
            yaxis_title=f"Rate ({to_curr} per {from_curr})",
            template="plotly_white",
            hovermode="x unified"
        )

        st.plotly_chart(fig_pair, use_container_width=True)
    else:
        st.warning("No data available for this currency pair.")
