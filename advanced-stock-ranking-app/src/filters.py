# filters.py

import pandas as pd
from config import DEFAULT_OUTLIER_PCT, MIN_PRICE, MIN_VOLUME

def apply_filters(df_metrics, data, outlier_pct=DEFAULT_OUTLIER_PCT):
    """
    Apply filters to the metrics DataFrame
    
    Args:
        df_metrics (pd.DataFrame): DataFrame with metrics
        data (dict): Raw data dictionary
        outlier_pct (float): Percentage to filter as outliers
    
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    # Filter stocks above 200-EMA
    # FIX: Ensure 'above_ema' is explicitly boolean and handle potential NaNs
    boolean_mask = df_metrics['above_ema'].astype(bool).fillna(False)
    filtered = df_metrics[boolean_mask].copy()
    print(f"[filters] After EMA filter: {filtered.shape[0]} stocks")
    
    # Filter out low price stocks
    filtered = filtered[filtered['price'] >= MIN_PRICE]
    print(f"[filters] After price filter: {filtered.shape[0]} stocks")
    
    return filtered