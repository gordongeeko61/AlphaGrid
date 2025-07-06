import pandas as pd
import numpy as np

def compute_metrics_for_all(data, weights=(0.33, 0.33, 0.33)):
    metrics = []
    w3m, w6m, w12m = weights

    for symbol, df in data.items():
        try:
            mom_3m = float(df["Close"].pct_change(63).iloc[-1]) * 100
            mom_6m = float(df["Close"].pct_change(126).iloc[-1]) * 100
            mom_12m = float(df["Close"].pct_change(252).iloc[-1]) * 100
            volatility = float(df["Close"].std())

            risk_adj_score = float((mom_3m * w3m + mom_6m * w6m + mom_12m * w12m) / (volatility + 1e-6))

            metrics.append({
                "symbol": symbol,
                "mom_3m": mom_3m,
                "mom_6m": mom_6m,
                "mom_12m": mom_12m,
                "volatility": volatility,
                "risk_adj_score": risk_adj_score
            })
            print(f"[metrics] Computed for {symbol}")
        except Exception as e:
            print(f"[metrics] Skipping {symbol}: {e}")

    print(f"[metrics] Computed metrics for {len(metrics)} symbols")
    return pd.DataFrame(metrics)
