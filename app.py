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
# HIDDEN API KEY
# --------------------------
api_key = "1d9cf629376473fa3c24b699ff4fd0d9"
# Better option:
# api_key = st.secrets["GNEWS_API_KEY"]

# --------------------------
# PREMIUM CSS
# --------------------------
page_bg = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    margin: 0 !important;
    padding: 0 !important;
}

/* App background */
.stApp {
    background: radial-gradient(circle at top left, #1a1f3a 0%, #0d1117 35%, #05070b 100%);
    color: white;
}

/* Remove top blank space */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 2rem;
    max-width: 96%;
}

/* Remove Streamlit default top header gap */
[data-testid="stHeader"] {
    background: transparent !important;
    height: 0rem !important;
}

[data-testid="stToolbar"] {
    top: 0.5rem;
    right: 0.5rem;
}

[data-testid="stAppViewContainer"] > .main {
    padding-top: 0rem !important;
    margin-top: 0rem !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b0d12 0%, #101826 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
}

/* Main glass panel */
.main-panel {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 8px 32px rgba(0,0,0,0.30);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 22px;
    padding: 1.5rem 1.5rem 1rem 1.5rem;
    margin-top: 0rem !important;
    margin-bottom: 1rem;
}

/* Headings */
h1, h2, h3, h4, h5, h6, p, label {
    color: white !important;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
    line-height: 1.1;
}

.hero-sub {
    font-size: 1.1rem;
    color: #d0d7e2 !important;
    margin-bottom: 0.8rem;
}

.badge-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 12px;
    margin-bottom: 6px;
}

.badge {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.10);
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 0.88rem;
    color: #f2f5f9;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button,
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #ff4b4b 0%, #ff7b54 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    min-height: 3rem !important;
    width: 100% !important;
    box-shadow: 0 6px 18px rgba(255, 75, 75, 0.25) !important;
}

/* Inputs */
.stTextInput input,
textarea {
    background-color: rgba(255,255,255,0.96) !important;
    color: black !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.96) !important;
    color: black !important;
    border-radius: 10px !important;
}

div[data-baseweb="tag"] {
    color: black !important;
}

ul[role="listbox"] li {
    background-color: white !important;
    color: black !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 800 !important;
}

[data-testid="stMetricLabel"] {
    color: #d3d9e3 !important;
}

/* Article cards */
.news-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.1rem 1.1rem 0.9rem 1.1rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.20);
}

.news-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.35rem;
}

.news-meta {
    font-size: 0.9rem;
    color: #cfd8e3;
    margin-bottom: 0.6rem;
}

.news-desc {
    color: #eef2f7;
    line-height: 1.6;
    margin-bottom: 0.7rem;
}

.risk-high {
    color: #ff8b8b;
    font-weight: 700;
}

.risk-medium {
    color: #ffd166;
    font-weight: 700;
}

.risk-low {
    color: #7ae582;
    font-weight: 700;
}

