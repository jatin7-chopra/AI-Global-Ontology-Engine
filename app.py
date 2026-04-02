import streamlit as st
import spacy
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import folium
from streamlit_folium import st_folium
from collections import Counter

# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(
    page_title="AI Global Ontology Engine",
    layout="wide"
)

# --------------------------
# API KEY
# --------------------------
api_key = "1d9cf629376473fa3c24b699ff4fd0d9"

# --------------------------
# LOAD NLP (SAFE)
# --------------------------
@st.cache_resource
def load_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except:
        return None

nlp = load_nlp()

# --------------------------
# SESSION STATE
# --------------------------
if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

# --------------------------
# SIDEBAR
# --------------------------
st.sidebar.title("⚙️ Control Panel")

country_options = {
    "All": "",
    "India": "in",
    "United States": "us"
}

language_options = {
    "English": "en",
    "Hindi": "hi"
}

selected_country = st.sidebar.selectbox("Country", list(country_options.keys()))
selected_language = st.sidebar.selectbox("Language", list(language_options.keys()))

query = st.sidebar.text_input("Search", "World")
max_results = st.sidebar.slider("Articles", 5, 20, 10)

if st.sidebar.button("Run Analysis"):
    st.session_state.run_analysis = True

# --------------------------
# FETCH GNEWS (FIXED)
# --------------------------
@st.cache_data(ttl=600)
def fetch_gnews(api_key, query, max_results, country, language, refresh_counter):
    url = "https://gnews.io/api/v4/search"

    params = {
        "q": query,
        "lang": language_options[language],
        "max": max_results,
        "apikey": api_key
    }

    if country_options[country]:
        params["country"] = country_options[country]

    res = requests.get(url, params=params)
    data = res.json()

    articles = data.get("articles", [])
    return articles

# --------------------------
# PROCESS DATA
# --------------------------
def process_articles(articles):
    rows = []
    for a in articles:
        rows.append({
            "Title": a.get("title"),
            "Source": a.get("source", {}).get("name"),
            "URL": a.get("url")
        })
    return pd.DataFrame(rows)

# --------------------------
# MAIN
# --------------------------
st.title("🌍 AI Global Ontology Engine")

if st.session_state.run_analysis:
    try:
        articles = fetch_gnews(
            api_key,
            query,
            max_results,
            selected_country,
            selected_language,
            st.session_state.refresh_counter
        )

        if not articles:
            st.warning("No news found")
        else:
            df = process_articles(articles)

            for _, row in df.iterrows():
                st.markdown(f"### {row['Title']}")
                st.write(row["Source"])
                st.write(row["URL"])
                st.markdown("---")

    except Exception as e:
        st.error(f"Error: {e}")
