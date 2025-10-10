# forecasting.py - SARIMAX Forecasting Function

from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd

def sarimax_forecast(series, steps=12):
    """
    Forecasts future values of a time series using SARIMAX.
    
    Parameters:
        series (pd.Series): Datetime-indexed numeric series
        steps (int): Number of steps to forecast
    
    Returns:
        forecast_df (pd.DataFrame): Forecast values with confidence intervals
    """
    series = series.astype(float)  # Ensure numeric
    
    # SARIMAX order (p,d,q)
    order = (1, 1, 1)
    
    model = SARIMAX(series,
                    order=order,
                    enforce_stationarity=False,
                    enforce_invertibility=False)
    model_fit = model.fit(disp=False)
    
    forecast = model_fit.get_forecast(steps=steps)
    forecast_df = forecast.summary_frame()
    
    return forecast_df
