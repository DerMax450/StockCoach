# Entry file for trading
# Author: derMax450

import os
import time
import dash
from setupLogger import setup_logger
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import calculateStockData as calsd
import plotDataPlotly as pltly
import loadStockData as ldStc

app = dash.Dash(__name__)
app.title = "StockCoach"

logger = setup_logger("main", "logs/stockAnalyzer.log")

TRACKED_ASSETS = {
    "^NDX": {
        "name": "Nasdaq100",
        "start": "2020-01-01",
        "interval": "1d"
    },
    "^GSPC": {
        "name": "S&P500",
        "start": "2019-01-01",
        "interval": "1wk"
    }
}

def analyze(ticker, name, start, interval):
    print(f"\n▶ Start analysis for: {name}")
    try:
        # Check that dir exists
        os.makedirs("ticker", exist_ok=True)
        data = ldStc.load_or_initialize_data(ticker, name, start, interval)

        if data.empty:
            raise ValueError("No data found (DataFrame is empty)")

        # resolve multiIndex
        if isinstance(data.columns, pd.MultiIndex):
            print(f"[{name}] MultiIndex detected - unpack data...")
            data = data.xs(ticker, axis=1, level=1)

        # check if close value is there
        if 'Close' not in data.columns:
            raise KeyError("Column Close is missing!")
        
        logger.debug(f"[{name}] Loaded Columns: {list(data.columns)}")

        # Calculate all the indicators
        calsd.calculate_indicators(data)
        calsd.detect_crossovers(data)
        calsd.calculate_averages(data)
        calsd.calculate_medians(data)
        calsd.calculate_donchian_channel(data)
        #calsd.detect_donchian_market_phases(data)
        calsd.calculate_sma_with_band(data)
        calsd.calculate_moving_median(data)
        calsd.calculate_median_crossover(data)
        calsd.calculate_chaikin_volatility(data)

        # Save data to files
        filename = os.path.join("ticker", f"{name.replace(' ', '_')}.csv")
        data.to_csv(filename)

        return name, data

    except Exception as e:
        logger.error(f"[{name}] Fehler: {e}")

if __name__ == "__main__":
    try:
        logger.info("Starting the program...")
        while True:
            results = []
            for symbol, info in TRACKED_ASSETS.items():
                logger.info("Symbol:", symbol)
                logger.info("Name:", info["name"])
                logger.info("Startdate:", info["start"])
                logger.info("Interval:", info["interval"])
                logger.info("---------")

                # Calc all the values needed for analyze
                result = analyze(symbol, info["name"], info["start"], info["interval"])
                if result:
                    results.append(result)
                    time.sleep(10) # 10 second timeout
            if results:
                pltly.plot_candlestick_chart(results)
            time.sleep(600)  # 10 minute timeout
    except KeyboardInterrupt:
        logger.Info("Auto-Refresh stopped from user.")
