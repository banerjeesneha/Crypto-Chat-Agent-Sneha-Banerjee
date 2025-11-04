import streamlit as st
import requests
import praw
from transformers import pipeline
from datetime import datetime

# ---------------------- Reddit Setup ----------------------
reddit = praw.Reddit(
    client_id="5zvsIGv4FawpVD7oqZqcHw",
    client_secret="TFeXWHyFBlMWPspjxD-72puVnIS5Wg",
    user_agent="SBCryptoAgent"
)

# ---------------------- Sentiment Model ----------------------
sentiment = pipeline("sentiment-analysis")

# ---------------------- Functions ----------------------
def get_crypto_data(ids="bitcoin,ethereum,solana,zcash", per_page=50):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ids,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1
    }
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

def get_top_coins():
    coins = get_crypto_data(per_page=50)
    if not coins:
        return [], "", []

    # Top 5 bullish coins (highest 24h % change)
    bullish = sorted(coins, key=lambda x: x.get("price_change_percentage_24h", 0), reverse=True)[:5]

    # Top 5 bearish coins (lowest 24h % change)
    bearish = sorted(coins, key=lambda x: x.get("price_change_percentage_24h", 0))[:5]

    bullish_list = [
        f"{c.get('name','Unknown')} ↑{c.get('price_change_percentage_24h',0):.2f}% — sentiment: {get_reddit_sentiment(c.get('name',''))}" 
        for c in bullish
    ]
    bearish_list = [
        f"{c.get('name','Unknown')} ↓{c.get('price_change_percentage_24h',0):.2f}% — sentiment: {get_reddit_sentiment(c.get('name',''))}" 
        for c in bearish
    ]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return bullish_list, timestamp, bearish_list

# ---------------------- Streamlit UI ----------------------
st.title("💬 Crypto Chat Agent")

# Daily summary
st.subheader("📊 Daily Coin Summary")
if st.button("Get Today's Crypto Summary"):
    with st.spinner("Fetching live market & sentiment data..."):
        output = generate_summary()
    st.text_area("AI Agent Summary", value=output, height=200)

# Top 5 bullish/bearish coins
st.subheader("📈 Top 5 Bullish & Bearish Coins")
if st.button("Get Top Coins"):
    with st.spinner("Fetching top coins..."):
        bullish_list, timestamp, bearish_list = get_top_coins()
    st.caption(f"Data fetched at: {timestamp}")
    st.subheader("Top 5 Bullish Coins")
    st.text_area("", value="\n".join(bullish_list), height=150)
    st.subheader("Top 5 Bearish Coins")
    st.text_area("", value="\n".join(bearish_list), height=150)

st.info("Click the buttons anytime — agent fetches fresh data automatically.")
