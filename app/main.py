# main.py
import streamlit as st
import pandas as pd
import os
import io
import plotly.graph_objs as go   # for interactive plots

from utils import load_data
from model import train_sarimax, forecast_next

st.set_page_config(page_title="Forex Forecasting", layout="wide")
st.title("💱 Forex Forecasting")

# 👇 ADD THIS HERE
st.markdown(
    "<a href='https://share.streamlit.io/your-username' target='_blank'>"
    "<button style='padding:10px;border-radius:10px;'>👤 View My Profile</button>"
    "</a>",
    unsafe_allow_html=True
)

# --- data path default
ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(ROOT, "..", "data", "daily_forex_rates.csv")

# Sidebar: data + performance controls
st.sidebar.header("Data & performance")
data_path = st.sidebar.text_input("CSV path", DEFAULT_DATA)
limit_rows = st.sidebar.checkbox("Limit rows for speed (dev)", value=True)
nrows = 5000 if limit_rows else None

# cache loading
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

# Flatten any tuple column names
cols = [c if not isinstance(c, tuple) else "_".join(map(str, c)) for c in df.columns]
df.columns = cols
df = df.loc[:, ~df.columns.duplicated()]   # ADD THIS LINE

# ---------------------------
# Friendly currency names
# ---------------------------
CURRENCY_NAMES = {
    "AED": "United Arab Emirates Dirham",
    "AFN": "Afghan Afghani",
    "ALL": "Albanian Lek",
    "AMD": "Armenian Dram",
    "ANG": "Netherlands Antillean Guilder",
    "AOA": "Angolan Kwanza",
    "ARS": "Argentine Peso",
    "AUD": "Australian Dollar",
    "AWG": "Aruban Florin",
    "AZN": "Azerbaijani Manat",
    "BAM": "Bosnia-Herzegovina Convertible Mark",
    "BBD": "Barbadian Dollar",
    "BDT": "Bangladeshi Taka",
    "BGN": "Bulgarian Lev",
    "BHD": "Bahraini Dinar",
    "BIF": "Burundian Franc",
    "BMD": "Bermudian Dollar",
    "BND": "Brunei Dollar",
    "BOB": "Bolivian Boliviano",
    "BRL": "Brazilian Real",
    "BSD": "Bahamian Dollar",
    "BTC": "Bitcoin",
    "BTN": "Bhutanese Ngultrum",
    "BWP": "Botswana Pula",
    "BYN": "Belarusian Ruble",
    "BYR": "Belarusian Ruble (old)",
    "BZD": "Belize Dollar",
    "CAD": "Canadian Dollar",
    "CDF": "Congolese Franc",
    "CHF": "Swiss Franc",
    "CLF": "Chilean Unit of Account (UF)",
    "CLP": "Chilean Peso",
    "CNH": "Chinese Yuan (Offshore)",
    "CNY": "Chinese Yuan",
    "COP": "Colombian Peso",
    "CRC": "Costa Rican Colón",
    "CUC": "Cuban Convertible Peso",
    "CUP": "Cuban Peso",
    "CVE": "Cape Verdean Escudo",
    "CZK": "Czech Koruna",
    "DJF": "Djiboutian Franc",
    "DKK": "Danish Krone",
    "DOP": "Dominican Peso",
    "DZD": "Algerian Dinar",
    "EGP": "Egyptian Pound",
    "ERN": "Eritrean Nakfa",
    "ETB": "Ethiopian Birr",
    "EUR": "Euro",
    "FJD": "Fijian Dollar",
    "FKP": "Falkland Islands Pound",
    "GBP": "British Pound Sterling",
    "GEL": "Georgian Lari",
    "GGP": "Guernsey Pound",
    "GHS": "Ghanaian Cedi",
    "GIP": "Gibraltar Pound",
    "GMD": "Gambian Dalasi",
    "GNF": "Guinean Franc",
    "GTQ": "Guatemalan Quetzal",
    "GYD": "Guyanese Dollar",
    "HKD": "Hong Kong Dollar",
    "HNL": "Honduran Lempira",
    "HRK": "Croatian Kuna",
    "HTG": "Haitian Gourde",
    "HUF": "Hungarian Forint",
    "IDR": "Indonesian Rupiah",
    "ILS": "Israeli New Shekel",
    "IMP": "Isle of Man Pound",
    "INR": "Indian Rupee",
    "IQD": "Iraqi Dinar",
    "IRR": "Iranian Rial",
    "ISK": "Icelandic Króna",
    "JEP": "Jersey Pound",
    "JMD": "Jamaican Dollar",
    "JOD": "Jordanian Dinar",
    "JPY": "Japanese Yen",
    "KES": "Kenyan Shilling",
    "KGS": "Kyrgyzstani Som",
    "KHR": "Cambodian Riel",
    "KMF": "Comorian Franc",
    "KPW": "North Korean Won",
    "KRW": "South Korean Won",
    "KWD": "Kuwaiti Dinar",
    "KYD": "Cayman Islands Dollar",
    "KZT": "Kazakhstani Tenge",
    "LAK": "Lao Kip",
    "LBP": "Lebanese Pound",
    "LKR": "Sri Lankan Rupee",
    "LRD": "Liberian Dollar",
    "LSL": "Lesotho Loti",
    "LTL": "Lithuanian Litas (old)",
    "LVL": "Latvian Lats (old)",
    "LYD": "Libyan Dinar",
    "MAD": "Moroccan Dirham",
    "MDL": "Moldovan Leu",
    "MGA": "Malagasy Ariary",
    "MKD": "Macedonian Denar",
    "MMK": "Burmese Kyat",
    "MNT": "Mongolian Tögrög",
    "MOP": "Macanese Pataca",
    "MRU": "Mauritanian Ouguiya",
    "MUR": "Mauritian Rupee",
    "MVR": "Maldivian Rufiyaa",
    "MWK": "Malawian Kwacha",
    "MXN": "Mexican Peso",
    "MYR": "Malaysian Ringgit",
    "MZN": "Mozambican Metical",
    "NAD": "Namibian Dollar",
    "NGN": "Nigerian Naira",
    "NIO": "Nicaraguan Córdoba",
    "NOK": "Norwegian Krone",
    "NPR": "Nepalese Rupee",
    "NZD": "New Zealand Dollar",
    "OMR": "Omani Rial",
    "PAB": "Panamanian Balboa",
    "PEN": "Peruvian Sol",
    "PGK": "Papua New Guinean Kina",
    "PHP": "Philippine Peso",
    "PKR": "Pakistani Rupee",
    "PLN": "Polish Zloty",
    "PYG": "Paraguayan Guarani",
    "QAR": "Qatari Rial",
    "RON": "Romanian Leu",
    "RSD": "Serbian Dinar",
    "RUB": "Russian Ruble",
    "RWF": "Rwandan Franc",
    "SAR": "Saudi Riyal",
    "SBD": "Solomon Islands Dollar",
    "SCR": "Seychellois Rupee",
    "SDG": "Sudanese Pound",
    "SEK": "Swedish Krona",
    "SGD": "Singapore Dollar",
    "SHP": "Saint Helena Pound",
    "SLE": "Sierra Leonean Leone (new)",
    "SLL": "Sierra Leonean Leone (old)",
    "SOS": "Somali Shilling",
    "SRD": "Surinamese Dollar",
    "STD": "São Tomé and Príncipe Dobra (old)",
    "STN": "São Tomé and Príncipe Dobra",
    "SVC": "Salvadoran Colón",
    "SYP": "Syrian Pound",
    "SZL": "Swazi Lilangeni",
    "THB": "Thai Baht",
    "TJS": "Tajikistani Somoni",
    "TMT": "Turkmenistani Manat",
    "TND": "Tunisian Dinar",
    "TOP": "Tongan Paʻanga",
    "TRY": "Turkish Lira",
    "TTD": "Trinidad and Tobago Dollar",
    "TWD": "New Taiwan Dollar",
    "TZS": "Tanzanian Shilling",
    "UAH": "Ukrainian Hryvnia",
    "UGX": "Ugandan Shilling",
    "USD": "United States Dollar",
    "UYU": "Uruguayan Peso",
    "UZS": "Uzbekistani Som",
    "VES": "Venezuelan Bolívar Soberano",
    "VND": "Vietnamese Dong",
    "VUV": "Vanuatu Vatu",
    "WST": "Samoan Tala",
    "XAF": "Central African CFA Franc",
    "XAG": "Silver (Troy Ounce)",
    "XAU": "Gold (Troy Ounce)",
    "XCD": "East Caribbean Dollar",
    "XCG": "Crypto Generic / Test (if needed)",
    "XDR": "IMF Special Drawing Rights",
    "XOF": "West African CFA Franc",
    "XPF": "CFP Franc (French Polynesia)",
    "YER": "Yemeni Rial",
    "ZAR": "South African Rand",
    "ZMK": "Zambian Kwacha (old)",
    "ZMW": "Zambian Kwacha",
    "ZWL": "Zimbabwean Dollar",
}

