# visualize.py

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.ticker import PercentFormatter

def plot_top_stocks(df, top_n=10):
    """Plot top stocks by risk-adjusted momentum"""
    df_top = df.sort_values('risk_adj_score', ascending=False).head(top_n)
    
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(x='risk_adj_score', y='symbol', data=df_top, palette='viridis')
    
    # Add value labels
    for p in ax.patches:
        width = p.get_width()
        ax.text(width + 0.1, p.get_y() + p.get_height()/2., 
                f'{width:.1f}', ha='left', va='center')
    
    plt.title(f"Top {top_n} Stocks by Risk-Adjusted Momentum", fontsize=14)
    plt.xlabel("Risk-Adjusted Momentum Score")
    plt.ylabel("Symbol")
    plt.tight_layout()
    plt.show()

def plot_momentum_heatmap(df, top_n=30):
    """Plot heatmap of momentum metrics for top stocks"""
    df_top = df.sort_values('risk_adj_score', ascending=False).head(top_n)
    
    # Select and normalize columns
    heatmap_cols = ['mom_3m', 'mom_6m', 'mom_12m', 'volatility', 'risk_adj_score']
    heatmap_data = df_top[heatmap_cols].copy()
    heatmap_data.index = df_top['symbol']
    
    # Create figure
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        heatmap_data,
        cmap="YlGnBu",
        linewidths=0.3,
        annot=True,
        fmt=".1f",
        cbar=True,
        annot_kws={"size": 8}
    )
    plt.title(f"Top {top_n} Stocks Momentum Metrics", fontsize=14)
    plt.tight_layout()
    plt.show()

def plot_price_vs_ema(df):
    """Plot price vs 200-EMA for top stocks"""
    df_top = df.sort_values('risk_adj_score', ascending=False).head(10)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(df_top['ema_200'], df_top['price'], s=100, alpha=0.6)
    
    # Add 1:1 line
    max_val = max(df_top[['price', 'ema_200']].max())
    plt.plot([0, max_val], [0, max_val], 'r--')
    
    # Add labels
    for i, row in df_top.iterrows():
        plt.text(row['ema_200']*1.01, row['price']*1.01, row['symbol'], fontsize=9)
    
    plt.title("Price vs 200-EMA for Top Stocks")
    plt.xlabel("200-EMA")
    plt.ylabel("Current Price")
    plt.grid(True)
    plt.tight_layout()
    plt.show()