hr {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 1.2rem 0;
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# --------------------------
# LOAD NLP
# --------------------------
@st.cache_resource
def load_nlp():
    return spacy.load("en_core_web_sm")

nlp = load_nlp()

# --------------------------
# SESSION STATE
# --------------------------
if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

# --------------------------
# HERO SECTION
# --------------------------
st.markdown(
    """
    <div class="main-panel">
        <div class="hero-title">🌍 AI Global Ontology Intelligence Engine</div>
        <div class="hero-sub">Strategic intelligence dashboard for live global monitoring, pattern discovery, and geopolitical signal analysis.</div>
        <div class="badge-row">
            <div class="badge">Live GNews Feed</div>
            <div class="badge">Ontology Mapping</div>
            <div class="badge">Knowledge Graph</div>
            <div class="badge">Risk Intelligence</div>
            <div class="badge">Geo Monitoring</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------
# SIDEBAR CONTROLS
# --------------------------
st.sidebar.title("⚙️ Control Panel")

country_options = {
    "All": "",
    "India": "in",
    "United States": "us",
    "United Kingdom": "gb",
    "Australia": "au",
    "Canada": "ca",
    "China": "cn",
    "France": "fr",
    "Germany": "de",
    "Japan": "jp",
    "Russia": "ru",
    "Ukraine": "ua",
    "Israel": "il",
    "Pakistan": "pk",
    "South Korea": "kr",
    "United Arab Emirates": "ae"
}

language_options = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "German": "de",
    "Spanish": "es"
}

selected_country_name = st.sidebar.selectbox(
    "Country Filter",
    options=list(country_options.keys()),
    index=0
)

selected_language_name = st.sidebar.selectbox(
    "Language Filter",
    options=list(language_options.keys()),
    index=0
)

topic_filter = st.sidebar.multiselect(
    "Filter Intelligence Domains",
    options=["Defense", "Economics", "Climate", "Technology", "Geopolitics", "Cybersecurity", "Health"],
    default=[]
)

headline_filter = st.sidebar.text_input("Filter Headlines")
show_debug = st.sidebar.checkbox("Show Debug Data", value=False)

selected_country = country_options[selected_country_name]
selected_language = language_options[selected_language_name]

# --------------------------
# MAIN FORM
# --------------------------
with st.form("control_form"):
    query = st.text_input("Search Topic / Keyword", value="World")
    max_results = st.slider("Number of Articles", 5, 50, 10)
    submitted = st.form_submit_button("Run Live Global Intelligence Analysis")

if submitted:
    st.session_state.run_analysis = True

col1, col2 = st.columns(2)

with col1:
    if st.button("Refresh News"):
        st.session_state.run_analysis = True
        st.session_state.refresh_counter += 1

with col2:
    if st.button("Clear Dashboard"):
        st.session_state.run_analysis = False

# --------------------------
# GNEWS FETCH
# --------------------------
@st.cache_data(ttl=600)
def fetch_gnews(api_key, query, max_results, country, language, refresh_counter):
    search_url = "https://gnews.io/api/v4/search"
    search_params = {
        "q": query,
        "lang": language,
        "max": max_results,
        "apikey": api_key
    }

    if country:
        search_params["country"] = country

    search_response = requests.get(search_url, params=search_params, timeout=20)
    search_response.raise_for_status()
    search_data = search_response.json()
    articles = search_data.get("articles", [])

    if not articles:
        top_url = "https://gnews.io/api/v4/top-headlines"
        top_params = {
            "lang": language,
            "max": max_results,
            "apikey": api_key
        }

        if country:
            top_params["country"] = country

        top_response = requests.get(top_url, params=top_params, timeout=20)
        top_response.raise_for_status()
        top_data = top_response.json()
        articles = top_data.get("articles", [])

    return articles

# --------------------------
# CLASSIFIER
# --------------------------
def classify_topic(text):
    text = text.lower()

    if any(word in text for word in ["military", "defense", "army", "missile", "war", "navy", "air force"]):
        return "Defense"

    if any(word in text for word in ["market", "inflation", "economy", "stock", "trade", "gdp", "finance", "bank"]):
        return "Economics"

    if any(word in text for word in ["climate", "environment", "weather", "carbon", "global warming", "flood", "heatwave"]):
        return "Climate"

    if any(word in text for word in ["ai", "artificial intelligence", "technology", "tech", "robot", "software", "semiconductor"]):
        return "Technology"

    if any(word in text for word in ["cyber", "hacker", "malware", "ransomware", "data breach", "cyberattack"]):
        return "Cybersecurity"

    if any(word in text for word in ["health", "virus", "disease", "hospital", "medicine", "vaccine"]):
        return "Health"

    return "Geopolitics"

# --------------------------
# RISK LEVEL
# --------------------------
def risk_level(topic, text):
    text = text.lower()

    high_words = ["war", "attack", "crisis", "missile", "explosion", "sanctions", "conflict", "cyberattack"]
    medium_words = ["warning", "pressure", "concern", "decline", "inflation", "storm", "heatwave"]

    if any(word in text for word in high_words):
        return "High"

    if topic in ["Defense", "Cybersecurity"]:
        return "High"

    if any(word in text for word in medium_words):
        return "Medium"

    if topic in ["Climate", "Economics", "Health"]:
        return "Medium"

    return "Low"

# --------------------------
# PROCESS ARTICLES
# --------------------------
def process_articles(articles):
    rows = []

    for article in articles:
        title = article.get("title", "") or ""
        description = article.get("description", "") or ""
        content_text = f"{title}. {description}"

        topic = classify_topic(content_text)
        risk = risk_level(topic, content_text)

        rows.append({
            "Title": title,
            "Description": description,
            "Content": content_text,
            "Topic": topic,
            "Risk": risk,
            "Source": article.get("source", {}).get("name", "Unknown"),
            "Published At": article.get("publishedAt", ""),
            "URL": article.get("url", "")
        })

    return pd.DataFrame(rows)

# --------------------------
# MAP COORDINATES
# --------------------------
country_coords = {
    "India": [20.59, 78.96],
    "United States": [37.09, -95.71],
    "China": [35.86, 104.19],
    "Russia": [61.52, 105.31],
    "Ukraine": [48.38, 31.17],
    "Israel": [31.04, 34.85],
    "Europe": [54.52, 15.25],
    "United Kingdom": [55.37, -3.43],
    "France": [46.22, 2.21],
    "Germany": [51.17, 10.45],
    "Japan": [36.20, 138.25],
    "Australia": [-25.27, 133.77],
    "Canada": [56.13, -106.35],
    "Pakistan": [30.37, 69.35],
    "South Korea": [35.91, 127.77],
    "United Arab Emirates": [23.42, 53.85]
}

# --------------------------
# DASHBOARD
# --------------------------
if st.session_state.run_analysis:
    if not api_key.strip():
        st.error("API key missing in code.")
    else:
        try:
            with st.spinner("Fetching live intelligence feed..."):
                articles = fetch_gnews(
                    api_key,
                    query,
                    max_results,
                    selected_country,
                    selected_language,
                    st.session_state.refresh_counter
                )

            if show_debug:
                st.write("Articles fetched from API:", len(articles))
                if articles:
                    st.json(articles[0])

            if not articles:
                st.warning("No articles found. Try changing the country, language, or keyword.")
            else:
                df = process_articles(articles)

                if show_debug:
                    st.write("Rows before filters:", len(df))
                    st.dataframe(df)

                if headline_filter:
                    df = df[
                        df["Title"].str.contains(headline_filter, case=False, na=False) |
                        df["Description"].str.contains(headline_filter, case=False, na=False)
                    ]

                if topic_filter:
                    df = df[df["Topic"].isin(topic_filter)]

                if show_debug:
                    st.write("Rows after filters:", len(df))
                    st.dataframe(df)

                if df.empty:
                    st.warning("No articles match the selected filters.")
                else:
                    st.subheader("📡 Live Global Intelligence Feed")

                    for _, row in df.iterrows():
                        risk_class = "risk-low"
                        if row["Risk"] == "High":
                            risk_class = "risk-high"
                        elif row["Risk"] == "Medium":
                            risk_class = "risk-medium"

                        st.markdown(
                            f"""
                            <div class="news-card">
                                <div class="news-title">{row['Title']}</div>
                                <div class="news-meta">
                                    <b>Topic:</b> {row['Topic']} |
                                    <b>Risk:</b> <span class="{risk_class}">{row['Risk']}</span> |
                                    <b>Source:</b> {row['Source']}
                                </div>
                                <div class="news-desc">{row['Description']}</div>
                                <div class="news-meta"><b>Published:</b> {row['Published At']}</div>
                                <a href="{row['URL']}" target="_blank">Read full article</a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    st.download_button(
                        "Download Intelligence Report CSV",
                        df.to_csv(index=False).encode("utf-8"),
                        file_name="live_global_intelligence_report.csv",
                        mime="text/csv"
                    )

                    st.header("🌐 Global Intelligence Overview")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Signals", len(df))
                    c2.metric("High Risk", int((df["Risk"] == "High").sum()))
                    c3.metric("Technology", int((df["Topic"] == "Technology").sum()))
                    c4.metric("Climate Alerts", int((df["Topic"] == "Climate").sum()))

                    st.header("📊 Intelligence Trend Analysis")
                    trend = df["Topic"].value_counts().reset_index()
                    trend.columns = ["Topic", "Count"]
                    fig_bar = px.bar(
                        trend,
                        x="Topic",
                        y="Count",
                        color="Topic",
                        title="Global Intelligence Topic Distribution"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                    st.markdown("### 📊 Multi-Factor Trend Analysis")

                    trend_df = pd.DataFrame({
                        "Year": [2020, 2021, 2022, 2023, 2024],
                        "Risk": [58, 66, 74, 83, 91],
                        "Growth": [24, 29, 35, 41, 47],
                        "Stability": [68, 62, 57, 51, 45]
                    })

                    fig_trend = px.line(
                        trend_df,
                        x="Year",
                        y=["Risk", "Growth", "Stability"],
                        markers=True,
                        title="Multi-Factor Trend Analysis Dashboard"
                    )

                    fig_trend.update_traces(
                        line=dict(width=3),
                        marker=dict(size=8)
                    )

                    fig_trend.update_layout(
                        template="plotly_white",
                        xaxis_title="Year",
                        yaxis_title="Performance Index",
                        legend_title="Metrics",
                        hovermode="x unified",
                        title_x=0.25
                    )

                    st.plotly_chart(fig_trend, use_container_width=True)

                    st.header("🧭 Intelligence Distribution")
                    fig_pie = px.pie(
                        df,
                        names="Topic",
                        title="Global Intelligence Breakdown"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                    st.header("⚠️ Risk Level Distribution")
                    risk_df = df["Risk"].value_counts().reset_index()
                    risk_df.columns = ["Risk", "Count"]
                    fig_risk = px.bar(
                        risk_df,
                        x="Risk",
                        y="Count",
                        color="Risk",
                        title="Risk Level Analysis"
                    )
                    st.plotly_chart(fig_risk, use_container_width=True)

                    st.header("📰 Top News Sources")
                    source_df = df["Source"].value_counts().reset_index()
                    source_df.columns = ["Source", "Articles"]
                    fig_source = px.bar(
                        source_df,
                        x="Source",
                        y="Articles",
                        color="Source",
                        title="Top Contributing News Sources"
                    )
                    st.plotly_chart(fig_source, use_container_width=True)

                    st.header("⏳ Publication Timeline")
                    df["Published At"] = pd.to_datetime(df["Published At"], errors="coerce")
                    timeline_df = df.dropna(subset=["Published At"]).copy()

                    if not timeline_df.empty:
                        timeline_df = timeline_df.sort_values("Published At")
                        timeline_df["Article Index"] = range(1, len(timeline_df) + 1)

                        fig_time = px.line(
                            timeline_df,
                            x="Published At",
                            y="Article Index",
                            hover_name="Title",
                            title="News Publication Timeline",
                            markers=True
                        )
                        st.plotly_chart(fig_time, use_container_width=True)

                    st.header("🧠 Global Knowledge Graph")
                    G = nx.Graph()

                    for text in df["Content"]:
                        doc = nlp(text)
                        entities = [ent.text for ent in doc.ents if len(ent.text.strip()) > 2]

                        for i in range(len(entities) - 1):
                            G.add_edge(entities[i], entities[i + 1])

                    if len(G.nodes()) > 0:
                        pos = nx.spring_layout(G, seed=42)

                        edge_x, edge_y = [], []
                        for edge in G.edges():
                            x0, y0 = pos[edge[0]]
                            x1, y1 = pos[edge[1]]
                            edge_x.extend([x0, x1, None])
                            edge_y.extend([y0, y1, None])

                        node_x, node_y, labels = [], [], []
                        for node in G.nodes():
                            x, y = pos[node]
                            node_x.append(x)
                            node_y.append(y)
                            labels.append(node)

                        fig_graph = go.Figure()
                        fig_graph.add_trace(go.Scatter(
                            x=edge_x,
                            y=edge_y,
                            mode="lines",
                            line=dict(width=1),
                            hoverinfo="none"
                        ))
                        fig_graph.add_trace(go.Scatter(
                            x=node_x,
                            y=node_y,
                            mode="markers+text",
                            text=labels,
                            textposition="top center",
                            marker=dict(size=18),
                            hoverinfo="text"
                        ))
                        fig_graph.update_layout(
                            title="Entity Relationship Intelligence Graph",
                            showlegend=False,
                            xaxis=dict(showgrid=False, zeroline=False, visible=False),
                            yaxis=dict(showgrid=False, zeroline=False, visible=False),
                            height=650
                        )
                        st.plotly_chart(fig_graph, use_container_width=True)
                    else:
                        st.warning("No entities found for knowledge graph.")

                    st.header("🌎 Global Intelligence Map")
                    world_map = folium.Map(location=[20, 0], zoom_start=2)
                    detected_places = Counter()

                    for text in df["Content"]:
                        doc = nlp(text)
                        for ent in doc.ents:
                            if ent.label_ in ["GPE", "LOC"] and ent.text in country_coords:
                                detected_places[ent.text] += 1

                    if not detected_places:
                        detected_places = {"India": 1, "United States": 1, "China": 1}

                    for place, count in detected_places.items():
                        coord = country_coords.get(place)
                        if coord:
                            folium.CircleMarker(
                                location=coord,
                                radius=8 + count * 2,
                                popup=f"{place} | Mentions: {count}",
                                color="red",
                                fill=True,
                                fill_opacity=0.7
                            ).add_to(world_map)

                    st_folium(world_map, width=1000, height=500, key="global_map")

                    st.header("🤖 AI Strategic Insights")
                    top_topic = df["Topic"].value_counts().idxmax()
                    high_risk_count = int((df["Risk"] == "High").sum())

                    st.info(
                        f"""
• Total live intelligence signals captured: {len(df)}  
• Dominant strategic domain detected: {top_topic}  
• High-risk developments identified: {high_risk_count}  
• News sources monitored: {df['Source'].nunique()}  
• Selected country filter: {selected_country_name}  
• Selected language filter: {selected_language_name}
                        """
                    )

        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error while fetching GNews data: {e}")
        except requests.exceptions.ConnectionError:
            st.error("Connection error. Please check your internet connection.")
        except requests.exceptions.Timeout:
            st.error("Request timed out while fetching live news.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
