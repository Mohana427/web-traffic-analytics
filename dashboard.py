import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DB_NAME = "analytics.db"

st.set_page_config(page_title="Web Traffic Analytics", layout="wide")

st.markdown(
    """
    <style>
    /* Premium Dark Mode Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0B0E14 0%, #1A202C 100%);
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Elegant styling for Metric cards (Glassmorphism effect) */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Metrics Label and Value Colors */
    [data-testid="stMetricLabel"] {
        color: #A0AEC0 !important;
        font-weight: 500;
        font-size: 1rem;
    }
    [data-testid="stMetricValue"] {
        color: #F7FAFC !important;
        font-weight: 700;
        font-size: 2.2rem;
        background: -webkit-linear-gradient(45deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Header Typography */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Web Traffic Analytics Dashboard")

def load_data(query):
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        df = pd.DataFrame()
    conn.close()
    return df

# Load daily metrics
daily_metrics = load_data("SELECT * FROM daily_metrics ORDER BY date")

if daily_metrics.empty:
    st.warning("No data found. Please run the app.py to collect events, or mock_data.py to generate data, and then run etl.py.")
    st.stop()

# KPIs
st.header("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

latest = daily_metrics.iloc[-1]
col1.metric("Total Sessions (Latest Day)", int(latest['total_sessions']))
col2.metric("Avg Session Duration", f"{latest['avg_duration']:.1f}s")
col3.metric("Bounce Rate", f"{latest['bounce_rate']*100:.1f}%")
col4.metric("Total Page Views", int(latest['total_page_views']))

st.divider()

# Daily Trends
st.header("Traffic Trends")
fig = px.line(
    daily_metrics, x='date', y='total_sessions', title='Daily Sessions',
    line_shape='spline', render_mode='svg'
)
fig.update_traces(line=dict(color='#00d2ff', width=3), fill='tozeroy', fillcolor='rgba(0, 210, 255, 0.1)')
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#A0AEC0'),
    title_font=dict(color='#FFFFFF', size=20),
    xaxis=dict(showgrid=False, title=''),
    yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', title='')
)
st.plotly_chart(fig, use_container_width=True)

# Funnel Analysis
st.header("User Journey Funnel")
sessions = load_data("SELECT * FROM processed_sessions")

# Count occurrences of specific pages to build the funnel
pages_order = ["Home", "Products", "Cart", "Checkout"]
funnel_data = []

# To keep it simple, we check if the path contains the page.
# In a real scenario, this would be a strict sequence check.
for page in pages_order:
    # A user reached a stage if it's in their path
    count = sessions['path'].str.contains(page).sum()
    funnel_data.append(dict(number=count, stage=page))

fig_funnel = go.Figure(go.Funnel(
    y=[d["stage"] for d in funnel_data],
    x=[d["number"] for d in funnel_data],
    textinfo="value+percent initial",
    marker=dict(
        color=['#3a7bd5', '#3a8bd5', '#3a9bd5', '#3aabd5'],
        line=dict(width=0)
    )
))
fig_funnel.update_layout(
    title="Conversion Funnel",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#A0AEC0'),
    title_font=dict(color='#FFFFFF', size=20)
)
st.plotly_chart(fig_funnel, use_container_width=True)

st.divider()

# Drop-off Analysis (Exit Pages)
st.header("Drop-off Analysis")
exit_pages = sessions.groupby('exit_page').size().reset_index(name='count')
exit_pages = exit_pages.sort_values(by='count', ascending=False)

fig_exit = px.bar(
    exit_pages, x='exit_page', y='count', title='Top Exit Pages (Drop-offs)',
    color='count', color_continuous_scale=['#3a7bd5', '#00d2ff']
)
fig_exit.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#A0AEC0'),
    title_font=dict(color='#FFFFFF', size=20),
    xaxis=dict(showgrid=False, title=''),
    yaxis=dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', title=''),
    coloraxis_showscale=False
)
st.plotly_chart(fig_exit, use_container_width=True)
