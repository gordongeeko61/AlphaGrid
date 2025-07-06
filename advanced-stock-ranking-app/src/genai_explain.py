# genai_explain.py

import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# The original generate_summary function remains unchanged for overall ranking explanation
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
            f"Explain why these stocks are great picks"
            f"{symbols}. "
            f"mentioned in a professional, Bloomberg-like style. "
            f"what common themes or characteristics are observed in top-performing stocks of this type/sector. and donot mentioned individual stocks description."
        )

        # Call OpenAI Chat Completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ Failed to generate explanation: {e}"