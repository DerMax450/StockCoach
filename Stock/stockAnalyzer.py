# Entry file for trading – Dash-Version
# Author: derMax450

import os
import dash
from setupLogger import setup_logger
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import calculateStockData as calsd
import plotDataPlotly as pltly
import loadStockData as ldStc
from dash import no_update

# Initialisiere Dash
app = dash.Dash(__name__)
app.title = "StockCoach"

# Logger initialisieren
logger = setup_logger("main", "logs/stockAnalyzer.log")

# Liste der beobachteten Assets
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

# Analysefunktion pro Asset
def analyze(ticker, name, start, interval):
    print(f"\n▶ Start analysis for: {name}")
    try:
        os.makedirs("ticker", exist_ok=True)
        data = ldStc.load_or_initialize_data(ticker, name, start, interval)

        if data.empty:
            raise ValueError("No data found (DataFrame is empty)")

        if isinstance(data.columns, pd.MultiIndex):
            print(f"[{name}] MultiIndex detected – unpacking...")
            data = data.xs(ticker, axis=1, level=1)

        if 'Close' not in data.columns:
            raise KeyError("Column 'Close' is missing!")

        logger.debug(f"[{name}] Loaded Columns: {list(data.columns)}")

        # Calc Indicators
        calsd.calculate_indicators(data)
        calsd.detect_crossovers(data)
        calsd.calculate_averages(data)
        calsd.calculate_medians(data)
        calsd.calculate_donchian_channel(data)
        calsd.calculate_sma_with_band(data)
        calsd.calculate_moving_median(data)
        calsd.calculate_median_crossover(data)
        calsd.calculate_chaikin_volatility(data)

        # Save data
        filename = os.path.join("ticker", f"{name.replace(' ', '_')}.csv")
        data.to_csv(filename)

        return name, data

    except Exception as e:
        logger.error(f"[{name}] Fehler: {e}")
        return None

# Dash-Layout
app.layout = html.Div(
    children=[
        html.H1("📈 StockCoach – Live Charts", style={
            "textAlign": "center",
            "marginTop": "30px",
            "marginBottom": "50px",
            "fontFamily": "Arial, sans-serif",
            "color": "#222"
        }),

        html.Div(id='chart-container', style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "gap": "60px"
        }),

        dcc.Interval(id='interval-component', interval=600 * 1000, n_intervals=0),

        html.Div("⏱️ Die Daten aktualisieren sich automatisch alle 10 Minuten.", style={
            "textAlign": "center",
            "marginTop": "40px",
            "marginBottom": "20px",
            "fontSize": "14px",
            "color": "#666"
        })
    ],
    style={"padding": "20px"}
)

# Callback: analyze and create garph
@app.callback(
    Output('chart-container', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_all_charts(n):
    logger.info(f"[Dash] Update triggered (n={n})")
    results = []

    for symbol, info in TRACKED_ASSETS.items():
        logger.info(f"Analysiere {info['name']} ({symbol})")
        result = analyze(symbol, info["name"], info["start"], info["interval"])
        if result:
            results.append(result)

    if not results:
        return no_update

    # Create foreach chart an dcc.Graph
    charts = []
    for name, data in results:
        fig = pltly.plot_candlestick_figure(name, data)
        chart = html.Div([
            html.H2(name, style={"textAlign": "center", "color": "#333", "marginBottom": "15px"}),
            dcc.Graph(
                figure=fig,
                config={"displayModeBar": True},
                style={"height": "700px", "width": "100%"}
            )
        ], style={
            "maxWidth": "1800px",
            "width": "90%",
            "padding": "20px",
            "boxShadow": "0 4px 20px rgba(0, 0, 0, 0.08)",
            "borderRadius": "10px",
            "backgroundColor": "white"
        })
        charts.append(chart)

    return charts

# Start Server
if __name__ == "__main__":
    logger.info("🚀 Starte Dash-Server...")
    app.run(debug=True)
