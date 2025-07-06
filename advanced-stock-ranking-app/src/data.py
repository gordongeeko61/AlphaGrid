import yfinance as yf
import pandas as pd
def fetch_data():
    # Example symbols: replace with your real list
    symbols = [
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "AMD", "INTC",
        "NFLX", "ADBE", "PYPL", "CSCO", "CMCSA", "PEP", "COST", "TXN", "QCOM",
        "AVGO", "INTU", "AMAT", "MU", "ADI", "LRCX", "KLAC", "MCHP"
    ]

    end_date = "2025-07-04"
    start_date = "2023-07-04"

    data = {}
    for symbol in symbols:
        try:
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)
            print(f"[fetch_data] {symbol}: fetched {len(df)} rows")
            data[symbol] = df
        except Exception as e:
            print(f"[fetch_data] Error fetching {symbol}: {e}")
    return data
