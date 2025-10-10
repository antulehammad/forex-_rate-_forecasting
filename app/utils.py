# utils.py
import pandas as pd
import os

def load_data(path=None, nrows=None):
    """
    Load CSV and return a cleaned wide-format DataFrame indexed by datetime.
    - If file is 'long' (has columns ['currency','exchange_rate','date']) it will pivot to wide.
    - If file is already wide (date + many currency columns) it will use as-is.
    - Converts values to numeric, forward-fills, drops all-NaN columns.
    """
    if path is None:
        root = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(root, "..", "data", "daily_forex_rates.csv")

    # read with explicit date parsing if present
    df_raw = pd.read_csv(path, parse_dates=["date"], nrows=nrows)
    # normalize column names
    df_raw.columns = [c.strip() for c in df_raw.columns]

    # If long format (common columns), pivot to wide
    long_cols = {"currency", "exchange_rate", "date"}
    if long_cols.issubset(set(df_raw.columns)):
        # pivot: index = date, columns = currency, values = exchange_rate
        df = df_raw.pivot(index="date", columns="currency", values="exchange_rate")
        # pivot produces columns as Index; make sure column names are clean strings
        df.columns = [str(c).strip() for c in df.columns]
    else:
        # If date column exists and multiple other columns, assume wide format
        if "date" in df_raw.columns:
            df = df_raw.set_index("date")
        else:
            # If there's no date column, attempt to find a first datetime-like column
            possible_date = None
            for c in df_raw.columns:
                if pd.api.types.is_datetime64_any_dtype(df_raw[c]) or df_raw[c].dtype == object:
                    # try parseable - but don't be too aggressive, keep simple
                    try:
                        parsed = pd.to_datetime(df_raw[c])
                        possible_date = c
                        break
                    except Exception:
                        continue
            if possible_date is None:
                raise KeyError("No 'date' column found and no parseable date-like column found in CSV.")
            df = df_raw.copy()
            df[possible_date] = pd.to_datetime(df[possible_date])
            df.set_index(possible_date, inplace=True)

    # Sort index and ensure datetime index
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df.sort_index()
    df = df[~df.index.isna()]  # drop rows where date couldn't be parsed

    # Convert all columns to numeric (coerce bad values -> NaN)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Forward-fill missing values (common for time series)
    df.fillna(method="ffill", inplace=True)

    # Drop any columns that are entirely NaN after cleaning
    df.dropna(axis=1, how="all", inplace=True)

    return df
