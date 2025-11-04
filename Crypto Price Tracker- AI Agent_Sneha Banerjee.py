import streamlit as st
import requests
import praw
from transformers import pipeline

# ---------------------- Reddit Setup ----------------------
reddit = praw.Reddit(
    client_id="5zvsIGv4FawpVD7oqZqcHw",
    client_secret="TFeXWHyFBlMWPspjxD-72puVnIS5Wg",
    user_agent="SBCryptoAgent"
)

# ---------------------- Sentiment Model ----------------------
sentiment = pipeline("sentiment-analysis")

# ---------------------- Functions ----------------------
def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": "bitcoin,ethereum,solana,zcash"}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if not isinstance(data, list):
            return []
        return data
    except Exception:
        return []

def get_reddit_sentiment(coin):
    try:
        posts = [p.title for p in reddit.subreddit("CryptoCurrency").search(coin, limit=10)]
        if not posts:
            return "neutral"
        joined = " ".join(posts)[:512]
        label = sentiment(joined)[0]["label"]
        return "bullish" if label == "POSITIVE" else "bearish"
    except Exception:
        return "neutral"

def generate_summary():
    coins = get_crypto_data()
    if not coins:
        return "Error fetching crypto data. Please try again later."

    summary_lines = []
    for c in coins:
        coin_name = c.get("name", "Unknown")
        price_change = c.get("price_change_percentage_24h", 0)

        trend = "↑" if price_change > 0 else "↓"
        sentiment_label = get_reddit_sentiment(coin_name)
        summary_lines.append(
            f"{coin_name} {trend}{abs(price_change):.2f}% — community sentiment: {sentiment_label}"
        )
    return "\n".join(summary_lines)

# ---------------------- Streamlit UI ----------------------
st.title("💬 Crypto Chat Agent")

if st.button("Get Today's Crypto Summary"):
    with st.spinner("Fetching live market & sentiment data..."):
        output = generate_summary()
    st.text_area("AI Agent Summary", value=output, height=200)

st.info("Click the button anytime — agent fetches fresh data automatically.")
