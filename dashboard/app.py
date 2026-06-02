import os
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# ─── 1. CORE CONFIGURATION (MUST BE FIRST) ─────────────────────────────────────
st.set_page_config(
    page_title="India Analytics Job Market Pulse",
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── 2. EXACT PATH RESOLUTION ──────────────────────────────────────────────────
@st.cache_resource
def get_db_path():
    _here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(_here, "..", "data", "job_market.db")
    if not os.path.exists(path):
        path = os.path.join(os.getcwd(), "data", "job_market.db")
    return path

DB_PATH = get_db_path()

# ─── 3. THE "SCORCHED EARTH" CSS ───────────────────────────────────────────────
# We are no longer asking Streamlit to style the button. We are forcing it.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

:root {
    --bg-base: #05050A;
    --card-bg: rgba(15, 23, 42, 0.4);
    --border-glow: rgba(0, 240, 255, 0.2);
    --text-primary: #FFFFFF;
    --text-muted: #94A3B8;
    --cyan: #00F0FF;
    --magenta: #FF2D7E;
}

/* Base App Styling */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', sans-serif !important;
    background-color: var(--bg-base) !important;
    background-image: 
        radial-gradient(circle at 15% 50%, rgba(0, 240, 255, 0.05), transparent 25%),
        radial-gradient(circle at 85% 30%, rgba(255, 45, 126, 0.05), transparent 25%);
    color: var(--text-primary) !important;
}

/* ─── EXTREME MEASURE: BRUTE FORCE THE SIDEBAR BUTTON ─── */
/* We rip the button out of the normal document flow and pin it to the screen */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important; 
    top: 15px !important;
    left: 15px !important;
    z-index: 9999999 !important; /* Maximum z-index */
    background-color: #0F172A !important;
    border: 1px solid #00F0FF !important;
    border-radius: 8px !important;
    padding: 2px !important;
    pointer-events: auto !important;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.3) !important;
}

/* Force the SVG icon colors */
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg {
    fill: #00F0FF !important;
    color: #00F0FF !important;
    width: 26px !important;
    height: 26px !important;
}

/* Hover effects */
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarCollapsedControl"]:hover {
    background-color: #1E293B !important;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.6) !important;
}

/* ─── ASSASSINATE THE CLUTTER ─── */
/* Hide the main header background but leave it physically there so React doesn't panic */
header[data-testid="stHeader"] { 
    background: transparent !important; 
    pointer-events: none !important; 
}

/* Target and destroy ONLY the specific cloud UI elements */
.stDeployButton, 
[data-testid="stToolbar"], 
[data-testid="stDecoration"], 
[data-testid="stStatusWidget"],
.viewerBadge_container, 
#MainMenu, 
footer {
    display: none !important;
    pointer-events: none !important;
    visibility: hidden !important;
}

.block-container { padding: 2rem 2.5rem !important; max-width: 100% !important; }

/* ─── FANCY HEADER ─── */
.premium-header {
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.2) 100%);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-glow);
    border-radius: 16px; padding: 30px; text-align: center; margin-bottom: 30px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}
.title-glow { font-size: 2.2rem; font-weight: 800; background: linear-gradient(90deg, #FFFFFF, #E2E8F0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.title-glow span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.live-pulse { display: inline-flex; align-items: center; gap: 8px; background: rgba(0, 240, 255, 0.1); border: 1px solid var(--cyan); color: var(--cyan); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-top: 15px; }
.pulse-dot { width: 8px; height: 8px; background-color: var(--cyan); border-radius: 50%; animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(0, 240, 255, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(0, 240, 255, 0); } 100% { box-shadow: 0 0 0 0 rgba(0, 240, 255, 0); } }

/* ─── GLASSMORPHISM METRIC CARDS ─── */
.glass-card {
    background: var(--card-bg); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.05); border-top: 3px solid var(--cyan) !important;
    border-radius: 16px; padding: 24px; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2);
}
.glass-card:hover { transform: translateY(-5px); border-color: var(--border-glow); box-shadow: 0 8px 32px 0 rgba(0, 240, 255, 0.15); }
.kpi-icon { font-size: 1.8rem; margin-bottom: 8px; display: block; }
.kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; color: var(--text-primary); line-height: 1.1; text-shadow: 0 0 20px rgba(255, 255, 255, 0.1); }
.kpi-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; margin-top: 8px; font-weight: 600; }

/* ─── UI COMPONENTS ─── */
.fancy-divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border-glow), transparent); margin: 40px 0 20px 0; }
.section-title { display: flex; align-items: center; gap: 12px; font-size: 1.25rem; font-weight: 800; text-transform: uppercase; margin-bottom: 20px; }
.section-title span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

