

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
