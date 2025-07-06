# data.py

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta
from config import LOOKBACK_PERIODS, MIN_DAYS_FOR_EMA,UNIVERSE_FILE

def fetch_data(tickers, end_date=None, start_date=None):
    """
    Fetch historical data for multiple tickers with 200-EMA calculation
    
    Args:
        tickers (list): List of ticker symbols
        end_date (str): End date in YYYY-MM-DD format (default: today)
        start_date (str): Start date in YYYY-MM-DD format 
                         (default: 12 months before end_date + 200 days buffer)
    
    Returns:
        dict: Dictionary of DataFrames keyed by symbol
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    if start_date is None:
        # Start date = 12 months + 200 days buffer for EMA calculation
        start_date = (datetime.now() - timedelta(days=LOOKBACK_PERIODS['12m'] + MIN_DAYS_FOR_EMA)).strftime('%Y-%m-%d')
    
    data = {}
    for symbol in tickers:
        try:
            df = yf.download(
                symbol + ".NS",  # Adding .NS for NSE stocks
                start=start_date,
                end=end_date,
                progress=False
            )
            
            # Calculate 200-EMA
            if len(df) >= MIN_DAYS_FOR_EMA:
                df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
                data[symbol] = df
                print(f"[fetch_data] {symbol}: fetched {len(df)} rows with EMA")
            else:
                print(f"[fetch_data] {symbol}: insufficient data for EMA ({len(df)} rows)")
                
        except Exception as e:
            print(f"[fetch_data] Error fetching {symbol}: {e}")
    
    return data

def load_universe(file_path):
    """Load the Nifty 500 universe from CSV"""
    # Get the absolute path of the directory containing the current script
# For app.py, this will be ALPHAGRID-1/advanced-stock-ranking-app/src/
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to the universe file
# Since UNIVERSE_FILE is just the filename and it's in the same directory as config.py
# and assuming app.py is also in the same directory (src)
    universe_file_full_path = os.path.join(current_script_dir, UNIVERSE_FILE)
    df = pd.read_csv(universe_file_full_path)
    return df['Symbol'].tolist()