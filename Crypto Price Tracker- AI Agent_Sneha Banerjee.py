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
def get_crypto_data(ids="", per_page=50):
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
        # Fetch 50 posts for better representation
        posts = [p.title for p in reddit.subreddit("CryptoCurrency").search(coin, limit=50)]
        if not posts:
            return "neutral"
        joined = " ".join(posts)[:1024]
        results = sentiment(joined)
        # Majority vote
        positive_count = sum(1 for r in results if r['label'] == 'POSITIVE')
        negative_count = sum(1 for r in results if r['label'] == 'NEGATIVE')
        if positive_count > negative_count:
            return "bullish"
        elif negative_count > positive_count:
            return "bearish"
        else:
            return "neutral"
    except Exception:
        return "neutral"

# ---------------------- Summary for 4 coins ----------------------
def get_summary_coins():
    ids = "bitcoin,ethereum,solana,zcash"
    return get_crypto_data(ids=ids, per_page=4)

def generate_summary():
    coins = get_summary_coins()
    if not coins:
        return ["Error fetching crypto data. Please try again later."]
    
    summary_lines = []
    for c in coins:
        name = c.get("name","Unknown")
        price_change = c.get("price_change_percentage_24h",0)
        trend = "↑" if price_change > 0 else "↓"
        sentiment_label = get_reddit_sentiment(name)
        # Separate metrics for clarity
        summary_lines.append(
            f"{name}: Market Trend {trend}{abs(price_change):.2f}% | Community Sentiment: {sentiment_label}"
        )
    return summary_lines

# ---------------------- Top Movers (price-driven only) ----------------------
def get_top_movers(per_page=250, top_n=5):
    coins = get_crypto_data(ids="", per_page=per_page)
    if not coins or not isinstance(coins, list):
        return [], "", []

    # Filter coins without 24h change
    coins = [c for c in coins if c.get("price_change_percentage_24h") is not None]
    if not coins:
        return [], "", []

    bullish = sorted(coins, key=lambda x: x["price_change_percentage_24h"], reverse=True)[:top_n]
    bearish = sorted(coins, key=lambda x: x["price_change_percentage_24h"])[:top_n]

    bullish_list = [f"{c.get('name','Unknown')} ↑{c['price_change_percentage_24h']:.2f}%" for c in bullish]
    bearish_list = [f"{c.get('name','Unknown')} ↓{c['price_change_percentage_24h']:.2f}%" for c in bearish]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return bullish_list, timestamp, bearish_list

# ---------------------- Streamlit UI ----------------------
st.title("💬 Crypto Chat Agent")

# Daily summary (4 coins)
st.subheader("📊 Daily Coin Summary (Bitcoin, Ethereum, Solana, Zcash)")
if st.button("Get Summary"):
    with st.spinner("Fetching 4 coin summary..."):
        summary_lines = generate_summary()
    st.text_area("Summary", value="\n".join(summary_lines), height=200)

# Top 5 movers (all coins)
st.subheader("📈 Top 5 Bullish & Bearish Coins (All Coins)")
if st.button("Get Top Movers"):
    with st.spinner("Fetching top movers..."):
        bullish_list, timestamp, bearish_list = get_top_movers()
    st.caption(f"Data fetched at: {timestamp}")
    st.subheader("Top 5 Bullish Coins")
    st.text_area("", value="\n".join(bullish_list), height=150)
    st.subheader("Top 5 Bearish Coins")
    st.text_area("", value="\n".join(bearish_list), height=150)

st.info("Cl
