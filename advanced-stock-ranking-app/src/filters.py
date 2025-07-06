import pandas as pd
# filters.py
# filters.py
def apply_filters(df_metrics, data, outlier_pct=5):
    # Filter out outliers by risk_adj_score quantiles
    q_low = df_metrics['risk_adj_score'].quantile(outlier_pct / 100)
    q_high = df_metrics['risk_adj_score'].quantile(1 - outlier_pct / 100)
    filtered = df_metrics[
        (df_metrics['risk_adj_score'] >= q_low) &
        (df_metrics['risk_adj_score'] <= q_high)
    ]
    print(f"[filters] Filtered to {filtered.shape[0]} rows")
    return filtered
