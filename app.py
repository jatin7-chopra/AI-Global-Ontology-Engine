import streamlit as st
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
api_key = "YOUR_API_KEY_HERE"

# --------------------------
# SESSION STATE
# --------------------------
if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

# --------------------------
# SIDEBAR
# --------------------------
st.sidebar.title("⚙️ Control Panel")

query = st.sidebar.text_input("Search Topic", "World")
max_results = st.sidebar.slider("Articles", 5, 50, 10)

if st.sidebar.button("Run Analysis"):
    st.session_state.run_analysis = True

# --------------------------
# FETCH NEWS
# --------------------------
def fetch_news():
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "en",
        "max": max_results,
        "apikey": api_key
    }

    res = requests.get(url, params=params)
    data = res.json()
    return data.get("articles", [])

# --------------------------
# CLASSIFIER
# --------------------------
def classify(text):
    text = text.lower()

    if "war" in text or "army" in text:
        return "Defense"
    elif "market" in text or "stock" in text:
        return "Economics"
    elif "climate" in text:
        return "Climate"
    elif "ai" in text or "tech" in text:
        return "Technology"
    else:
        return "General"

# --------------------------
# MAIN
# --------------------------
st.title("🌍 AI Global Ontology Intelligence Engine")

if st.session_state.run_analysis:

    articles = fetch_news()

    if not articles:
        st.warning("No news found")
    else:
        rows = []

        for a in articles:
            title = a.get("title", "")
            desc = a.get("description", "")
            text = title + " " + desc

            topic = classify(text)

            rows.append({
                "Title": title,
                "Description": desc,
                "Topic": topic,
                "URL": a.get("url", "")
            })

        df = pd.DataFrame(rows)

        st.subheader("📰 News Feed")

        for _, row in df.iterrows():
            st.markdown(f"""
            **{row['Title']}**  
            {row['Description']}  
            Topic: {row['Topic']}  
            [Read More]({row['URL']})
            """)

        # --------------------------
        # CHART
        # --------------------------
        st.subheader("📊 Topic Distribution")

        fig = px.bar(df["Topic"].value_counts())
        st.plotly_chart(fig)

        # --------------------------
        # GRAPH (NO SPACY)
        # --------------------------
        st.subheader("🧠 Knowledge Graph")

        G = nx.Graph()

        for text in df["Title"]:
            words = text.split()
            words = [w for w in words if len(w) > 4]

            for i in range(len(words)-1):
                G.add_edge(words[i], words[i+1])

        if len(G.nodes()) > 0:
            pos = nx.spring_layout(G)

            edge_x = []
            edge_y = []

            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x += [x0, x1, None]
                edge_y += [y0, y1, None]

            node_x = []
            node_y = []

            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines'
            ))

            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=list(G.nodes())
            ))

            st.plotly_chart(fig)