def code_to_label(code):
    name = CURRENCY_NAMES.get(code, None)
    if name:
        return f"{code} — {name}"
    else:
        return f"{code}"

display_labels = [code_to_label(c) for c in cols if c not in ["date"]]
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

last_from_series = df[from_curr].dropna()
last_to_series = df[to_curr].dropna()

if not last_from_series.empty and not last_to_series.empty:
    rate_from_latest = last_from_series.iloc[-1]
    rate_to_latest = last_to_series.iloc[-1]

    # ✅ FIX: invert so it shows 1 FROM = X TO
    converted = (amount * rate_to_latest) / rate_from_latest

    st.sidebar.markdown(f"**{amount:,.4f} {from_curr} = {converted:,.4f} {to_curr}**")
    st.sidebar.caption(f"Using latest data at {last_from_series.index[-1].date()}")
else:
    st.sidebar.warning("One of the selected currencies has no recent data; converter disabled.")

# ---------------------------
# Date range helper
# ---------------------------
def get_range_from_preset(series_index, preset):
    end = series_index.max()
    if preset == "1M":
        start = end - pd.DateOffset(months=1)
    elif preset == "3M":
        start = end - pd.DateOffset(months=3)
    elif preset == "6M":
        start = end - pd.DateOffset(months=6)
    elif preset == "1Y":
        start = end - pd.DateOffset(years=1)
    elif preset == "All":
        start = series_index.min()
    else:
        start = series_index.min()
    return (start, end)

# ---------------------------
# Layout
# ---------------------------
left_col, right_col = st.columns([2, 1])

with left_col:
    # ----------------- Single currency plot -----------------
    st.subheader("📊 Historical series (single currency)")
    sel_label = st.selectbox("Select currency to view", display_labels, index=0, key="main_select")
    sel_currency = label_to_code[sel_label]
    s = df[sel_currency].dropna()

    if not s.empty:
        preset = st.selectbox("Preset", ["1M", "3M", "6M", "1Y", "All", "Custom"], index=1, key="preset_single")
        if preset != "Custom":
            start, end = get_range_from_preset(s.index, preset)
        else:
            start, end = st.date_input("Custom range", [s.index.max() - pd.DateOffset(months=1), s.index.max()])
            start, end = pd.to_datetime(start), pd.to_datetime(end)

        start, end = max(start, s.index.min()), min(end, s.index.max())
        to_plot = s.loc[start:end]

        if not to_plot.empty:
            fig_single = go.Figure()
            fig_single.add_trace(go.Scatter(
                x=to_plot.index, y=to_plot.values,
                mode="lines+markers",
                line=dict(color="royalblue", width=2),
                marker=dict(size=5, color="orange"),
                name=sel_currency
            ))
            fig_single.update_layout(
                title=f"{sel_label} Historical Trend",
                xaxis_title="Date", yaxis_title=f"Value ({sel_currency})",
                template="plotly_dark", hovermode="x unified"
            )
            st.plotly_chart(fig_single, use_container_width=True)

    st.markdown("---")

    # ----------------- Pair series -----------------
    st.subheader("📉 Exchange rate between two currencies (FROM → TO)")
    st.write(f"Displays 1 {from_curr} in units of {to_curr}")

    # ✅ FIX: invert so it's FROM → TO
    pair_series = (df[to_curr] / df[from_curr]).dropna()

    if not pair_series.empty:
        preset_pair = st.selectbox("Preset (pair)", ["1M", "3M", "6M", "1Y", "All", "Custom"], index=1, key="preset_pair")
        if preset_pair != "Custom":
            p_start, p_end = get_range_from_preset(pair_series.index, preset_pair)
        else:
            p_start, p_end = st.date_input("Custom range for pair", [pair_series.index.max() - pd.DateOffset(months=1), pair_series.index.max()])
            p_start, p_end = pd.to_datetime(p_start), pd.to_datetime(p_end)

        p_start, p_end = max(p_start, pair_series.index.min()), min(p_end, pair_series.index.max())
        pair_to_plot = pair_series.loc[p_start:p_end]

        if not pair_to_plot.empty:
            fig_pair = go.Figure()
            fig_pair.add_trace(go.Scatter(
                x=pair_to_plot.index, y=pair_to_plot.values,
                mode="lines+markers",
                line=dict(color="white", width=2),
                marker=dict(size=5, color="red"),
                name=f"{from_curr}/{to_curr}"
            ))
            fig_pair.update_layout(
                title=f"1 {from_curr} = ? {to_curr}",
                xaxis_title="Date", yaxis_title=f"Rate ({to_curr} per {from_curr})",
                template="plotly_white", hovermode="x unified"
            )
            st.plotly_chart(fig_pair, use_container_width=True)

with right_col:
    # ----------------- Forecast -----------------
    st.subheader("🔮 Forecast (pair series)")
    st.write("Forecast the exchange rate BETWEEN two currencies.")

    steps = st.number_input("Forecast steps", min_value=1, max_value=365, value=30)
    freq = st.selectbox("Frequency", ["D", "W", "M"], index=0)
    p = st.number_input("AR p", 0, 5, 1)
    d = st.number_input("Diff d", 0, 2, 1)
    q = st.number_input("MA q", 0, 5, 1)

    auto_mode = st.checkbox("Auto-select ARIMA order", value=True)
    seasonal = st.checkbox("Seasonal", value=False)
    seasonal_m = st.number_input("Seasonal period (m)", 0, 365, 12)

    if st.button("Run forecast"):
        pair_series_full = (df[to_curr] / df[from_curr]).dropna()

        # ✅ FIX: force 1D series
        if isinstance(pair_series_full, pd.DataFrame):
            pair_series_full = pair_series_full.iloc[:, 0]

        pair_series_full = pair_series_full.squeeze()

        if pair_series_full.shape[0] >= 10:
            with st.spinner("Training SARIMAX..."):
                try:
                    model_fit = train_sarimax(
                        pair_series_full,
                        order=(p, d, q),
                        seasonal=seasonal,
                        seasonal_period=seasonal_m,
                        auto=auto_mode
                    )
                except Exception as e:
                    st.error(f"Model training failed: {e}")
                    model_fit = None

            if model_fit:
                last_date = pair_series_full.index[-1]
                try:
                    forecast_df = forecast_next(model_fit, last_date, steps=steps, freq=freq)
                except Exception as e:
                    st.error(f"Forecasting failed: {e}")
                    forecast_df = None

                if forecast_df is not None:
                    st.success("Forecast ready ✅")
                    st.dataframe(forecast_df.head())

                    # Interactive Plotly forecast
                    hist_to_plot = pair_series_full.tail(200)
                    fig_forecast = go.Figure()
                    fig_forecast.add_trace(go.Scatter(
                        x=hist_to_plot.index, y=hist_to_plot.values,
                        mode="lines", name="Historical", line=dict(color="cyan")
                    ))
                    fig_forecast.add_trace(go.Scatter(
                        x=forecast_df.index, y=forecast_df["mean"],
                        mode="lines+markers", name="Forecast", line=dict(color="orange")
                    ))
                    if "mean_ci_lower" in forecast_df and "mean_ci_upper" in forecast_df:
                        fig_forecast.add_trace(go.Scatter(
                            x=forecast_df.index.tolist() + forecast_df.index[::-1].tolist(),
                            y=forecast_df["mean_ci_upper"].tolist() + forecast_df["mean_ci_lower"][::-1].tolist(),
                            fill="toself", fillcolor="rgba(255,165,0,0.2)",
                            line=dict(color="rgba(255,255,255,0)"), showlegend=True, name="95% CI"
                        ))
                    fig_forecast.update_layout(
                        title=f"Forecast: 1 {from_curr} → {to_curr}",
                        xaxis_title="Date", yaxis_title=f"Rate ({to_curr} per {from_curr})",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_forecast, use_container_width=True)

                    # Download CSV
                    csv_buffer = io.StringIO()
                    forecast_df.to_csv(csv_buffer)
                    st.download_button("Download forecast CSV", csv_buffer.getvalue(),
                                       file_name=f"forecast_{from_curr}_to_{to_curr}.csv", mime="text/csv")
