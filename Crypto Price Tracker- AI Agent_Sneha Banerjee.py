#!/usr/bin/env python
# coding: utf-8

# In[1]:



# In[2]:


import requests

url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "ids": "bitcoin,ethereum,solana,zcash"
}

response = requests.get(url, params=params)
data = response.json()

print("---- DAILY CRYPTO SUMMARY ----")
for coin in data:
    name = coin["name"]
    price = coin["current_price"]
    change = coin["price_change_percentage_24h"]
    trend = "↑" if change > 0 else "↓"
    print(f"{name}: ${price:,.2f} ({trend}{abs(change):.2f}% in 24h)")


# In[3]:





# In[4]:


import praw

reddit = praw.Reddit(
    client_id="5zvsIGv4FawpVD7oqZqcHw",
    client_secret="TFeXWHyFBlMWPspjxD-72puVnIS5Wg",
    user_agent="SBCryptoAgent"
)

subreddit = reddit.subreddit("CryptoCurrency")
for post in subreddit.hot(limit=1):
    print(post.title)


# In[5]:


import streamlit as st
import requests
import praw

# ---------------------- Reddit Setup ----------------------
reddit = praw.Reddit(
    client_id="5zvsIGv4FawpVD7oqZqcHw",
    client_secret="TFeXWHyFBlMWPspjxD-72puVnIS5Wg",
    user_agent="SBCryptoAgent"
)

# ---------------------- Functions ----------------------
def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": "bitcoin,ethereum,solana,zcash"}
    return requests.get(url, params=params).json()

# Safe Reddit sentiment placeholder (avoids heavy ML)
def get_reddit_sentiment(coin):
    posts = [p.title for p in reddit.subreddit("CryptoCurrency").search(coin, limit=10)]
    if not posts:
        return "neutral"
    # Basic heuristic: if "bull" appears in any title → bullish, else neutral
    joined = " ".join(posts).lower()
    if "bull" in joined:
        return "bullish"
    elif "bear" in joined:
        return "bearish"
    else:
        return "neutral"

def generate_summary():
    coins = get_crypto_data()
    summary_lines = []
    for c in coins:
        trend = "↑" if c["price_change_percentage_24h"] > 0 else "↓"
        sentiment_label = get_reddit_sentiment(c["name"])
        summary_lines.append(
            f"{c['name']} {trend}{abs(c['price_change_percentage_24h']):.2f}% — community sentiment: {sentiment_label}"
        )
    return "\n".join(summary_lines)

# ---------------------- Streamlit UI ----------------------
st.title("💬 Crypto Chat Agent (Safe Version)")

if st.button("Get Today's Crypto Summary"):
    st.write("Fetching live market & Reddit data...")
    output = generate_summary()
    st.text_area("AI Agent Summary", value=output, height=200)

st.info("Click the button anytime — agent fetches fresh data automatically.")


# In[1]:


import streamlit as st
import requests
import praw

# ---------------------- Reddit Setup ----------------------
reddit = praw.Reddit(
    client_id="5zvsIGv4FawpVD7oqZqcHw",
    client_secret="TFeXWHyFBlMWPspjxD-72puVnIS5Wg",
    user_agent="SBCryptoAgent"
)

# ---------------------- Functions ----------------------
def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "ids": "bitcoin,ethereum,solana,zcash"}
    return requests.get(url, params=params).json()

# Safe Reddit sentiment heuristic
def get_reddit_sentiment(coin):
    posts = [p.title for p in reddit.subreddit("CryptoCurrency").search(coin, limit=10)]
    if not posts:
        return "neutral"
    joined = " ".join(posts).lower()
    if "bull" in joined:
        return "bullish"
    elif "bear" in joined:
        return "bearish"
    else:
        return "neutral"

def generate_summary():
    coins = get_crypto_data()
    summary_lines = []
    for c in coins:
        trend = "↑" if c["price_change_percentage_24h"] > 0 else "↓"
        sentiment_label = get_reddit_sentiment(c["name"])
        summary_lines.append(
            f"{c['name']} {trend}{abs(c['price_change_percentage_24h']):.2f}% — community sentiment: {sentiment_label}"
        )
    return "\n".join(summary_lines)

# ---------------------- Streamlit UI ----------------------
st.title("💬 Crypto Chat Agent (Safe Version)")

if st.button("Get Today's Crypto Summary"):
    st.write("Fetching live market & Reddit data...")
    output = generate_summary()
    st.text_area("AI Agent Summary", value=output, height=200)

st.info("Click the button anytime — agent fetches fresh data automatically.")


# In[ ]:




