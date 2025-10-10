# model.py
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima

def train_sarimax(series, order=(1, 1, 1), seasonal=False, seasonal_period=12, auto=False):
    """
    Train SARIMAX or auto-ARIMA model on a time series.

    series: pd.Series with DateTimeIndex
    order: (p,d,q)
    auto: if True, automatically find best (p,d,q)
    """
    s = series.dropna()
    if s.empty:
        raise ValueError("Series is empty or all NaN")

    if auto:
        model_auto = auto_arima(
            s, start_p=1, start_q=1,
            max_p=5, max_q=5, d=None,
            seasonal=seasonal, m=seasonal_period,
            stepwise=True, suppress_warnings=True, trace=False
        )
        order = model_auto.order
        print("Auto ARIMA best order:", order)

    model = SARIMAX(s, order=order, enforce_stationarity=False, enforce_invertibility=False)
    fit = model.fit(disp=False)
    return fit

def forecast_next(model_fit, last_date, steps=30, freq="D"):
    """
    Forecast future values.
    Returns a DataFrame with mean, lower, upper forecast and dates.
    """
    forecast_res = model_fit.get_forecast(steps=steps)
    forecast_df = forecast_res.summary_frame(alpha=0.05)

    # build date index starting after last_date
    future_dates = pd.date_range(start=last_date, periods=steps+1, freq=freq)[1:]
    forecast_df.index = future_dates
    return forecast_df
