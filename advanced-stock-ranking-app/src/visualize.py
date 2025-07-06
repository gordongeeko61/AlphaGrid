# visualize.py

import matplotlib.pyplot as plt
import seaborn as sns

def plot_top_stocks(df, top_n=10):
    df_top = df.sort_values('risk_adj_score', ascending=False).head(top_n)
    plt.figure(figsize=(10,6))
    sns.barplot(x='risk_adj_score', y='Symbol', data=df_top, palette='viridis')
    plt.title(f"Top {top_n} Stocks by Risk-Adjusted Momentum")
    plt.xlabel("Risk-Adjusted Momentum Score")
    plt.ylabel("Symbol")
    plt.tight_layout()
    plt.show()
