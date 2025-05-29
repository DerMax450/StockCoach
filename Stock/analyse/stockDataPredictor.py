from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf

from services.setupLogger import setup_logger

logger = setup_logger(__name__, f"logs/stockAnalyzer.log")

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf

def validate_ml_data(
    data, 
    required_features=None, 
    min_rows=50, 
    label_column=None, 
    context="ML-Validation", 
    logger=None
):
    """
    Prüft, ob der ML-Datensatz verwendbar ist.
    
    Parameter:
        data: Pandas DataFrame mit allen Spalten.
        required_features: Liste der Features, die vorhanden sein müssen.
        min_rows: Mindestanzahl an Zeilen.
        label_column: Spalte für das Target/Label (z.B. 'TrendUp').
        context: Optionaler Log-Context.
        logger: Optionaler Logger, sonst print().
        
    Rückgabe:
        True/False (verwendbar oder nicht)
    """

    def log(msg):
        if logger:
            logger.info(msg)
        else:
            print(msg)
    
    # Check 1: Genug Daten vorhanden?
    if data is None or len(data) < min_rows:
        log(f"[{context}] Zu wenig Daten: nur {len(data) if data is not None else 0} Zeilen.")
        return False

    # Check 2: Alle Features vorhanden?
    if required_features is not None:
        missing = [f for f in required_features if f not in data.columns]
        if missing:
            log(f"[{context}] Fehlende Features: {missing}")
            return False

    # Check 3: NaN-Prüfung für Features
    if required_features is not None:
        nan_feats = [f for f in required_features if data[f].isnull().any()]
        if nan_feats:
            log(f"[{context}] Achtung: Nullwerte in Features: {nan_feats}")
            return False

    # Check 4: Label-Prüfung
    if label_column:
        if label_column not in data.columns:
            log(f"[{context}] Labelspalte '{label_column}' fehlt!")
            return False
        if data[label_column].isnull().any():
            log(f"[{context}] Nullwerte im Label '{label_column}'!")
            return False
        if data[label_column].nunique() < 2:
            log(f"[{context}] Label '{label_column}' hat nur eine Klasse (Werte: {data[label_column].unique()})")
            return False
        bincounts = data[label_column].value_counts()
        log(f"[{context}] Labelverteilung: {bincounts.to_dict()}")

    # Check 5: Features ausreichende Varianz?
    if required_features is not None:
        zero_var = [f for f in required_features if data[f].nunique() <= 1]
        if zero_var:
            log(f"[{context}] Feature(s) mit keiner oder zu geringer Varianz: {zero_var}")
            return False

    # Optional: Warnung bei extremem Klassenungleichgewicht
    if label_column:
        bincounts = data[label_column].value_counts(normalize=True)
        if bincounts.min() < 0.05:
            log(f"[{context}] Warnung: Klassen sehr ungleich verteilt! {bincounts.to_dict()}")

    log(f"[{context}] ML-Validation erfolgreich.")
    return True


# --- Hilfsfunktion für Feature-Auswahl ---
def get_features(df):
    forbidden = ['FutureClose', 'TrendUp', 'Trend', 'Crossover']  # passe an
    numerical = df.select_dtypes(include=[np.number]).columns
    features = [col for col in numerical if col not in forbidden and not col.startswith("('Close") and not col.endswith("_num")]
    return features

# --- RandomForest optimiert ---
def predict_with_random_forest(data, future_days=5):
    data = data.copy()
    data['FutureClose'] = data['Close'].shift(-future_days)
    data.dropna(subset=['FutureClose'], inplace=True)
    features = get_features(data)

    if not validate_ml_data(data, required_features=features, min_rows=50, label_column='FutureClose', context="RandomForest"):
        return data

    X = data[features]
    y = data['FutureClose']
    # Skalierung (optional, nicht zwingend für RF)
    #scaler = MinMaxScaler()
    #X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    if len(X_train) < 50:
        return data

    model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    data.loc[X_test.index, 'RF_Prediction'] = model.predict(X_test)
    return data

# --- LSTM optimiert (mit mehreren Features) ---
def predict_with_lstm(data, lookback=60, future_days=5, epochs=30):
    features = ['Close', 'Volume', 'SMA_50', 'Median_50']  # beliebig erweiterbar, alle numerischen Features sinnvoll!
    df = data[features].copy()
    df['Target'] = df['Close'].shift(-future_days)
    df.dropna(inplace=True)

    if df.empty or len(df) <= lookback:
        return data

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df)
    X, y = [], []
    for i in range(lookback, len(scaled)):
        X.append(scaled[i-lookback:i, :-1])
        y.append(scaled[i, -1])

    X, y = np.array(X), np.array(y)
    # shape: [samples, lookback, features]
    X = X.reshape((X.shape[0], X.shape[1], X.shape[2]))

    # Modell
    model = tf.keras.models.Sequential([
        tf.keras.Input(shape=(X.shape[1], X.shape[2])),
        tf.keras.layers.LSTM(64, return_sequences=False),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=epochs, batch_size=32, verbose=0)

    # Prediction auf Testbereich
    for offset in range(len(df) - lookback, len(df)):
        seq = scaled[offset-lookback:offset, :-1].reshape(1, lookback, X.shape[2])
        pred = model.predict(seq, verbose=0)[0][0]
        pred_unscaled = scaler.inverse_transform(np.concatenate([scaled[offset-lookback+1:offset+1, :-1], [[pred]]], axis=1))[-1, -1]
        data.at[df.index[offset], f'LSTM_Pred_{future_days}d'] = pred_unscaled

    return data

def classify_trend_with_gradient_boosting(data, future_days=1):
    logger.info("[TrendBoost] --- Classify trend with GradientBoosting ---")
    data = data.copy()
    data['FutureClose'] = data['Close'].shift(-future_days)
    data['TrendUp'] = (data['FutureClose'] > data['Close']).astype(int)
    data.dropna(inplace=True)
    
    # Feature Engineering
    features = [
        'Close', 'Volume', 'SMA_50', 'SMA_200', 'HL_range',
        'Chaikin_Volatility_100', 'Median_50', 'DC_Upper_20', 'DC_Lower_20', 
        'DC_Mid_20'
    ]
    features = [f for f in features if f in data.columns and data[f].dtype != 'object']
    context = "TrendBoost"
    
    if not validate_ml_data(data, required_features=features, min_rows=50, label_column='TrendUp', context=context):
        return data

    X = data[features]
    y = data['TrendUp']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)
    logger.info(f"[{context}] Klassenverteilung Training: {np.bincount(y_train)}")
    if len(X_train) < 30 or len(np.unique(y_train)) < 2:
        logger.warning(f"[{context}] Zu wenig Trainingsdaten oder nur eine Klasse.")
        return data

    model = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        random_state=42
    )
    model.fit(X_train, y_train)
    logger.info(f"[{context}] Model trained. Predicting...")
    data.loc[X_test.index, 'TrendPrediction'] = model.predict(X_test)

    # Optional: Feature Importance
    importances = model.feature_importances_
    for name, imp in zip(features, importances):
        logger.info(f"[{context}] Feature Importance: {name} = {imp:.4f}")

    # Log Ergebnis
    score = model.score(X_test, y_test)
    logger.info(f"[{context}] Test-Accuracy: {score:.4f}")

    return data
