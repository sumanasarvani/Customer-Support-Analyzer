# Imports
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import altair as alt

# Session 
session = get_active_session()
session.sql("USE DATABASE CUSTOMER_SUPPORT").collect()
session.sql("USE SCHEMA SUPPORT_ANALYZER").collect()

# Custom CSS 
st.markdown("""
<style>
    .stApp { background-color: #0F1117; color: #FFFFFF; }

    [data-testid="stSidebar"] {
        background-color: #161B27;
        border-right: 1px solid #00D4FF22;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }

    .kpi-card {
        background-color: #161B27;
        border: 1px solid #00D4FF33;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #00D4FF; margin: 0; }
    .kpi-label { font-size: 0.78rem; color: #8B9BB4; margin-top: 6px;
                 text-transform: uppercase; letter-spacing: 0.08em; }

    .section-header {
        color: #00D4FF; font-size: 1rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.1em;
        border-bottom: 1px solid #00D4FF33;
        padding-bottom: 8px; margin-bottom: 16px;
    }
    .page-title { font-size: 1.8rem; font-weight: 700; color: #FFFFFF; margin-bottom: 4px; }
    .page-subtitle { color: #8B9BB4; font-size: 0.95rem; margin-bottom: 24px; }

    .ticket-card {
        background-color: #161B27;
        border: 1px solid #ffffff11;
        border-radius: 8px;
        padding: 16px; margin-bottom: 12px;
    }
    .border-critical { border-left: 4px solid #FF4B4B; }
    .border-high     { border-left: 4px solid #FFA500; }
    .border-medium   { border-left: 4px solid #FFD700; }
    .border-low      { border-left: 4px solid #00FF88; }

    .badge { display:inline-block; padding:3px 10px; border-radius:20px;
             font-size:0.75rem; font-weight:600; margin:2px; }
    .badge-critical { background:#FF4B4B22; color:#FF4B4B; border:1px solid #FF4B4B55; }
    .badge-high     { background:#FFA50022; color:#FFA500; border:1px solid #FFA50055; }
    .badge-medium   { background:#FFD70022; color:#FFD700; border:1px solid #FFD70055; }
    .badge-low      { background:#00FF8822; color:#00FF88; border:1px solid #00FF8855; }
    .badge-negative { background:#FF4B4B22; color:#FF4B4B; border:1px solid #FF4B4B55; }
    .badge-neutral  { background:#8B9BB422; color:#8B9BB4; border:1px solid #8B9BB455; }
    .badge-positive { background:#00FF8822; color:#00FF88; border:1px solid #00FF8855; }
    .badge-blue     { background:#00D4FF22; color:#00D4FF; border:1px solid #00D4FF55; }

    .response-box {
        background:#0D1F2D; border:1px solid #00D4FF33;
        border-radius:8px; padding:14px;
        color:#CBD5E1; font-size:0.9rem; margin-top:8px;
    }
    .alert-card {
        background:#1A0F0F; border:1px solid #FF4B4B44;
        border-left:4px solid #FF4B4B;
        border-radius:8px; padding:16px; margin-bottom:12px;
    }
    hr { border-color: #ffffff11; margin: 24px 0; }
/* Selectbox labels */
    .stSelectbox label {
        color: #00D4FF !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        font-weight: 600 !important;
    }

    /* Selectbox dropdown background */
    .stSelectbox > div > div {
        background-color: #161B27 !important;
        border: 1px solid #ffffff22 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)




# Data
@st.cache_data
def load_data():
    return session.sql("SELECT * FROM TICKET_ANALYSIS_FINAL").to_pandas()

df = load_data()

def dark_bar_chart(data, x_col, y_col, color_hex, title=""):
    return (
        alt.Chart(data, title=title)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color=color_hex)
        .encode(
            x=alt.X(f"{x_col}:N", sort="-y",
                    axis=alt.Axis(labelColor="#8B9BB4", tickColor="#8B9BB4",
                                  domainColor="#ffffff22", labelAngle=-30,
                                  titleColor="#8B9BB4")),
            y=alt.Y(f"{y_col}:Q",
                    axis=alt.Axis(labelColor="#8B9BB4", tickColor="#8B9BB4",
                                  domainColor="#ffffff22", gridColor="#ffffff11",
                                  titleColor="#8B9BB4")),
            tooltip=[x_col, y_col]
        )
        .properties(height=280, background="transparent")
        .configure_view(strokeOpacity=0)
        .configure_title(color="#FFFFFF", fontSize=14)
    )


# Badge helpers 
def urgency_badge(val):
    v = str(val).lower()
    cls = f"badge-{v}" if v in ["critical","high","medium","low"] else "badge-blue"
    return f'<span class="badge {cls}">{str(val).upper()}</span>'

def sentiment_badge(val):
    v = str(val).lower()
    cls = f"badge-{v}" if v in ["positive","neutral","negative"] else "badge-blue"
    return f'<span class="badge {cls}">{str(val).capitalize()}</span>'

def churn_badge(val):
    mapping = {"high":"badge-critical","medium":"badge-medium","low":"badge-low"}
    cls = mapping.get(str(val).lower(), "badge-blue")
    return f'<span class="badge {cls}">Churn: {val}</span>'

def border_class(urgency):
    return {"Critical":"border-critical","High":"border-high",
            "Medium":"border-medium","Low":"border-low"}.get(str(urgency), "")

# Sidebar 
with st.sidebar:
    # Logo / App title
    st.markdown("""
    <div style="padding: 12px 0 8px 0; text-align: center;">
        <div style="font-size: 2rem;">❄️</div>
        <div style="font-size: 1.2rem; font-weight: 800; color: #FFFFFF;
                    letter-spacing: 0.05em;">SUPPORT</div>
        <div style="font-size: 0.75rem; color: #00D4FF; letter-spacing: 0.2em;
                    text-transform: uppercase; margin-top: 2px;">ANALYZER</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Navigation
    page = st.radio("Navigation", ["Overview","Ticket Explorer","Manager Alerts"],
                    label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════
if page == "Overview":
    st.markdown('<div class="page-title">📊 Customer Support Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">AI-powered analysis powered by Snowflake Cortex</div>', unsafe_allow_html=True)

    # ── KPI Cards ─────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    kpis = [
        (c1, len(df),                                        "Total Tickets"),
        (c2, int(df["REQUIRES_MANAGER_ATTENTION"].sum()),    "Needs Manager"),
        (c3, int((df["CHURN_RISK"] == "High").sum()),        "High Churn Risk"),
        (c4, f"{df['BUSINESS_IMPACT_SCORE'].mean():.1f}",    "Avg Impact Score"),
        (c5, f"{df['MANAGER_ALERT_SCORE'].mean():.1f}",      "Avg Alert Score"),
    ]
    for col, val, label in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{val}</div>
                <div class="kpi-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">🧠 Sentiment Breakdown</div>', unsafe_allow_html=True)
        s_data = df["SENTIMENT_LABEL"].value_counts().reset_index()
        s_data.columns = ["Sentiment", "Count"]
        st.altair_chart(dark_bar_chart(s_data, "Sentiment", "Count", "#00D4FF"), use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">⚡ Urgency Breakdown</div>', unsafe_allow_html=True)
        u_data = df["AI_URGENCY"].value_counts().reset_index()
        u_data.columns = ["Urgency", "Count"]
        st.altair_chart(dark_bar_chart(u_data, "Urgency", "Count", "#FF4B4B"), use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">📂 Category Breakdown</div>', unsafe_allow_html=True)
        c_data = df["AI_CATEGORY"].value_counts().reset_index()
        c_data.columns = ["Category", "Count"]
        st.altair_chart(dark_bar_chart(c_data, "Category", "Count", "#00D4FF"), use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">⚠️ Churn Risk Distribution</div>', unsafe_allow_html=True)
        ch_data = df["CHURN_RISK"].value_counts().reset_index()
        ch_data.columns = ["Churn Risk", "Count"]
        st.altair_chart(dark_bar_chart(ch_data, "Churn Risk", "Count", "#FFA500"), use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="section-header">👥 Recommended Team Routing</div>', unsafe_allow_html=True)
    t_data = df["RECOMMENDED_TEAM"].value_counts().reset_index()
    t_data.columns = ["Team", "Count"]
    st.altair_chart(dark_bar_chart(t_data, "Team", "Count", "#00FF88"), use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# PAGE 2 — TICKET EXPLORER
# ═══════════════════════════════════════════════════════════════
elif page == "Ticket Explorer":
    st.markdown('<div class="page-title">🔍 Ticket Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Filter and explore individual AI-analyzed tickets</div>', unsafe_allow_html=True)

    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        urgency_filter = st.selectbox(
            "Urgency",
            options=["All"] + sorted(df["AI_URGENCY"].dropna().unique().tolist())
        )
    with col2:
        churn_filter = st.selectbox(
            "Churn Risk",
            options=["All"] + sorted(df["CHURN_RISK"].dropna().unique().tolist())
        )
    with col3:
        sentiment_filter = st.selectbox(
            "Sentiment",
            options=["All"] + sorted(df["SENTIMENT_LABEL"].dropna().unique().tolist())
        )
    with col4:
        team_filter = st.selectbox(
            "Team",
            options=["All"] + sorted(df["RECOMMENDED_TEAM"].dropna().unique().tolist())
        )

    # Apply Filters
    filtered_df = df.copy()
    if urgency_filter   != "All": filtered_df = filtered_df[filtered_df["AI_URGENCY"]      == urgency_filter]
    if churn_filter     != "All": filtered_df = filtered_df[filtered_df["CHURN_RISK"]       == churn_filter]
    if sentiment_filter != "All": filtered_df = filtered_df[filtered_df["SENTIMENT_LABEL"]  == sentiment_filter]
    if team_filter      != "All": filtered_df = filtered_df[filtered_df["RECOMMENDED_TEAM"] == team_filter]

    st.markdown(f"<div style='color:#8B9BB4;margin:12px 0;'>Showing "
                f"<span style='color:#00D4FF;font-weight:600;'>{len(filtered_df)}</span> tickets</div>",
                unsafe_allow_html=True)

    # Ticket Cards
    for _, row in filtered_df.head(20).iterrows():
        bc = border_class(row.get("AI_URGENCY", ""))
        st.markdown(f"""
        <div class="ticket-card {bc}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <span style="font-weight:700;color:#FFFFFF;font-size:1rem;">
                    🎫 #{int(row['TICKET_ID'])} — {row['CUSTOMER_NAME']}
                </span>
                <span>
                    {urgency_badge(row.get('AI_URGENCY',''))}
                    {sentiment_badge(row.get('SENTIMENT_LABEL',''))}
                    {churn_badge(row.get('CHURN_RISK',''))}
                </span>
            </div>
            <div style="color:#8B9BB4;font-size:0.85rem;margin-bottom:10px;">
                📦 {row['PRODUCT_PURCHASED']} &nbsp;|&nbsp;
                👥 {row['RECOMMENDED_TEAM']} &nbsp;|&nbsp;
                💼 Impact: <span style="color:#00D4FF;">{row['BUSINESS_IMPACT_SCORE']}/100</span> &nbsp;|&nbsp;
                🚨 Alert: <span style="color:#FF4B4B;">{row['MANAGER_ALERT_SCORE']}/100</span>
            </div>
            <div style="color:#CBD5E1;font-size:0.9rem;margin-bottom:8px;">
                <strong style="color:#8B9BB4;">📝 Summary:</strong> {row['AI_SUMMARY']}
            </div>
            <div style="color:#CBD5E1;font-size:0.9rem;margin-bottom:8px;">
                <strong style="color:#8B9BB4;">🔍 Root Cause:</strong> {row['ROOT_CAUSE']}
            </div>
            <div style="color:#8B9BB4;font-size:0.85rem;margin-bottom:6px;">
                <strong>💬 Suggested Response:</strong>
            </div>
            <div class="response-box">{row['SUGGESTED_RESPONSE']}</div>
        </div>
        """, unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════
# PAGE 3 — MANAGER ALERTS
# ═══════════════════════════════════════════════════════════════
elif page == "Manager Alerts":
    st.markdown('<div class="page-title">🚨 Manager Alerts</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Tickets requiring immediate management attention — Alert Score above 80</div>',
                unsafe_allow_html=True)

    alerts_df = df[df["REQUIRES_MANAGER_ATTENTION"] == True].sort_values(
        "MANAGER_ALERT_SCORE", ascending=False)

    st.markdown(f"""
    <div style="background:#1A0F0F;border:1px solid #FF4B4B44;border-radius:8px;
                padding:14px;margin-bottom:20px;">
        <span style="color:#FF4B4B;font-weight:700;font-size:1.1rem;">⚠️ {len(alerts_df)} tickets</span>
        <span style="color:#8B9BB4;"> require immediate manager attention</span>
    </div>
    """, unsafe_allow_html=True)

    for _, row in alerts_df.iterrows():
        st.markdown(f"""
        <div class="alert-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <span style="font-weight:700;color:#FFFFFF;font-size:1rem;">
                    🚨 #{int(row['TICKET_ID'])} — {row['CUSTOMER_NAME']}
                </span>
                <span>
                    {urgency_badge(row.get('AI_URGENCY',''))}
                    {churn_badge(row.get('CHURN_RISK',''))}
                    <span class="badge badge-critical">Alert: {row['MANAGER_ALERT_SCORE']}/100</span>
                </span>
            </div>
            <div style="color:#8B9BB4;font-size:0.85rem;margin-bottom:10px;">
                📧 {row['CUSTOMER_EMAIL']} &nbsp;|&nbsp;
                📦 {row['PRODUCT_PURCHASED']} &nbsp;|&nbsp;
                👥 {row['RECOMMENDED_TEAM']} &nbsp;|&nbsp;
                💼 Impact: <span style="color:#FF4B4B;">{row['BUSINESS_IMPACT_SCORE']}/100</span>
            </div>
            <div style="color:#CBD5E1;font-size:0.9rem;margin-bottom:8px;">
                <strong style="color:#8B9BB4;">📝 Summary:</strong> {row['AI_SUMMARY']}
            </div>
            <div style="color:#CBD5E1;font-size:0.9rem;margin-bottom:8px;">
                <strong style="color:#8B9BB4;">🔍 Root Cause:</strong> {row['ROOT_CAUSE']}
            </div>
            <div style="color:#8B9BB4;font-size:0.85rem;margin-bottom:6px;">
                <strong>💬 Suggested Response:</strong>
            </div>
            <div class="response-box">{row['SUGGESTED_RESPONSE']}</div>
        </div>
        """, unsafe_allow_html=True)