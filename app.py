import streamlit as st
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import folium
from streamlit_folium import st_folium
from collections import Counter

st.set_page_config(page_title="AI Global Ontology Engine", layout="wide")

api_key = "YOUR_API_KEY_HERE"

st.title("🌍 AI Global Ontology Intelligence Engine")

@st.cache_data(ttl=600)
def fetch_gnews(api_key, query, max_results):
url = "https://gnews.io/api/v4/search"
params = {"q": query, "max": max_results, "apikey": api_key}
res = requests.get(url, params=params)
data = res.json()
return data.get("articles", [])

query = st.text_input("Search Topic", "World")
max_results = st.slider("Number of Articles", 5, 20, 10)

if st.button("Run Analysis"):
articles = fetch_gnews(api_key, query, max_results)

```
if not articles:
    st.warning("No data found")
else:
    rows = []
    for a in articles:
        text = (a.get("title","") + " " + a.get("description",""))
        
        # SIMPLE ENTITY EXTRACTION (NO SPACY)
        entities = text.split()[:5]

        rows.append({
            "Title": a.get("title"),
            "Source": a.get("source", {}).get("name"),
            "Entities": ", ".join(entities)
        })

    df = pd.DataFrame(rows)

    st.dataframe(df)

    st.subheader("📊 Chart")
    fig = px.bar(df, x="Source", title="News Sources")
    st.plotly_chart(fig)

    st.subheader("🧠 Knowledge Graph")
    G = nx.Graph()

    for e in df["Entities"]:
        words = e.split(", ")
        for i in range(len(words)-1):
            G.add_edge(words[i], words[i+1])

    if len(G.nodes()) > 0:
        pos = nx.spring_layout(G)
        edge_x, edge_y = [], []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        node_x, node_y = [], []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

        fig_graph = go.Figure()
        fig_graph.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines'))
        fig_graph.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers+text', text=list(G.nodes())))
        st.plotly_chart(fig_graph)

    st.subheader("🌍 Map")
    m = folium.Map(location=[20,0], zoom_start=2)
    folium.Marker([28.61,77.23], popup="India").add_to(m)
    st_folium(m, width=700, height=400)
```
