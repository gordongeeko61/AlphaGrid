# metrics.py

import pandas as pd
import numpy as np
from config import LOOKBACK_PERIODS

def compute_metrics_for_all(data, weights=(0.33, 0.33, 0.33)):
    """
    Compute momentum metrics for all stocks with 200-EMA filter
    
    Args:
        data (dict): Dictionary of DataFrames keyed by symbol
        weights (tuple): Weights for 3m, 6m, 12m momentum
    
    Returns:
        pd.DataFrame: DataFrame with computed metrics
    """
    metrics = []
    w3m, w6m, w12m = weights

    for symbol, df in data.items():
        try:
            # Check if price is above 200-EMA
            # Ensure these are scalar floats to prevent 'above_ema' from becoming a Series
            current_price = float(df['Close'].iloc[-1])
            ema_200 = float(df['EMA_200'].iloc[-1])
            above_ema = current_price > ema_200
            
            # Calculate momentum metrics
            mom_3m = float(df["Close"].pct_change(LOOKBACK_PERIODS['3m']).iloc[-1]) * 100
            mom_6m = float(df["Close"].pct_change(LOOKBACK_PERIODS['6m']).iloc[-1]) * 100
            mom_12m = float(df["Close"].pct_change(LOOKBACK_PERIODS['12m']).iloc[-1]) * 100
            
            # Calculate volatility (standard deviation of daily returns)
            daily_returns = df["Close"].pct_change()
            volatility = float(daily_returns.std() * np.sqrt(252))  # Annualized
            
            # Risk-adjusted score
            risk_adj_score = float((mom_3m * w3m + mom_6m * w6m + mom_12m * w12m) / (volatility + 1e-6))

            metrics.append({
                "symbol": symbol,
                "price": current_price,
                "ema_200": ema_200,
                "above_ema": above_ema,
                "mom_3m": mom_3m,
                "mom_6m": mom_6m,
                "mom_12m": mom_12m,
                "volatility": volatility,
                "risk_adj_score": risk_adj_score
            })
            print(f"[metrics] Computed for {symbol}")
        except Exception as e:
            print(f"[metrics] Error computing metrics for {symbol}: {e}")
            continue # Skip to the next symbol if there's an error
    
    df_metrics = pd.DataFrame(metrics)
    return df_metrics