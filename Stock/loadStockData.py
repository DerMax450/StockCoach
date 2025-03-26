import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
import time

def fetch_new_data(ticker, start_date, intervalPeriod):
    print(f"[{ticker}] Lade Daten ab {start_date}...")
    data = yf.download(ticker, start=start_date, end=pd.Timestamp.today().strftime('%Y-%m-%d'), interval=intervalPeriod, auto_adjust=True)
    return data

def load_or_initialize_data(ticker, name, start_date, interval):
    filename = os.path.join("ticker", f"{name.replace(' ', '_')}.csv")

    if os.path.exists(filename):
        existing_data = pd.read_csv(filename, index_col=0, parse_dates=True)
        first_date = existing_data.index.min().strftime('%Y-%m-%d')
        earliest = yf.Ticker(ticker).history(period="max").index.min().strftime('%Y-%m-%d')
        print(f'Earliest date for {name}: {earliest}')
        if(first_date == start_date):
            last_date = existing_data.index.max() + pd.Timedelta(days=1)
            new_data = fetch_new_data(ticker, last_date.strftime('%Y-%m-%d'), interval)
            combined = pd.concat([existing_data, new_data])
            combined = combined[~combined.index.duplicated(keep='last')]
        else:
            combined = fetch_new_data(ticker, start_date, interval)
    else: 
        combined = fetch_new_data(ticker, start_date, interval)
    return combined