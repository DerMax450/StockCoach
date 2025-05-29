import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
import time
import Stock.analyse.stockDataCalculator as cals
from services.setupLogger import setup_logger

logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

def plot_all_data_interactive(results):
    for name, data, bullish, bearish in results:
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name="Price", line=dict(color='black')))
        fig.add_trace(go.Scatter(x=data.index, y=data['50_MA'], name="50-day MA", line=dict(dash='dash', color='blue')))
        fig.add_trace(go.Scatter(x=data.index, y=data['200_MA'], name="200-day MA", line=dict(dash='dash', color='orange')))
        fig.add_trace(go.Scatter(x=bullish.index, y=bullish['Close'], mode='markers', name='Bullish Crossover',
                                 marker=dict(symbol='triangle-up', size=10, color='green')))
        fig.add_trace(go.Scatter(x=bearish.index, y=bearish['Close'], mode='markers', name='Bearish Crossover',
                                 marker=dict(symbol='triangle-down', size=10, color='red')))

        fig.update_layout(
            title=f"{name}: Preis mit 50/200 MA und Crossovers",
            xaxis_title="Datum",
            yaxis_title="Preis",
            legend=dict(x=0, y=1.2),
            hovermode="x unified"
        )

        fig.show()

def plot_all_data(results):
    n = len(results)
    fig, axes = plt.subplots(nrows=n, ncols=1, figsize=(14, 5 * n), squeeze=False)

    for idx, (name, data, bullish, bearish) in enumerate(results):
        ax = axes[idx][0]
        ax.plot(data.index, data['Close'], label="Price", color="black", linewidth=1)
        ax.plot(data.index, data['50_MA'], label="50-day MA", linestyle='--', color='blue')
        ax.plot(data.index, data['200_MA'], label="200-day MA", linestyle='--', color='orange')
        ax.scatter(bullish.index, bullish['Close'], marker='^', color='green', label='Bullish Crossover', s=60)
        ax.scatter(bearish.index, bearish['Close'], marker='v', color='red', label='Bearish Crossover', s=60)
        ax.set_title(f"{name}: Preis mit 50/200 MA")
        ax.set_xlabel("Datum")
        ax.set_ylabel("Preis")
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    plt.show()