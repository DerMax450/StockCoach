# Entry file for trading – Dash-Version
# Author: derMax450

import os
import dash
from services.setupLogger import setup_logger
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import analyse.stockDataCalculator as calsd
import analyse.stockDataPredictor as pred
import analyse.chatGptAnalyzer as gptAnalyzer
import plot.plotDataPlotly as pltly
import datafeeds.marketData.yfinanceData as ldStc
from services.configLoader import load_config
import datafeeds.social.fetchX as fetchXData
import datafeeds.feed.rssFetcher as fetchRSS
import notifier.sendPushNotification as sendPush
import datafeeds.marketData.economicCalendar as ecoCal
from dash import no_update
import time

# Initialize Dash
app = dash.Dash(__name__)
app.title = "StockCoach"

# Initialize Logger
logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

api_key = load_config("jbNewsAPIKey")
helper = ecoCal.JBNewsHelper(api_key, offset=7)

# List all asseets
TRACKED_ASSETS = load_config("assets")

def calculate_indicators(name, data):
    """
    Calculate all necessary indicators for the given stock data.
    This function is called within the analyze function.
    """
    try:
        logger.info("Calculating indicators...")
        calsd.calculate_indicators(data)
        calsd.detect_crossovers(data)
        calsd.calculate_averages(data)
        calsd.calculate_medians(data)
        calsd.calculate_donchian_channel(data)
        calsd.calculate_sma_with_band(data)
        calsd.calculate_moving_median(data)
        calsd.calculate_median_crossover(data)
        calsd.calculate_chaikin_volatility(data)
        logger.info("Indicators calculated successfully.")

        logger.info("Save calculated data to file...")
        filename = os.path.join("ticker", f"{name}_calculated.csv")
        data.to_csv(filename)

        return data
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")

def calculate_predictions(name, data):
    """
    Calculate and log predictions for the given stock data.
    """
    try:
        # Calc prediction
        logger.info("Make ML prediction...")
        pred.predict_with_random_forest(data)
        pred.classify_trend_with_gradient_boosting(data)
        pred.predict_with_lstm(data)
        logger.info("Predictions calculated successfully.")

        # Save data
        logger.info("Save predicted data to file...")
        filename = os.path.join("ticker", f"{name}_predicted.csv")
        data.to_csv(filename)

        return data
    except Exception as e:
        logger.error(f"Error calculating predictions: {e}")

# Analyzer function for each asset
def analyze(ticker, name, start, interval):
    '''Analyze the stock data for a given ticker and return the processed data.
    Args:
        ticker (str): The stock ticker symbol.
        name (str): The name of the stock.
        start (str): The start date for the analysis.
        interval (str): The time interval for the stock data.
    Returns:
        tuple: A tuple containing the stock name and the processed DataFrame.
    '''

    logger.info(f"\n▶ Start analysis for: {name}")
    try:
        raw_data = ldStc.load_or_initialize_data(ticker, name, start, interval)

        if raw_data.empty:
            raise ValueError("No data found (DataFrame is empty)")

        if 'Close' not in raw_data.columns:
            raise KeyError("Column 'Close' is missing!")

        logger.debug(f"[{name}] Loaded Columns: {list(raw_data.columns)}")

        # Calc Indicators
        calc_data = calculate_indicators(name, raw_data)

        # Calculate Predictions
        predicted_data = calculate_predictions(name, calc_data)

        # Fetch RSS Data
        fetchRSS.fetch_and_store_rss_feeds(raw_data, output_dir="ticker")

        #Fetch Economic Calendar
        today_events = helper.get_calendar(today=True)

        # Generate chatGPT report
        report = gptAnalyzer.generate_report(ticker, name, calc_data)
        with open(os.path.join("ticker", f"{name.replace(' ', '_')}_report.txt"), "w") as f: f.write(report)

        # Send data to Telegram
        # sendPush.send_telegram_message(report)

        return name, raw_data, calc_data, predicted_data

    except Exception as e:
        logger.error(f"[{name}] Error: {e}")
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

# Callback: analyze and create graph
@app.callback(
    Output('chart-container', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_all_charts(n):
    logger.info(f"[Dash] Update triggered (n={n})")
    results = []

    for symbol, info in TRACKED_ASSETS.items():
        logger.info(f"Analyze {info['name']} ({symbol})")
        result = analyze(symbol, info["name"], info["start"], info["interval"])
        # Yahoo Finance rate Limit timeout
        time.sleep(5)
        if result:
            results.append(result)

    if not results:
        return no_update

    # Create foreach chart an dcc.Graph
    charts = []
    for name, calc_data, predicted_data in results:
        fig = pltly.plot_candlestick_figure(name, calc_data)
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
    logger.info("🚀 Starting Dash-Server...")
    app.run(debug=True)
