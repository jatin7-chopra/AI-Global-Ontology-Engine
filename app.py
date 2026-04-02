import streamlit as st
import pandas as pd
import requests

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(page_title="AI Global Ontology Engine", layout="wide")

# --------------------------
# API KEY
# --------------------------
api_key = "1d9cf629376473fa3c24b699ff4fd0d9"

# --------------------------
# SESSION
# --------------------------
if "run" not in st.session_state:
    st.session_state.run = False

# --------------------------
# SIDEBAR
# --------------------------
st.sidebar.title("Control Panel")

query = st.sidebar.text_input("Search Topic", "World")
max_results = st.sidebar.slider("Articles", 5, 20, 10)

if st.sidebar.button("Run"):
    st.session_state.run = True

# --------------------------
# FETCH NEWS
# --------------------------
@st.cache_data(ttl=600)
def fetch_news():
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "en",
        "max": max_results,
        "apikey": api_key
    }

    res = requests.get(url)
    data = res.json()
    return data.get("articles", [])

# --------------------------
# MAIN UI
# --------------------------
st.title("🌍 AI Global Ontology Engine")

if st.session_state.run:
    try:
        articles = fetch_news()

        if not articles:
            st.warning("No news found")
        else:
            for a in articles:
                st.subheader(a.get("title"))
                st.write(a.get("source", {}).get("name"))
                st.write(a.get("url"))
                st.markdown("---")

    except Exception as e:
        st.error(e)
