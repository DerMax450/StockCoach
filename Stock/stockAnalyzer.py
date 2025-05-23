import os
import time
import pandas as pd
import calculateStockData as calsd
import plotDataPlotly as pltly
import loadStockData as ldStc

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
        # Stelle sicher, dass der Ordner existiert
        os.makedirs("ticker", exist_ok=True)
        data = ldStc.load_or_initialize_data(ticker, name, start, interval)

        if data.empty:
            raise ValueError("No data found (DataFrame is empty)")

        # MultiIndex auflösen, falls vorhanden
        if isinstance(data.columns, pd.MultiIndex):
            print(f"[{name}] MultiIndex detected - unpack data...")
            data = data.xs(ticker, axis=1, level=1)

        print(f"[{name}] Loaded Columns: {list(data.columns)}")

        if 'Close' not in data.columns:
            raise KeyError("Column Close is missing!")

        if data.empty:
            raise ValueError("No usable data found.")

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
        print(f"[{name}] Fehler: {e}")

if __name__ == "__main__":
    try:
        while True:
            results = []
            for symbol, info in TRACKED_ASSETS.items():
                print("Symbol:", symbol)
                print("Name:", info["name"])
                print("Startdate:", info["start"])
                print("Interval:", info["interval"])
                print("---------")
                result = analyze(symbol, info["name"], info["start"], info["interval"])
                if result:
                    results.append(result)
                    time.sleep(10)
            if results:
                pltly.plot_candlestick_chart(results)
            time.sleep(600)  # 10 Minuten warten
    except KeyboardInterrupt:
        print("Auto-Refresh gestoppt vom Benutzer.")
