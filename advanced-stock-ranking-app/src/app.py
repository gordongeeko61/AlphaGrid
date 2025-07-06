# app.py

import argparse
from fetch_data import get_nasdaq_tickers, download_data
from metrics import compute_metrics_for_all
from filters import apply_filters
from visualize import plot_top_stocks
from genai_explain import generate_summary
from config import DEFAULT_WEIGHTS, DEFAULT_OUTLIER_PCT, DEFAULT_TOP_N

def run_app(weights, outlier_pct, top_n):
    print("Fetching tickers...")
    tickers = get_nasdaq_tickers()
    print(f"Found {len(tickers)} tickers")

    print("Downloading data...")
    data = download_data(tickers)

    print("Computing metrics...")
    df_metrics = compute_metrics_for_all(data, weights=weights)

    print("Applying filters...")
    df_filtered = apply_filters(df_metrics, data, outlier_pct=outlier_pct)
    df_final = df_filtered.sort_values('risk_adj_score', ascending=False).head(top_n)

    print(f"\nTop {top_n} stocks:\n{df_final[['Symbol','risk_adj_score']]}")

    print("Generating summary...")
    summary = generate_summary(df_final)
    print("\n📝 GenAI Summary:\n", summary)

    print("Plotting chart...")
    plot_top_stocks(df_final, top_n=top_n)

    df_final.to_csv("top_stocks.csv", index=False)
    print("\n✅ Exported to top_stocks.csv")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--w3m', type=float, default=DEFAULT_WEIGHTS[0])
    parser.add_argument('--w6m', type=float, default=DEFAULT_WEIGHTS[1])
    parser.add_argument('--w12m', type=float, default=DEFAULT_WEIGHTS[2])
    parser.add_argument('--outlier', type=float, default=DEFAULT_OUTLIER_PCT)
    parser.add_argument('--top', type=int, default=DEFAULT_TOP_N)
    args = parser.parse_args()
    weights = (args.w3m, args.w6m, args.w12m)
    run_app(weights, args.outlier, args.top)

if __name__ == "__main__":
    main()
