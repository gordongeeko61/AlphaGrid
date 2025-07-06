import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# Assuming these modules exist and are functional
from data import fetch_data, load_universe
from metrics import compute_metrics_for_all
from filters import apply_filters
from genai_explain import generate_summary
from config import DEFAULT_WEIGHTS, PORTFOLIO_SIZE, UNIVERSE_FILE

# Page config
st.set_page_config(
    page_title="🚀AlphaGrid",
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="expanded"
)

# Initialize session state for the explanation if not already present
if 'genai_explanation' not in st.session_state:
    st.session_state.genai_explanation = ""
if 'summary_generated' not in st.session_state:
    st.session_state.summary_generated = False


def main():
    st.title("🚀 AlphaGrid Dashboard")
    st.markdown("""
    *A data-driven momentum strategy on the **Nifty 500**:*
    - Combines **12-month momentum**, price filters, and **risk-adjusted scoring**
    - Visualizes top stocks, momentum heatmaps & price trends vs 200-EMA
    """)
    top_n_stocks=30 # Default number of top stocks to display
    try:
        nifty_500_symbols = load_universe(UNIVERSE_FILE)
        df = fetch_data(nifty_500_symbols)
        df_metrics = compute_metrics_for_all(df)

        # Apply filters, now passing weights to apply_filters if needed for score calculation
        # Assuming apply_filters uses the weights to calculate risk_adj_score
        df_final = apply_filters(df_metrics) # Pass weights here

        if not df_final.empty:
            top_stocks = df_final.sort_values('risk_adj_score', ascending=False).head(top_n_stocks)

            # Create tabs for better organization
            tab1, tab2, tab3 = st.tabs(["📊 Top Stock Visualizations", "📝 AI Insights", "Detailed Data"])

            with tab1:
                st.subheader(f"🏆 Top {top_n_stocks} Momentum Stocks Overview")
                st.write("Here's a summary of the highest, lowest, and average risk-adjusted scores among the top stocks.")
                col1, col2, col3 = st.columns(3)
                col1.metric("Highest Score", f"{top_stocks['risk_adj_score'].max():.2f}")
                col2.metric("Lowest Score (Top List)", f"{top_stocks['risk_adj_score'].min():.2f}")
                col3.metric("Avg Score (Top List)", f"{top_stocks['risk_adj_score'].mean():.2f}")

                st.markdown("---")
                st.subheader("🥇 Top Stocks by Risk-Adjusted Momentum Score")
                st.write(f"This chart displays the top {top_n_stocks} stocks ranked by their calculated risk-adjusted momentum score.")
                if not top_stocks.empty:
                    fig, ax = plt.subplots(figsize=(12, max(6, len(top_stocks) * 0.4))) # Dynamic height, slightly larger width
                    sns.barplot(x='risk_adj_score', y='symbol', data=top_stocks, palette='viridis', ax=ax)
                    plt.title(f"Top {top_n_stocks} Stocks by Risk-Adjusted Momentum Score")
                    plt.xlabel("Risk-Adjusted Score")
                    plt.ylabel("Stock Symbol")
                    st.pyplot(fig)
                else:
                    st.info("No top stocks to visualize for Risk-Adjusted Score.")

                st.markdown("---")
                st.subheader("🔥 12-Month Momentum Heatmap")
                st.write(f"This heatmap shows the 12-month momentum percentage for the top {top_n_stocks} stocks. Higher values indicate stronger momentum.")
                if not top_stocks.empty and 'mom_12m' in top_stocks.columns:
                    fig, ax = plt.subplots(figsize=(8, max(6, len(top_stocks) * 0.5))) # Adjust size
                    mom_12m_heatmap_data = top_stocks[['mom_12m']].set_index(top_stocks['symbol'])

                    sns.heatmap(
                        mom_12m_heatmap_data,
                        cmap="RdYlGn",
                        linewidths=0.5,
                        linecolor='gray',
                        annot=True,
                        fmt=".1f",
                        cbar_kws={'label': '12-Month Momentum (%)'}
                    )
                    plt.title(f"12-Month Momentum for Top {top_n_stocks} Stocks")
                    plt.xlabel("")
                    plt.ylabel("Stock Symbol")
                    plt.yticks(rotation=0)
                    st.pyplot(fig)
                else:
                    st.info("No top stocks data or 'mom_12m' column missing for 12-Month Momentum Heatmap.")

                st.markdown("---")
                st.subheader("⚖️ Price vs 200-Day Exponential Moving Average (EMA)")
                st.write(f"This scatter plot compares the current price of the top {top_n_stocks} stocks against their 200-day EMA. Stocks above the red dashed line are trading above their 200-day EMA, often seen as a bullish sign.")
                if not top_stocks.empty and 'ema_200' in top_stocks.columns and 'price' in top_stocks.columns:
                    fig, ax = plt.subplots(figsize=(10, 8)) # Slightly larger for better clarity
                    plt.scatter(top_stocks['ema_200'], top_stocks['price'], s=200, alpha=0.8, edgecolors='w', linewidth=0.7) # Larger points

                    max_val = max(top_stocks[['price', 'ema_200']].max().max(), 1.0) * 1.1
                    min_val = min(top_stocks[['price', 'ema_200']].min().min(), 0.0) * 0.9
                    plt.plot([min_val, max_val], [min_val, max_val], 'r--', label='Price = 200-EMA')

                    # Label the points with stock symbols, with a simple adjustment to prevent direct overlap
                    for i, row in top_stocks.iterrows():
                        plt.text(row['ema_200'] * 1.01, row['price'] * 1.01, row['symbol'], fontsize=10, ha='left', va='bottom', color='darkblue')

                    plt.title(f"Price vs 200-EMA for Top {top_n_stocks} Stocks")
                    plt.xlabel("200-Day Exponential Moving Average (EMA)")
                    plt.ylabel("Current Price")
                    plt.grid(True, linestyle='--', alpha=0.6)
                    plt.legend()
                    plt.xlim(min_val, max_val)
                    plt.ylim(min_val, max_val)
                    st.pyplot(fig)
                else:
                    st.info("No top stocks data to plot Price vs 200-EMA, or required columns are missing.")

            with tab2:
                st.subheader("🤖 AI-Powered Insights")
                st.write("Click the button below to get an AI-generated explanation and summary of the top-performing stocks based on the current parameters.")
                if st.button("Generate AI Summary", help="Click to get an AI-generated explanation of the top stocks."):
                    with st.spinner("Generating summary... This might take a moment."):
                        try:
                            # Ensure generate_summary can handle the top_stocks DataFrame
                            st.session_state.genai_explanation = generate_summary(top_stocks, top_n=top_n_stocks)
                            st.session_state.summary_generated = True
                        except Exception as e:
                            st.error(f"❌ Failed to generate AI summary: {e}")
                            st.session_state.genai_explanation = ""
                            st.session_state.summary_generated = False

                if st.session_state.summary_generated and st.session_state.genai_explanation:
                    st.info(f"💡 **AI Summary:** {st.session_state.genai_explanation}")
                elif st.session_state.summary_generated and not st.session_state.genai_explanation:
                    st.warning("No AI summary could be generated with the current data or parameters.")
                else:
                    st.info("Click 'Generate AI Summary' to get an AI-powered explanation of the top stocks.")

            with tab3:
                st.subheader("Detailed Top Stocks Data Table")
                st.write(f"This table provides a comprehensive view of the data for the top {top_n_stocks} stocks, including price, momentum, volatility, and risk-adjusted score.")
                if not top_stocks.empty:
                    detailed_columns = [
                        'symbol', 'price', 'ema_200', 'mom_3m', 'mom_6m', 'mom_12m',
                        'volatility', 'risk_adj_score' # 'date' if available, but not in the provided image data
                    ]
                    existing_detailed_columns = [col for col in detailed_columns if col in top_stocks.columns]
                    st.dataframe(top_stocks[existing_detailed_columns].style.format({
                        'price': "{:.2f}",
                        'ema_200': "{:.2f}",
                        'mom_3m': "{:.2f}",
                        'mom_6m': "{:.2f}",
                        'mom_12m': "{:.2f}",
                        'volatility': "{:.4f}",
                        'risk_adj_score': "{:.2f}"
                    }))
                else:
                    st.info("No detailed stock data available.")

        else:
            st.warning("⚠️ No stocks found matching the criteria. Please adjust filters (e.g., minimum price, outlier percentage) in the sidebar.")

    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}. Please check the data sources or configuration.")
        st.exception(e) # Display the full traceback for debugging

if __name__ == "__main__":
    main()