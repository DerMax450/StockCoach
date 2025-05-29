# Loading the stock data from Yahoo Finance
# Author: derMax450

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
from services.setupLogger import setup_logger

logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

def fetch_short_term_data(ticker, interval='1h'):
    """
    Fetches 1-hour interval stock data from Yahoo Finance.
    Yahoo only allows intraday data (like '1h') for the last ~730 days.
    """
    logger.info(f"[{ticker}] Fetching HOURLY data from {(pd.Timestamp.today() - pd.Timedelta(days=729)).strftime('%Y-%m-%d')}...")
    try:
        data = yf.download(
            ticker,
            start=(pd.Timestamp.today() - pd.Timedelta(days=729)).strftime('%Y-%m-%d'),
            end=(pd.Timestamp.today()).strftime('%Y-%m-%d'),
            interval=interval,
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        if data.empty:
            raise ValueError("No HOURLY data returned from Yahoo Finance.")
        return data
    except Exception as e:
        logger.error(f"[{ticker}] Error fetching hourly data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on failure

def fetch_long_term_data(ticker, start_date, interval='1d'):
    """
    Fetches 1-day interval stock data from Yahoo Finance.
    """
    logger.info(f"[{ticker}] Fetching DAILY data from {start_date}...")
    try:
        data = yf.download(
            ticker,
            start=start_date,
            end=(pd.Timestamp.today()).strftime('%Y-%m-%d'),
            interval=interval,
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        if data.empty:
            raise ValueError("No DAILY data returned from Yahoo Finance.")
        return data
    except Exception as e:
        logger.error(f"[{ticker}] Error fetching daily data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on failure

def load_clean_csv(filepath, start_date_fallback=None):
    """
    Loads a CSV file robustly, cleans invalid date values,
    converts data to float where possible, and returns the DataFrame + last valid date string.
    """
    if not os.path.exists(filepath):
        logger.warning(f"[CSV Loader] File not found: {filepath}")
        return pd.DataFrame(), start_date_fallback

    try:
        df = pd.read_csv(filepath)
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce', utc=False, dayfirst=False)
        df = df.dropna(subset=[df.columns[0]])
        df.set_index(df.columns[0], inplace=True)
        df = df[~df.index.duplicated(keep='last')]
        df.sort_index(inplace=True)
        df = df.apply(pd.to_numeric, errors='coerce')
        last_valid_date = df.index.max()
        if pd.isna(last_valid_date):
            logger.warning(f"[CSV Loader] No valid dates found in index. Using fallback.")
            last_date_str = start_date_fallback
        else:
            last_date_str = last_valid_date.strftime('%Y-%m-%d')
        logger.info(f"[CSV Loader] Loaded {len(df)} rows from: {filepath}")
        return df, last_date_str
    except Exception as e:
        logger.error(f"[CSV Loader] Error loading CSV file {filepath}: {e}")
        return pd.DataFrame(), start_date_fallback or pd.Timestamp.today().strftime('%Y-%m-%d')

def load_or_initialize_data(ticker, name, start_date, interval):
    directory = "ticker"
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    filename = os.path.join(directory, f"{name.replace(' ', '_')}.csv")
    combined = pd.DataFrame()

    # Choose fetcher based on interval
    fetcher = fetch_long_term_data
    if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
        fetcher = fetch_short_term_data
    else:
        fetcher = fetch_long_term_data

    if os.path.exists(filename):
        existing_data, last_date_str = load_clean_csv(filename, start_date)
        new_data = fetcher(ticker, last_date_str, interval)
        combined = pd.concat([existing_data, new_data])
    else:
        logger.info(f"[{name}] No local file found. Initial fetch from {start_date}.")
        combined = fetcher(ticker, start_date)

    if not combined.empty:
        combined = combined[~combined.index.duplicated(keep='last')]
        combined.sort_index(inplace=True)

        # Save (overwrite) CSV after merge
        # Reset index to write datetime as first column
        combined_reset = combined.reset_index()
        combined_reset.to_csv(filename, index=False)
        logger.info(f"[CSV Writer] Wrote {len(combined_reset)} rows to: {filename}")

    return combined
