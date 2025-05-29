# Calculation Methods
# Author: derMax450

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf
from services.setupLogger import setup_logger

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
    cross_num_label = f'{cross_label}_num'

    # Diffrence
    data[diff_label] = data[sma_label] - data[median_label]

    # Classification as text (Above/Below/Equal)
    data[cross_label] = data[diff_label].apply(
        lambda x: 'Above' if x > 0 else ('Below' if x < 0 else 'Equal')
    )

    # Numerical version for Machine Learning
    mapping = {'Above': 1, 'Below': -1, 'Equal': 0}
    data[cross_num_label] = data[cross_label].map(mapping)

    return data

def calculate_chaikin_volatility(data, ema_period=100):
    range_label = f'HL_range'
    chaikin_label = f'Chaikin_Volatility_{ema_period}'

    data[range_label] = data['High'] - data['Low']
    data[chaikin_label] = data[range_label].ewm(span=ema_period, adjust=False).mean()
    return data
## Machine Learning Algorithms

def validate_ml_data(df, required_features=None, min_rows=10, label_column=None, context="ML"):
    logger.debug(f"[{context}] DataFrame shape: {df.shape}")
    logger.debug(f"[{context}] DataFrame columns: {list(df.columns)}")
    if df.empty:
        logger.warning(f"[{context}] DataFrame is empty – skipping.")
        return False

    if len(df) < min_rows:
        logger.warning(f"[{context}] Not enough rows ({len(df)} < {min_rows}) – skipping.")
        logger.info(f"[{context}] DataFrame head:\n{df.head(5)}")
        return False

    if required_features:
        for f in required_features:
            if f not in df.columns:
                logger.warning(f"[{context}] Required feature missing: {f}")
                logger.info(f"[{context}] Available columns: {list(df.columns)}")
                return False
            if df[f].isna().any():
                n_nan = df[f].isna().sum()
                logger.warning(f"[{context}] Feature '{f}' contains {n_nan} NaNs.")
                logger.info(f"[{context}] Example NaN rows in '{f}':\n{df[df[f].isna()].head(5)}")
                return False

    if label_column:
        if label_column not in df.columns or df[label_column].isna().any():
            logger.warning(f"[{context}] Label column '{label_column}' missing or invalid.")
            if label_column not in df.columns:
                logger.info(f"[{context}] Columns: {list(df.columns)}")
            else:
                logger.info(f"[{context}] Example NaN rows in label:\n{df[df[label_column].isna()].head(5)}")
            return False

    logger.debug(f"[{context}] Data passed validation.")
    return True

