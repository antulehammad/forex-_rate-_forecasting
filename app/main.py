# main.py
import streamlit as st
import pandas as pd
import os
import io
import plotly.graph_objs as go

from utils import load_data
from model import train_sarimax, forecast_next

st.set_page_config(page_title="Forex Forecasting", layout="wide")
st.title("💱 Forex Forecasting")

st.markdown(
    "<a href='https://share.streamlit.io/antulehammad' target='_blank'>"
    "<button style='padding:10px;border-radius:10px;'>👤 View My Profile</button>"
    "</a>",
    unsafe_allow_html=True
)

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(ROOT, "..", "data", "daily_forex_rates.csv")

st.sidebar.header("Data & performance")
data_path = st.sidebar.text_input("CSV path", DEFAULT_DATA)
limit_rows = st.sidebar.checkbox("Limit rows for speed (dev)", value=True)
nrows = 5000 if limit_rows else None

@st.cache_data
def get_data(path, nrows):
    return load_data(path, nrows=nrows)

try:
    df = get_data(data_path, nrows)
except Exception as e:
    st.error(f"Failed to load CSV: {e}")
    st.stop()

if df.empty:
    st.error("Loaded dataframe is empty after cleaning.")
    st.stop()

cols = [c if not isinstance(c, tuple) else "_".join(map(str, c)) for c in df.columns]
df.columns = cols
df = df.loc[:, ~df.columns.duplicated()]

# 🔥 IMPORTANT FIX: ensure numeric
for col in df.columns:
    if col != "date":
        df[col] = pd.to_numeric(df[col], errors="coerce")

def code_to_label(code):
    return code

display_labels = [code_to_label(c) for c in cols if c != "date"]
label_to_code = {label: code for label, code in zip(display_labels, cols) if code != "date"}

st.sidebar.subheader("Data info")
st.sidebar.write(f"Rows: {len(df)}  Columns: {len(cols)}")

# ---------------------------
# Converter
# ---------------------------
st.sidebar.subheader("Currency Converter")
from_label = st.sidebar.selectbox("From", display_labels, index=0)
to_label = st.sidebar.selectbox("To", display_labels, index=1 if len(display_labels) > 1 else 0)

from_curr = label_to_code[from_label]
to_curr = label_to_code[to_label]

amount = st.sidebar.number_input("Amount (in FROM)", min_value=0.0, value=1.0, step=1.0)

last_from_series = df[from_curr].replace(0, pd.NA).dropna()
last_to_series = df[to_curr].replace(0, pd.NA).dropna()

if not last_from_series.empty and not last_to_series.empty:
    rate_from_latest = last_from_series.iloc[-1]
    rate_to_latest = last_to_series.iloc[-1]

    converted = (amount * rate_to_latest) / rate_from_latest

    st.sidebar.markdown(f"**{amount:,.4f} {from_curr} = {converted:,.4f} {to_curr}**")
    st.sidebar.caption(f"Using latest data at {last_from_series.index[-1].date()}")
else:
    st.sidebar.warning("Converter disabled due to invalid data")

# ---------------------------
# Layout
# ---------------------------
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("📊 Historical series")

    sel_label = st.selectbox("Select currency", display_labels)
    sel_currency = label_to_code[sel_label]

    s = df[sel_currency].dropna()

    if not s.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("📉 Pair (FROM → TO)")

    pair_series = (df[to_curr] / df[from_curr])

    # 🔥 FIX: clean data
    pair_series = pair_series.replace([float("inf"), float("-inf")], pd.NA)
    pair_series = pair_series.dropna()

    if not pair_series.empty:
        fig_pair = go.Figure()
        fig_pair.add_trace(go.Scatter(x=pair_series.index, y=pair_series.values))
        st.plotly_chart(fig_pair, use_container_width=True)

with right_col:
    st.subheader("🔮 Forecast")

    steps = st.number_input("Steps", 1, 365, 30)
    freq = st.selectbox("Freq", ["D", "W", "M"])
    p = st.number_input("p", 0, 5, 1)
    d = st.number_input("d", 0, 2, 1)
    q = st.number_input("q", 0, 5, 1)

    auto_mode = st.checkbox("Auto", True)

    if st.button("Run forecast"):

        pair_series_full = (df[to_curr] / df[from_curr])

        # 🔥 CRITICAL FIX BLOCK
        pair_series_full = pair_series_full.replace([float("inf"), float("-inf")], pd.NA)
        pair_series_full = pair_series_full.replace(0, pd.NA)
        pair_series_full = pair_series_full.dropna()
        pair_series_full = pair_series_full.astype(float)
        pair_series_full = pair_series_full.squeeze()

        if len(pair_series_full) < 20:
            st.error("Not enough clean data for forecasting")
            st.stop()

        if pair_series_full.nunique() < 5:
            st.error("Data has no variation")
            st.stop()

        try:
            model_fit = train_sarimax(
                pair_series_full,
                order=(p, d, q),
                seasonal=False,
                seasonal_period=12,
                auto=auto_mode
            )
        except Exception as e:
            st.error(f"Training failed: {e}")
            st.stop()

        try:
            last_date = pair_series_full.index[-1]
            forecast_df = forecast_next(model_fit, last_date, steps=steps, freq=freq)
        except Exception as e:
            st.error(f"Forecast failed: {e}")
            st.stop()

        # 🔥 FIX: ensure valid output
        if forecast_df is None or forecast_df.empty:
            st.error("Forecast returned empty results")
            st.stop()

        if forecast_df["mean"].isnull().all():
            st.error("Model produced invalid predictions")
            st.stop()

        st.success("Forecast ready")
        st.dataframe(forecast_df.head())

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=pair_series_full.tail(200).index,
                                 y=pair_series_full.tail(200).values,
                                 name="History"))
        fig.add_trace(go.Scatter(x=forecast_df.index,
                                 y=forecast_df["mean"],
                                 name="Forecast"))
        st.plotly_chart(fig, use_container_width=True)

        csv_buffer = io.StringIO()
        forecast_df.to_csv(csv_buffer)

        st.download_button(
            "Download CSV",
            csv_buffer.getvalue(),
            file_name=f"forecast_{from_curr}_{to_curr}.csv"
        )
