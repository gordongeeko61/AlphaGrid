# app.py

import argparse
from datetime import datetime
from data import fetch_data , load_universe
from metrics import compute_metrics_for_all
from filters import apply_filters
from visualize import plot_top_stocks, plot_momentum_heatmap, plot_price_vs_ema
from genai_explain import generate_summary
from config import DEFAULT_WEIGHTS, DEFAULT_OUTLIER_PCT, PORTFOLIO_SIZE,UNIVERSE_FILE
import pandas as pd # Import pandas for DataFrame operations

def run_app(weights, outlier_pct, top_n):
    print(f"\n{'='*50}")
    print(f"Running Momentum Ranking System - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Universe: Nifty 500 | Portfolio Size: {top_n}")
    print(f"Momentum Weights: 3m={weights[0]}, 6m={weights[1]}, 12m={weights[2]}")
    print(f"{'='*50}\n")
    
    print("Fetching tickers...\n")
    tickers = load_universe(UNIVERSE_FILE)
    print(f"Found {len(tickers)} tickers in Nifty 500")

    print("\nDownloading data with 200-EMA calculation...\n")
    data = fetch_data(tickers)
    print(f"Successfully downloaded data for {len(data)} stocks")

    print("\nComputing metrics...\n")
    df_metrics = compute_metrics_for_all(data, weights=weights)
    # Print only key columns
    print(df_metrics[['symbol', 'risk_adj_score', 'mom_3m', 'mom_6m', 'mom_12m']].to_string(index=False))

    print("\nApplying filters...\n")
    df_filtered = apply_filters(df_metrics, data, outlier_pct=outlier_pct)
    
    # Handle case where no stocks pass filters
    if df_filtered.empty:
        print("No stocks passed the filters. Exiting.")
        return

    print("\nRanking stocks...\n")
    # Sort by risk_adj_score and add rank
    df_final = df_filtered.sort_values(by='risk_adj_score', ascending=False).reset_index(drop=True)
    df_final['rank'] = df_final['risk_adj_score'].rank(ascending=False, method='min').astype(int)
    
    # Select top N stocks for final display and processing
    df_final = df_final.head(top_n)

    print(f"\nTop {top_n} stocks:\n")
    print(df_final[['symbol', 'risk_adj_score', 'rank', 'mom_3m', 'mom_6m', 'mom_12m']].to_string(index=False))

    print("\nGenerating summary...\n")
    summary = generate_summary(df_final)
    print("\n📝 GenAI Summary:\n", summary)

    print("\nPlotting visualizations...\n")
    plot_top_stocks(df_final, top_n=top_n)
    plot_momentum_heatmap(df_final, top_n=top_n)
    plot_price_vs_ema(df_final)

    # Save results
    df_final.to_csv("momentum_portfolio.csv", index=False)
    print("\n✅ Results saved to momentum_portfolio.csv")

def main():
    parser = argparse.ArgumentParser(description='Momentum Stock Ranking System')
    parser.add_argument('--w3m', type=float, default=DEFAULT_WEIGHTS[0],
                       help='Weight for 3-month momentum')
    parser.add_argument('--w6m', type=float, default=DEFAULT_WEIGHTS[1],
                       help='Weight for 6-month momentum')
    parser.add_argument('--w12m', type=float, default=DEFAULT_WEIGHTS[2],
                       help='Weight for 12-month momentum')
    parser.add_argument('--outlier', type=float, default=DEFAULT_OUTLIER_PCT,
                       help='Percentage to filter as outliers')
    parser.add_argument('--top', type=int, default=PORTFOLIO_SIZE,
                       help='Number of top stocks to display')
    args = parser.parse_args()

    weights = (args.w3m, args.w6m, args.w12m)
    run_app(weights, args.outlier, args.top)

if __name__ == "__main__":
    main()