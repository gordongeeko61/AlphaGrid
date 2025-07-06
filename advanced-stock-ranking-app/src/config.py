# config.py

# Universe configuration
UNIVERSE_FILE = "data/ind_nifty500list.csv"

# Momentum parameters
LOOKBACK_PERIODS = {
    '3m': 63,    # 3 months (~63 trading days)
    '6m': 126,   # 6 months (~126 trading days)
    '12m': 252   # 12 months (~252 trading days)
}

# Portfolio configuration
PORTFOLIO_SIZE = 30          # Number of stocks in portfolio
EXIT_RANK_THRESHOLD = 60     # Exit if rank falls below this
MIN_DAYS_FOR_EMA = 200       # Minimum days required for EMA calculation

# Default weights for momentum periods
DEFAULT_WEIGHTS = (0.4, 0.3, 0.3)  # weights for 3m, 6m, 12m returns

# Filter parameters
DEFAULT_OUTLIER_PCT = 3      # remove top 3% as outliers
MIN_PRICE = 10               # Minimum price filter (Rs)
MIN_VOLUME = 100000          # Minimum average volume filter