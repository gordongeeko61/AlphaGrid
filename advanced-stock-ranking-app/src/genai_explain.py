# genai_explain.py

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_summary(df, top_n=5):
    """
    Generate a natural language explanation for the top ranked stocks.
    
    Args:
        df (pd.DataFrame): DataFrame containing at least 'risk_adj_score' and 'symbol' columns.
        top_n (int): Number of top stocks to include in the explanation.
    
    Returns:
        str: Explanation text from the LLM.
    """
    try:
        # Get top symbols by risk-adjusted score
        symbols = df.sort_values('risk_adj_score', ascending=False).head(top_n)['symbol'].tolist()
        if not symbols:
            return "No symbols available to generate summary."

        # Build prompt
        prompt = (
            f"Explain why these stocks are top ranked based on multi-period momentum, "
            f"volatility adjustment, and trend filters: {symbols}. "
            f"Mention strong returns, low volatility, and SMA uptrend."
        )

        # Call OpenAI Chat Completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Failed to generate explanation: {e}"
