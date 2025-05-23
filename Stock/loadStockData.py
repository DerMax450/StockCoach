# Loading the stock data from Yahoo Finance
# Author: derMax450

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
import time

import yfinance as yf
import pandas as pd
import os

def fetch_new_data(ticker, start_date, intervalPeriod):
    print(f"[{ticker}] Fetching data from {start_date}...")
    try:
        data = yf.download(
            ticker,
            start=start_date,
            end=pd.Timestamp.today().strftime('%Y-%m-%d'),
            interval=intervalPeriod,
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        if data.empty:
            raise ValueError("No data returned from Yahoo Finance.")
        return data
    except Exception as e:
        print(f"[{ticker}] Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on failure


def load_or_initialize_data(ticker, name, start_date, interval):
    filename = os.path.join("ticker", f"{name.replace(' ', '_')}.csv")
    combined = pd.DataFrame()

    # Load existing data if file exists
    if os.path.exists(filename):
        try:
            existing_data = pd.read_csv(filename, index_col=0, parse_dates=True)
            existing_data.index = pd.to_datetime(existing_data.index)
            print(f"[{name}] Found existing file with {len(existing_data)} rows.")

            # Get latest available date + 1 day
            last_date = existing_data.index.max() + pd.Timedelta(days=1)
            last_date_str = last_date.strftime('%Y-%m-%d')

            print(f"[{name}] Loading data from {last_date_str} to today...")
            new_data = fetch_new_data(ticker, last_date_str, interval)

            combined = pd.concat([existing_data, new_data])
        except Exception as e:
            print(f"[{name}] Failed to read existing data: {e}")
            combined = fetch_new_data(ticker, start_date, interval)
    else:
        print(f"[{name}] No local file found. Initial fetch from {start_date}.")
        combined = fetch_new_data(ticker, start_date, interval)

    if not combined.empty:
        combined = combined[~combined.index.duplicated(keep='last')]
        combined.sort_index(inplace=True)

    return combined
