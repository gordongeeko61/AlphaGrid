import streamlit as st
from data import fetch_data
from metrics import compute_metrics_for_all
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from genai_explain import generate_summary


def main():
    st.title("TrendFinder")

    # Fetch historical stock data
    data = fetch_data()

    # Compute risk-adjusted and weighted momentum scores
    w3m, w6m, w12m = 0.3, 0.3, 0.4
    df_metrics = compute_metrics_for_all(data, weights=(w3m, w6m, w12m))

    # Ensure risk_adj_score is numeric & drop rows with NaN
    df_metrics["risk_adj_score"] = pd.to_numeric(df_metrics["risk_adj_score"], errors="coerce")
    df_metrics = df_metrics.dropna(subset=["risk_adj_score"])

    # Sort by risk-adjusted score
    df_sorted = df_metrics.sort_values("risk_adj_score", ascending=False)

    # Generate GenAI explanation (now at the top)
    st.subheader("🧠 GenAI Explanation")
    summary = generate_summary(df_sorted)
    st.info(summary)

    # Heatmap for wow effect (moved up)
    st.subheader("🔥 Heatmap: Momentum & Risk Metrics")
    sns.set(style="whitegrid")

    # Select columns for heatmap & normalize
    heatmap_cols = ["mom_3m", "mom_6m", "mom_12m", "volatility", "risk_adj_score"]
    heatmap_data = df_sorted[heatmap_cols].copy()
    heatmap_data.index = df_sorted["symbol"]
    normalized_data = (heatmap_data - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min())

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(
        normalized_data,
        cmap="YlGnBu",
        linewidths=0.3,
        annot=True,
        fmt=".2f",
        cbar=True,
        ax=ax
    )
    ax.set_title("📊 Stock Ranking Heatmap (Momentum & Risk Adjusted Score)", fontsize=16, weight='bold')
    st.pyplot(fig)

    # The display results table section is removed to show only the summary and heatmap.

if __name__ == "__main__":
    main()