def predict_with_random_forest(data, future_days=5):
    logger.info("[RandomForest] --- Predicting with RandomForest ---")
    logger.debug(f"[RandomForest] Input shape: {data.shape}")
    data = data.copy()
    data['FutureClose'] = data['Close'].shift(-future_days)
    data.dropna(subset=['Close', 'Volume', 'FutureClose'], inplace=True)
    logger.debug(f"[RandomForest] Shape after shift/dropna: {data.shape}")

    features = ['Close', 'Volume']
    context = "RandomForest"

    if not validate_ml_data(data, required_features=features, min_rows=10, label_column='FutureClose', context=context):
        logger.info(f"[{context}] Data after failed validation:\n{data.head(5)}")
        return data

    X = data[features]
    y = data['FutureClose']

    logger.debug(f"[{context}] Features head:\n{X.head(3)}")
    logger.debug(f"[{context}] Target head:\n{y.head(3)}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    logger.debug(f"[{context}] X_train: {X_train.shape}, X_test: {X_test.shape}")

    if len(X_train) < 5:
        logger.warning(f"[{context}] Too few training samples – skipping.")
        return data

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    logger.info(f"[{context}] Model trained. Predicting...")
    data.loc[X_test.index, 'RF_Prediction'] = model.predict(X_test)
    logger.info(f"[{context}] Prediction done. Data shape: {data.shape}")

    return data

def classify_trend_with_gradient_boosting(data, future_days=1):
    logger.info("[TrendBoost] --- Classify trend with GradientBoosting ---")
    logger.debug(f"[TrendBoost] Initial rows: {len(data)}")
    logger.debug(f"[TrendBoost] Input shape: {data.shape}")
    logger.debug(f"[TrendBoost] Columns: {list(data.columns)}")

    data = data.copy()
    data['FutureClose'] = data['Close'].shift(-future_days)
    data['TrendUp'] = (data['FutureClose'] > data['Close']).astype(int)
    logger.debug(f"[TrendBoost] Rows after shift: {len(data)}")
    logger.debug(f"[TrendBoost] Columns after new features: {list(data.columns)}")
    data.dropna(inplace=True)
    logger.debug(f"[TrendBoost] Rows after dropna: {len(data)}")
    logger.debug(f"[TrendBoost] Data after dropna:\n{data.head(5)}")

    features = ['Close', 'Volume'] + [
        col for col in data.columns
        if ('SMA' in col or 'Median' in col) and data[col].dtype != 'object'
    ]
    features = [f for f in features if f in data.columns]
    logger.debug(f"[TrendBoost] Feature list: {features}")

    context = "TrendBoost"
    if not validate_ml_data(data, required_features=features, min_rows=10, label_column='TrendUp', context=context):
        logger.info(f"[{context}] Data after failed validation:\n{data.head(5)}")
        return data

    X = data[features]
    y = data['TrendUp']
    logger.debug(f"[{context}] X head:\n{X.head(3)}")
    logger.debug(f"[{context}] y head:\n{y.head(3)}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    logger.debug(f"[{context}] X_train: {X_train.shape}, X_test: {X_test.shape}")

    if len(X_train) < 5:
        logger.warning(f"[{context}] Too few samples for training – skipping.")
        return data

    model = GradientBoostingClassifier()
    model.fit(X_train, y_train)
    logger.info(f"[{context}] Model trained. Predicting...")
    data.loc[X_test.index, 'TrendPrediction'] = model.predict(X_test)
    logger.info(f"[{context}] Prediction done. Data shape: {data.shape}")

    return data

def predict_with_lstm(data, lookback=30, future_days=5, epochs=10):
    logger.info("[LSTM] --- Predict with LSTM ---")
    df = data[['Close']].copy()
    df['Target'] = df['Close'].shift(-future_days)
    df.dropna(inplace=True)
    logger.debug(f"[LSTM] Shape after shift/dropna: {df.shape}")

    context = "LSTM"
    if df.empty or len(df) <= lookback:
        logger.warning(f"[{context}] Not enough data for LSTM – skipping prediction.")
        logger.info(f"[{context}] Data after failed check:\n{df.head(5)}")
        return data

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df)
    logger.debug(f"[{context}] Scaled data shape: {scaled_data.shape}")

    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i - lookback:i, 0])
        y.append(scaled_data[i, 1])

    logger.debug(f"[{context}] Number of LSTM samples: {len(X)}")
    if len(X) == 0:
        logger.warning(f"[{context}] No valid LSTM sequences – skipping prediction.")
        return data

    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))
    logger.debug(f"[{context}] Final X shape for LSTM: {X.shape}")

    model = tf.keras.models.Sequential([
        tf.keras.Input(shape=(X.shape[1], 1)),
        tf.keras.layers.LSTM(50, return_sequences=False),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=epochs, verbose=0)
    logger.info(f"[{context}] Model trained.")

    # Letzte Sequenz als Vorhersagebasis
    last_seq = scaled_data[-lookback:, 0].reshape(1, lookback, 1)
    prediction = model.predict(last_seq)[0][0]
    prediction = scaler.inverse_transform([[0, prediction]])[0][1]

    data.at[data.index[-1], f'LSTM_Pred_{future_days}d'] = prediction
    logger.info(f"[{context}] Prediction inserted. Data shape: {data.shape}")
    return data
