# Plot the figures with plotly, recently updatin to make ot live with "dash"
# Author: derMax450

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from services.setupLogger import setup_logger

logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

# Add Median Line
def add_median(fig, data, window=50):
    label = f'Median_{window}'
    if label in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, y=data[label],
            name=label,
            line=dict(color='red', dash='dot')
        ))

# Add Average Line
def add_average(fig, data, window=50):
    label = f'Average_{window}'
    if label in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, y=data[label],
            name=label,
            line=dict(color='green', dash='dot')
        ))

# Add Donchian Channel
def add_donchian_channel(fig, data, window=20):
    upper_label = f'DC_Upper_{window}'
    lower_label = f'DC_Lower_{window}'
    mid_label = f'DC_Mid_{window}'

    if upper_label in data.columns and lower_label in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, y=data[upper_label],
            line=dict(color='purple', width=1),
            name=f'Donchian Upper {window}'
        ))
        fig.add_trace(go.Scatter(
            x=data.index, y=data[lower_label],
            line=dict(color='purple', width=1),
            name=f'Donchian Lower {window}',
            fill='tonexty',
            fillcolor='rgba(128, 0, 128, 0.1)'
        ))
        fig.add_trace(go.Scatter(
            x=data.index, y=data[mid_label],
            line=dict(color='purple', dash='dot'),
            name=f'Donchian Mid {window}'
        ))

# Add Moving Averages
def add_moving_average(fig, data, window=50):
    label = f'SMA_{window}'
    if label in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, y=data[label],
            line=dict(color='blue', dash='dot'),
            name=label
        ))

# Add SMA Bands (+/- X%)
def add_sma_band(fig, data, window=50, percent=2.0):
    upper_label = f'SMA_{window}_upper_{percent}'
    lower_label = f'SMA_{window}_lower_{percent}'

    if upper_label in data.columns and lower_label in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, y=data[upper_label],
            line=dict(color='blue', width=1),
            name=f'SMA {window} +{percent}%'
        ))
        fig.add_trace(go.Scatter(
            x=data.index, y=data[lower_label],
            line=dict(color='blue', width=1),
            name=f'SMA {window} -{percent}%',
            fill='tonexty',
            fillcolor='rgba(0, 0, 255, 0.1)'
        ))

# Add Chaikin Volatility
def add_chaikin_volatility(fig, data, ema_period=100):
    label = f'Chaikin_Volatility_{ema_period}'
    if label in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, y=data[label],
            name=f'Chaikin Volatility {ema_period}',
            line=dict(color='magenta')
        ))

def add_rf_prediction(fig, data):
    if 'RF_Prediction' in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, y=data['RF_Prediction'],
            name="RF Prediction",
            mode='lines',
            line=dict(color='orange', dash='dash')
        ))

def add_trend_prediction(fig, data):
    if 'TrendPrediction' in data.columns:
        color_map = {0: 'red', 1: 'green'}
        fig.add_trace(go.Scatter(
            x=data.index, y=data['Close'],
            name="Trend Prediction",
            mode='markers',
            marker=dict(
                color=data['TrendPrediction'].map(color_map),
                size=6,
                symbol='triangle-up'
            ),
            showlegend=True
        ))

def add_lstm_prediction(fig, data, future_days=5):
    col = f'LSTM_Pred_{future_days}d'
    if col in data.columns:
        fig.add_trace(go.Scatter(
            x=data.index, y=data[col],
            name=f"LSTM Prediction ({future_days}d)",
            mode='markers',
            marker=dict(color='blue', size=10, symbol='x'),
            showlegend=True
        ))


# Hauptfunktion zum Erstellen der Candlestick-Charts mit allen Indikatoren
def plot_candlestick_figure(name, data):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'],
        name="Candles"
    ))

    # alle add_* Methoden wie gehabt
    add_median(fig, data, window=50)
    add_average(fig, data, window=50)
    add_donchian_channel(fig, data, window=20)
    add_moving_average(fig, data, window=50)
    add_moving_average(fig, data, window=200)
    add_sma_band(fig, data, window=50, percent=2.0)
    add_chaikin_volatility(fig, data, ema_period=100)

    # ML-Predictions
    add_rf_prediction(fig, data)
    add_trend_prediction(fig, data)
    add_lstm_prediction(fig, data, future_days=5)

    fig.update_layout(
        title=f"{name} - Candlestick Chart",
        xaxis_title="Datum",
        yaxis_title="Preis",
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )
    return fig

