# streamlit_app.py

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np # Import numpy for np.inf
from data import fetch_data, load_universe
from metrics import compute_metrics_for_all
from filters import apply_filters
from genai_explain import generate_summary
from config import DEFAULT_WEIGHTS, PORTFOLIO_SIZE, UNIVERSE_FILE

# Page config
st.set_page_config(
    page_title="Momentum Stock Ranking",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("嶋 Momentum Stock Ranking Dashboard")
    st.markdown("""
    A systematic approach to identify high momentum stocks from Nifty 500 universe,
    filtered by 200-EMA and ranked by risk-adjusted momentum scores.
    """)
    
    # Sidebar controls
    st.sidebar.header("Parameters")
    w3m = st.sidebar.slider("3-month weight", 0.0, 1.0, DEFAULT_WEIGHTS[0], 0.05)
    w6m = st.sidebar.slider("6-month weight", 0.0, 1.0, DEFAULT_WEIGHTS[1], 0.05)
    w12m = st.sidebar.slider("12-month weight", 0.0, 1.0, DEFAULT_WEIGHTS[2], 0.05)
    outlier_pct = st.sidebar.slider("Outlier filter (%)", 0.0, 10.0, 3.0, 0.5)
    top_n = st.sidebar.slider("Portfolio size", 10, 100, PORTFOLIO_SIZE, 5)
    
    weights = (w3m, w6m, w12m)
    
    if st.sidebar.button("Run Analysis"):
        with st.spinner("Running analysis..."):
            # Load data
            tickers = load_universe(UNIVERSE_FILE)
            data = fetch_data(tickers)
            
            # Compute metrics
            df_metrics = compute_metrics_for_all(data, weights=weights)
            df_filtered = apply_filters(df_metrics, data, outlier_pct=outlier_pct)
            
            # Drop rows with NaN or infinite risk_adj_score
            # Replace inf with NaN first, then drop NaNs
            df_filtered = df_filtered.replace([np.inf, -np.inf], np.nan).dropna(subset=['risk_adj_score'])
            
            # Ensure df_filtered is not empty after dropping NaNs
            if df_filtered.empty:
                st.warning("No stocks with valid risk-adjusted scores after filters. Adjust parameters or check data availability.")
                # Clear session state if no results
                if 'df_final' in st.session_state:
                    del st.session_state.df_final
                if 'weights' in st.session_state:
                    del st.session_state.weights
                return

            # Add rank column before selecting top_n
            df_filtered = df_filtered.sort_values('risk_adj_score', ascending=False).reset_index(drop=True)
            df_filtered['rank'] = df_filtered['risk_adj_score'].rank(ascending=False, method='min').astype(int)
            
            # Now select the top_n stocks
            df_final = df_filtered.head(top_n)
            
            # Store in session state
            st.session_state.df_final = df_final
            st.session_state.weights = weights
    
    if 'df_final' not in st.session_state:
        st.warning("Configure parameters and click 'Run Analysis'")
        return
    
    df_final = st.session_state.df_final
    weights = st.session_state.weights
    
    # Summary stats
    st.subheader("投 Portfolio Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Stocks in Portfolio", len(df_final))
    col2.metric("Avg 3m Momentum", f"{df_final['mom_3m'].mean():.1f}%")
    col3.metric("Avg 12m Momentum", f"{df_final['mom_12m'].mean():.1f}%")
    
    # GenAI Explanation
    st.subheader("ｧ AI Portfolio Analysis")
    with st.expander("See explanation"):
        summary = generate_summary(df_final)
        st.info(summary)
    
    # Main results
    st.subheader("醇 Top Momentum Stocks")
    st.dataframe(
        df_final[['symbol', 'risk_adj_score', 'rank', 'mom_3m', 'mom_6m', 'mom_12m', 'volatility']]
        .sort_values('risk_adj_score', ascending=False) # Ensure sorting for display consistency
        .style.background_gradient(subset=['risk_adj_score'], cmap='YlGnBu')
        .format({'mom_3m': '{:.1f}%', 'mom_6m': '{:.1f}%', 'mom_12m': '{:.1f}%'}),
        height=600
    )
    
    # Visualizations
    st.subheader("嶋 Portfolio Visualizations")
    
    tab1, tab2, tab3 = st.tabs(["Momentum Scores", "Heatmap", "Price vs EMA"])
    
    with tab1:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='risk_adj_score', y='symbol', data=df_final.sort_values('risk_adj_score', ascending=True), palette='viridis')
        plt.title(f"Top {top_n} Stocks by Risk-Adjusted Momentum")
        plt.xlabel("Score")
        plt.ylabel("Symbol")
        st.pyplot(fig)
    
    with tab2:
        heatmap_cols = ['mom_3m', 'mom_6m', 'mom_12m', 'volatility', 'risk_adj_score']
        heatmap_data = df_final[heatmap_cols].copy()
        heatmap_data.index = df_final['symbol']
        
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(
            heatmap_data,
            cmap="YlGnBu",
            linewidths=0.3,
            annot=True,
            fmt=".1f",
            cbar=True
        )
        plt.title("Momentum Metrics Heatmap")
        st.pyplot(fig)
    
    with tab3:
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.scatter(df_final['ema_200'], df_final['price'], s=100, alpha=0.6)
        
        # Add 1:1 line
        max_val = max(df_final[['price', 'ema_200']].max().max(), 1.0) # Ensure max_val is at least 1.0 to avoid potential issues
        plt.plot([0, max_val], [0, max_val], 'r--')
        
        # Add labels
        for i, row in df_final.iterrows():
            plt.text(row['ema_200']*1.01, row['price']*1.01, row['symbol'], fontsize=9)
        
        plt.title("Price vs 200-EMA")
        plt.xlabel("200-EMA")
        plt.ylabel("Current Price")
        plt.grid(True)
        st.pyplot(fig)
    
    # Download button
    st.download_button(
        label="Download Portfolio",
        data=df_final.to_csv(index=False),
        file_name=f"momentum_portfolio_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )

if __name__ == "__main__":
    main()