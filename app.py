import streamlit as st
import spacy
import networkx as nx
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --------------------------
# PAGE CONFIG
# --------------------------

st.set_page_config(
    page_title="AI Global Ontology Engine",
    layout="wide"
)

# --------------------------
# BACKGROUND STYLE (FIXED)
# --------------------------

page_bg = """
<style>

/* FULL APP BACKGROUND */

.stApp {
background-image: url("https://www.shutterstock.com/image-photo/complete-global-world-map-dark-260nw-2684247997.jpg");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
}

/* DASHBOARD PANEL */

.block-container {
background-color: rgba(0,0,0,0.85);
padding: 2rem;
border-radius: 15px;
}

/* TEXT COLOR */

h1, h2, h3, h4, h5, h6, p, span, label {
color: white;
}

/* BUTTON STYLE */

.stButton>button {
background-color: #ff4b4b;
color: white;
border-radius: 10px;
height: 3em;
width: 100%;
font-size: 16px;
}

</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# --------------------------
# LOAD NLP
# --------------------------

nlp = spacy.load("en_core_web_sm")

# --------------------------
# TITLE
# --------------------------

st.title("🌍 AI Global Ontology Intelligence Engine")
st.markdown("Strategic Intelligence Dashboard for Global Monitoring")

# --------------------------
# SIDEBAR CONTROLS
# --------------------------

st.sidebar.title("Control Panel")

topic_filter = st.sidebar.multiselect(
"Select Intelligence Domains",
["Defense","Economics","Climate","Technology","Geopolitics"]
)

search_text = st.sidebar.text_input("Search Intelligence")

# --------------------------
# SESSION STATE
# --------------------------

if "run_analysis" not in st.session_state:
    st.session_state.run_analysis = False

# --------------------------
# SAMPLE DATA
# --------------------------

news_data = [
"India strengthens defense cooperation with United States",
"China launches new AI technology initiative",
"Russia expands military operations in eastern Europe",
"Global stock markets fall due to inflation concerns",
"Climate change causing extreme weather across Europe",
"United Nations warns about environmental crisis",
"Major cyber attack targets global financial systems",
"Artificial intelligence transforming global technology industry"
]

# --------------------------
# CLASSIFIER
# --------------------------

def classify_topic(text):

    text = text.lower()

    if "military" in text or "defense" in text:
        return "Defense"

    if "market" in text or "inflation" in text:
        return "Economics"

    if "climate" in text or "environment" in text:
        return "Climate"

    if "ai" in text or "technology" in text:
        return "Technology"

    return "Geopolitics"

# --------------------------
# RISK LEVEL
# --------------------------

def risk_level(topic):

    if topic == "Defense":
        return "High"

    if topic == "Climate":
        return "Medium"

    if topic == "Economics":
        return "Medium"

    return "Low"

# --------------------------
# BUTTON
# --------------------------

if st.button("🚀 Run Global Intelligence Analysis"):
    st.session_state.run_analysis = True

# --------------------------
# MAIN DASHBOARD
# --------------------------

if st.session_state.run_analysis:

    st.header("📡 Global Intelligence Feed")

    topics=[]
    risks=[]

    for text in news_data:

        topic = classify_topic(text)
        risk = risk_level(topic)

        topics.append(topic)
        risks.append(risk)

    df = pd.DataFrame({
        "News":news_data,
        "Topic":topics,
        "Risk":risks
    })

    # SEARCH FILTER

    if search_text:
        df = df[df["News"].str.contains(search_text, case=False)]

    if topic_filter:
        df = df[df["Topic"].isin(topic_filter)]

    for index,row in df.iterrows():

        st.success(f"{row['Topic']} | Risk: {row['Risk']} → {row['News']}")

    # DOWNLOAD REPORT

    st.download_button(
        "Download Intelligence Report",
        df.to_csv(index=False),
        file_name="global_intelligence_report.csv"
    )

    # METRICS

    st.header("🌐 Global Intelligence Overview")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Signals",len(df))
    col2.metric("High Risk",(df["Risk"]=="High").sum())
    col3.metric("Technology",(df["Topic"]=="Technology").sum())
    col4.metric("Climate Alerts",(df["Topic"]=="Climate").sum())

    # BAR CHART

    st.header("📊 Intelligence Trend Analysis")

    trend = df["Topic"].value_counts().reset_index()
    trend.columns = ["Topic","Count"]

    fig = px.bar(
        trend,
        x="Topic",
        y="Count",
        color="Topic",
        title="Global Intelligence Topic Distribution"
    )

    st.plotly_chart(fig,use_container_width=True)

    # PIE CHART

    st.header("🧭 Intelligence Distribution")

    pie = px.pie(
        df,
        names="Topic",
        title="Global Intelligence Breakdown"
    )

    st.plotly_chart(pie,use_container_width=True)

    # KNOWLEDGE GRAPH

    st.header("🧠 Global Knowledge Graph")

    G = nx.Graph()

    for text in df["News"]:

        doc = nlp(text)
        entities=[ent.text for ent in doc.ents]

        for i in range(len(entities)-1):
            G.add_edge(entities[i],entities[i+1])

    if len(G.nodes()) > 0:

        pos = nx.spring_layout(G)

        node_x=[]
        node_y=[]
        labels=[]

        for node in G.nodes():

            x,y = pos[node]

            node_x.append(x)
            node_y.append(y)
            labels.append(node)

        graph_fig = px.scatter(
            x=node_x,
            y=node_y,
            text=labels,
            title="Entity Relationship Intelligence Graph"
        )

        graph_fig.update_traces(marker=dict(size=20))

        st.plotly_chart(graph_fig,use_container_width=True)

    else:
        st.warning("No entities found for knowledge graph")

    # GLOBAL MAP

    st.header("🌎 Global Intelligence Map")

    world_map = folium.Map(location=[20,0],zoom_start=2)

    locations = {
        "India":[20.59,78.96],
        "United States":[37.09,-95.71],
        "China":[35.86,104.19],
        "Russia":[61.52,105.31],
        "Europe":[54.52,15.25]
    }

    for place,coord in locations.items():

        folium.CircleMarker(
            coord,
            radius=10,
            popup=place,
            color="red",
            fill=True,
            fill_opacity=0.7
        ).add_to(world_map)

    st_folium(world_map,width=900)

    # AI INSIGHTS

    st.header("🤖 AI Strategic Insights")

    st.info(
    """
    • Rising geopolitical signals detected across multiple regions  
    • Artificial Intelligence becoming a dominant strategic sector  
    • Defense cooperation expanding globally  
    • Climate related global risk signals increasing  
    """
    )