section[data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.95) !important; border-right: 1px solid var(--border-glow) !important; backdrop-filter: blur(20px); }
[data-testid="stDataFrame"] { border: 1px solid var(--border-glow) !important; border-radius: 12px !important; overflow: hidden !important; background: #06093A !important; }
[data-testid="stDataFrame"] [role="columnheader"] { background: #0A0E45 !important; color: var(--cyan) !important; font-weight: 600 !important; }
[data-testid="stDataFrame"] [role="gridcell"] { background: #06093A !important; color: var(--text-primary) !important; border-bottom: 1px solid rgba(255,255,255,0.05) !important; }
.plat-card { background: var(--card-bg); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); padding: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ─── 4. MODERNIZED PLOTLY THEME ENGINE ─────────────────────────────────────────
def generate_glass_layout(height=380):
    return dict(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        height=height,
        font=dict(family='Outfit, sans-serif', color='#F8FAFC', size=13),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False),
        hoverlabel=dict(bgcolor='rgba(15, 23, 42, 0.9)', bordercolor='#00F0FF', font=dict(family='JetBrains Mono')),
        legend=dict(font=dict(color='#F8FAFC'), bgcolor='rgba(0,0,0,0)'),
    )

THEME_COLORS = ['#00F0FF', '#FF2D7E', '#7C3AED', '#00FF9D', '#FFD740', '#FF6B35', '#38BDF8', '#F472B6']

# ─── 5. ROBUST DATA LOADER ─────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_market_data(db_path):
    tables = ['jobs', 'skills', 'city', 'role', 'company']
    if not os.path.exists(db_path):
        return {k: pd.DataFrame() for k in tables}
    
    try:
        with sqlite3.connect(db_path) as conn:
            return {
                'jobs': pd.read_sql("SELECT * FROM jobs", conn),
                'skills': pd.read_sql("SELECT * FROM weekly_skill_trends ORDER BY week", conn),
                'city': pd.read_sql("SELECT * FROM weekly_city_demand ORDER BY week", conn),
                'role': pd.read_sql("SELECT * FROM weekly_role_demand ORDER BY week", conn),
                'company': pd.read_sql("SELECT * FROM weekly_company_demand", conn),
            }
    except Exception as e:
        st.error(f"Database Error: {e}")
        return {k: pd.DataFrame() for k in tables}

# Extract and Clean Data
data = fetch_market_data(DB_PATH)
df_jobs, df_skills, df_city, df_role, df_company = data['jobs'], data['skills'], data['city'], data['role'], data['company']

if not df_jobs.empty and 'city_normalized' in df_jobs.columns:
    df_jobs['city_normalized'] = df_jobs['city_normalized'].str.title()
if not df_city.empty and 'city' in df_city.columns:
    df_city['city'] = df_city['city'].str.title()

# ─── 6. SIDEBAR CONTROLS ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00F0FF;'>Global Filters</h2>", unsafe_allow_html=True)
    
    cities_list = sorted(df_jobs["city_normalized"].dropna().unique()) if not df_jobs.empty else []
    roles_list  = sorted(df_jobs["role_category"].dropna().unique()) if not df_jobs.empty else []
    weeks_list  = sorted(df_skills["week"].unique()) if not df_skills.empty else []
    
    user_cities = st.multiselect("Cities", cities_list, default=[], placeholder="All cities")
    user_roles  = st.multiselect("Roles", roles_list, default=[], placeholder="All roles")
    user_exp    = st.slider("Max Exp (yrs)", 0, 15, 15)
    
    week_bounds = (weeks_list[0], weeks_list[-1]) if len(weeks_list) >= 2 else (None, None)
    if len(weeks_list) >= 2:
        week_bounds = st.select_slider("Week Range", options=weeks_list, value=week_bounds)
    
    st.markdown("---")
    st.markdown(f"<div style='font-size:0.75rem; color:#94A3B8;'>UPDATED: <span style='color:#00F0FF'>{datetime.now().strftime('%d %b %Y')}</span><br>LIVE DB HOOK ACTIVE</div>", unsafe_allow_html=True)

# ─── 7. APPLY LOGIC FILTERS ────────────────────────────────────────────────────
filtered_jobs = df_jobs.copy()
if not filtered_jobs.empty:
    if user_cities: filtered_jobs = filtered_jobs[filtered_jobs["city_normalized"].isin(user_cities)]
    if user_roles:  filtered_jobs = filtered_jobs[filtered_jobs["role_category"].isin(user_roles)]
    filtered_jobs = filtered_jobs[filtered_jobs["exp_min"].fillna(0) <= user_exp]

filtered_skills = df_skills.copy()
if not filtered_skills.empty and week_bounds[0]:
    filtered_skills = filtered_skills[(filtered_skills["week"] >= week_bounds[0]) & (filtered_skills["week"] <= week_bounds[1])]

# Calculate core metrics dynamically
total_jobs  = len(filtered_jobs)
avg_salary  = round(filtered_jobs["salary_min_lpa"].dropna().mean(), 1) if not filtered_jobs.empty and filtered_jobs["salary_min_lpa"].notna().any() else "N/A"
top_city    = filtered_jobs["city_normalized"].mode()[0] if not filtered_jobs.empty and not filtered_jobs["city_normalized"].mode().empty else "—"
fresher_pct = round(100 * filtered_jobs["is_fresher_role"].sum() / max(total_jobs, 1), 1) if not filtered_jobs.empty else 0
top_skill   = filtered_skills.groupby("skill")["mention_count"].sum().idxmax().upper() if not filtered_skills.empty else "—"
num_weeks   = df_skills["week"].nunique() if not df_skills.empty else 0

# ─── 8. DASHBOARD RENDERING ────────────────────────────────────────────────────
if df_jobs.empty:
    st.error("⚠️ Database is empty or missing. Please run your scraper.")
    st.stop()

st.markdown(f"""
<div class="premium-header">
  <div class="title-glow">India Analytics & AI <span>Job Market Pulse</span></div>
  <div style="color:#94A3B8; margin-top:8px;">Real-time intelligence · Naukri · LinkedIn · Internshala</div>
  <div class="live-pulse"><div class="pulse-dot"></div> LIVE DATAFEED ({num_weeks} WEEKS)</div>
</div>
""", unsafe_allow_html=True)

# Render KPIs
cols = st.columns(5)
metrics_data = [
    ("📊", f"{total_jobs:,}", "Total Jobs Scraped"),
    ("💰", f"₹{avg_salary}L", "Avg Min Salary (LPA)"),
    ("🏙️", top_city, "Top Hiring Hub"),
    ("🎓", f"{fresher_pct}%", "Fresher Friendly"),
    ("⚡", top_skill, "Highest Demand Skill")
]
for col, (icon, val, label) in zip(cols, metrics_data):
    col.markdown(f'<div class="glass-card"><span class="kpi-icon">{icon}</span><div class="kpi-value">{val}</div><div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

# Skills Analysis
st.markdown('<div class="fancy-divider"></div><div class="section-title">⚡ <span>Skills Intelligence</span></div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    if not filtered_skills.empty:
        t20 = filtered_skills.groupby("skill")["mention_count"].sum().nlargest(20).sort_values(ascending=True).reset_index()
        fig1 = go.Figure(go.Bar(
            x=t20["mention_count"], y=t20["skill"], orientation='h',
            marker=dict(color=t20["mention_count"], colorscale=['#7C3AED', '#FF2D7E', '#00F0FF'])
        ))
        layout1 = generate_glass_layout(500)
        layout1.update(title="Top 20 Skills Demanded", xaxis_title="Mentions")
        fig1.update_layout(**layout1)
        st.plotly_chart(fig1, use_container_width=True)

with c2:
    if not filtered_skills.empty:
        top8_skills = filtered_skills.groupby("skill")["mention_count"].sum().nlargest(8).index
        fig2 = go.Figure()
        for i, skill in enumerate(top8_skills):
            s_data = filtered_skills[filtered_skills["skill"] == skill]
            fig2.add_trace(go.Scatter(x=s_data["week"], y=s_data["mention_count"], name=skill, line=dict(color=THEME_COLORS[i % len(THEME_COLORS)], width=3)))
        layout2 = generate_glass_layout(500)
        layout2.update(title="Weekly Velocity — Top 8 Skills", legend=dict(orientation='h', y=-0.2))
        fig2.update_layout(**layout2)
        st.plotly_chart(fig2, use_container_width=True)

# Geographic & Market Breakdown
st.markdown('<div class="fancy-divider"></div><div class="section-title">🗺️ <span>Market Logistics</span></div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    if not df_city.empty:
        ct = df_city.groupby("city")["job_count"].sum().reset_index().sort_values("job_count", ascending=False)
        fig3 = go.Figure(go.Bar(x=ct["city"], y=ct["job_count"], marker=dict(color=ct["job_count"], colorscale='Tealgrn')))
        layout3 = generate_glass_layout(320)
        layout3.update(title="Job Volume by Hub")
        fig3.update_layout(**layout3)
        st.plotly_chart(fig3, use_container_width=True)

with c4:
    if not df_role.empty:
        rt = df_role.groupby("role_category")["job_count"].sum().reset_index()
        fig4 = go.Figure(go.Pie(labels=rt["role_category"], values=rt["job_count"], hole=0.7, marker=dict(colors=THEME_COLORS)))
        layout4 = generate_glass_layout(320)
        layout4.update(title="Role Category Split", showlegend=False)
        fig4.update_layout(**layout4)
        st.plotly_chart(fig4, use_container_width=True)

# Data Registry
st.markdown('<div class="fancy-divider"></div><div class="section-title">🔍 <span>Production Database Registry</span></div>', unsafe_allow_html=True)
if not filtered_jobs.empty:
    search_q = st.text_input("Search DB", placeholder="Search titles, tech stacks...", label_visibility="collapsed")
    display_df = filtered_jobs.sort_values("scrape_date", ascending=False)
    if search_q:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_q, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]
    
    st.dataframe(display_df.head(100), use_container_width=True, hide_index=True)