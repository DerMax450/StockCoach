# Calculation Methods
# Author: derMax450

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf
from setupLogger import setup_logger

logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

def calculate_indicators(data, short_window=50, long_window=200):
    data[f'SMA_{short_window}'] = data['Close'].rolling(window=short_window).mean()
    data[f'SMA_{long_window}'] = data['Close'].rolling(window=long_window).mean()
    return data

def detect_crossovers(data, short_window=50, long_window=200):
    sma_short = f'SMA_{short_window}'
    sma_long = f'SMA_{long_window}'

    data['Trend'] = 'Hold'
    data.loc[data[sma_short] > data[sma_long], 'Trend'] = 'Bullish'
    data.loc[data[sma_short] < data[sma_long], 'Trend'] = 'Bearish'
    data['Crossover'] = data['Trend'].ne(data['Trend'].shift())

    bullish = data[(data['Crossover']) & (data['Trend'] == 'Bullish')]
    bearish = data[(data['Crossover']) & (data['Trend'] == 'Bearish')]
    return bullish, bearish

def calculate_medians(data, window=50):
    label = f'Median_{window}'
    data[label] = data['Close'].rolling(window=window).median()
    return data

def calculate_averages(data, window=50):
    label = f'Average_{window}'
    data[label] = data['Close'].rolling(window=window).mean()
    return data

def calculate_donchian_channel(data, window=20):
    data[f'DC_Upper_{window}'] = data['High'].rolling(window=window).max()
    data[f'DC_Lower_{window}'] = data['Low'].rolling(window=window).min()
    data[f'DC_Mid_{window}'] = (data[f'DC_Upper_{window}'] + data[f'DC_Lower_{window}']) / 2
    return data

def detect_donchian_market_phases(data, high_window=90, low_window=200):
    new_high_col = f'NewHigh_{high_window}'
    new_low_col = f'NewLow_{low_window}'
    phase_col = f'MarketPhase_{high_window}_{low_window}'

    data[new_high_col] = data['High'] == data['High'].rolling(high_window).max()
    data[new_low_col] = data['Low'] == data['Low'].rolling(low_window).min()

    def classify(row):
        if row[new_high_col] and not row[new_low_col]:
            return 'Bullish'
        elif row[new_low_col] and not row[new_high_col]:
            return 'Bearish'
        else:
            return 'Neutral'

    data[phase_col] = data.apply(classify, axis=1)
    return data

def calculate_sma_with_band(data, window=50, percent=2.0):
    sma_label = f'SMA_{window}'
    upper_label = f'{sma_label}_upper_{percent}'
    lower_label = f'{sma_label}_lower_{percent}'

    data[sma_label] = data['Close'].rolling(window=window).mean()
    factor = percent / 100.0
    data[upper_label] = data[sma_label] * (1 + factor)
    data[lower_label] = data[sma_label] * (1 - factor)
    return data

def calculate_moving_median(data, window=50):
    label = f'Median_{window}'
    data[label] = data['Close'].rolling(window=window).median()
    return data

def calculate_median_crossover(data, sma_window=50, median_window=50):
    sma_label = f'SMA_{sma_window}'
    median_label = f'Median_{median_window}'
    diff_label = f'SMA_vs_Median_{sma_window}_{median_window}'
    cross_label = f'Median_Crossover_{sma_window}_{median_window}'

    data[diff_label] = data[sma_label] - data[median_label]
    data[cross_label] = data[diff_label].apply(
        lambda x: 'Above' if x > 0 else ('Below' if x < 0 else 'Equal')
    )
    return data

def calculate_chaikin_volatility(data, ema_period=100):
    range_label = f'HL_range'
    chaikin_label = f'Chaikin_Volatility_{ema_period}'

    data[range_label] = data['High'] - data['Low']
    data[chaikin_label] = data[range_label].ewm(span=ema_period, adjust=False).mean()
    return data

## Machine Learning
def predict_with_random_forest(data, future_days=5):
    data = data.copy()
    data['FutureClose'] = data['Close'].shift(-future_days)
    data.dropna(inplace=True)

    features = ['Close', 'Volume'] + [col for col in data.columns if 'SMA' in col or 'Median' in col]
    X = data[features]
    y = data['FutureClose']

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    data.loc[X_test.index, 'RF_Prediction'] = model.predict(X_test)
    return data

def classify_trend_with_gradient_boosting(data, future_days=1):
    data = data.copy()
    data['FutureClose'] = data['Close'].shift(-future_days)
    data['TrendUp'] = (data['FutureClose'] > data['Close']).astype(int)
    data.dropna(inplace=True)

    features = ['Close', 'Volume'] + [col for col in data.columns if 'SMA' in col or 'Median' in col]
    X = data[features]
    y = data['TrendUp']

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    model = GradientBoostingClassifier()
    model.fit(X_train, y_train)

    data.loc[X_test.index, 'TrendPrediction'] = model.predict(X_test)
    return data

def predict_with_lstm(data, lookback=30, future_days=5, epochs=10):
    df = data[['Close']].copy()
    df['Target'] = df['Close'].shift(-future_days)
    df.dropna(inplace=True)

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df)

    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i - lookback:i, 0])
        y.append(scaled_data[i, 1])
    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(50, return_sequences=False, input_shape=(X.shape[1], 1)),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=epochs, verbose=0)

    # Letzte Sequenz als Vorhersagebasis
    last_seq = scaled_data[-lookback:, 0].reshape(1, lookback, 1)
    prediction = model.predict(last_seq)[0][0]
    prediction = scaler.inverse_transform([[0, prediction]])[0][1]
    
    data.at[data.index[-1], f'LSTM_Pred_{future_days}d'] = prediction
    return data
