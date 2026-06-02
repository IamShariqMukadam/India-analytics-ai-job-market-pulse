import os
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import streamlit.components.v1 as components

# ─── 1. CORE CONFIG & EXACT PATHS ──────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_here, "..", "data", "job_market.db")
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(os.getcwd(), "data", "job_market.db")

# Changed page icon to a Suitcase 💼
st.set_page_config(
    page_title="India Analytics Job Market Pulse",
    page_icon="💼", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── 2. PREMIUM DARK GLASSMORPHISM CSS & RESPONSIVENESS ────────────────────────
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
    --violet: #7C3AED;
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

/* ─── GHOSTING THE NATIVE HEADER CLUTTER ─── */
header[data-testid="stHeader"], .stAppHeader { 
    background: transparent !important; 
    box-shadow: none !important;
    pointer-events: none !important;
}

/* Hide native header buttons, toolbars, and menus */
header[data-testid="stHeader"] button,
header[data-testid="stHeader"] a,
.stDeployButton, 
[data-testid="stToolbar"], 
[data-testid="stDecoration"], 
[data-testid="stStatusWidget"], 
#MainMenu, 
footer {
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
    position: absolute !important;
}

/* ─── MOVE STREAMLIT / GITHUB BADGE TO TOP RIGHT ─── */
.viewerBadge_container {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    bottom: 15px !important;
    top: 15px !important;
    right: 15px !important;
    z-index: 999999 !important;
    pointer-events: auto !important;
}
/* Surgically target and destroy ONLY the Streamlit link inside the badge */
.viewerBadge_container a[href*="streamlit.io"],
.viewerBadge_link[href*="streamlit.io"] {
    display: none !important;
}

/* Permanently hide native toggles */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"] {
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
}

/* Nuke the empty iframe container */
iframe[title="streamlit_components.v1.html"] {
    display: none !important; position: absolute !important; width: 0 !important; height: 0 !important;
}

.block-container { padding: 2rem 2.5rem 1.5rem 2.5rem !important; max-width: 100% !important; }

/* ─── FANCY HEADER ─── */
.premium-header {
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.2) 100%);
    backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-glow); border-radius: 16px;
    padding: 30px; text-align: center; margin-bottom: 30px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}
.title-glow { font-size: 2.2rem; font-weight: 800; background: linear-gradient(90deg, #FFFFFF, #E2E8F0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; }
.title-glow span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.live-pulse { display: inline-flex; align-items: center; gap: 8px; background: rgba(0, 240, 255, 0.1); border: 1px solid var(--cyan); color: var(--cyan); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-top: 15px; letter-spacing: 2px; }
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
.kpi-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 8px; font-weight: 600; }

/* ─── SECTION HEADERS ─── */
.fancy-divider { height: 1px; background: linear-gradient(90deg, transparent, var(--border-glow), transparent); margin: 40px 0 20px 0; }
.section-title { display: flex; align-items: center; gap: 12px; font-size: 1.25rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 20px; }
.section-title span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* ─── COMPONENT OVERRIDES ─── */
[data-testid="stDataFrame"], [data-testid="stDataFrame"] > div { background-color: #06093A !important; }
[data-testid="stDataFrame"] [role="columnheader"] { background-color: #0A0E45 !important; color: var(--cyan) !important; border-bottom: 2px solid var(--border-glow) !important; }
[data-testid="stDataFrame"] [role="gridcell"] { background-color: #06093A !important; color: var(--text-primary) !important; border-bottom: 1px solid rgba(0, 240, 255, 0.1) !important; }
[data-testid="stDataFrame"] [role="row"]:hover [role="gridcell"] { background-color: rgba(0, 240, 255, 0.08) !important; }
section[data-testid="stSidebar"] { background: rgba(15, 23, 42, 0.95) !important; border-right: 1px solid var(--border-glow) !important; backdrop-filter: blur(20px); }
div[data-baseweb="select"] > div { background: rgba(2, 6, 23, 0.8) !important; border-color: rgba(0, 240, 255, 0.2) !important; }
.stMultiSelect [data-baseweb="tag"] { background: rgba(0, 240, 255, 0.1) !important; border: 1px solid var(--cyan) !important; color: var(--text-primary) !important; }
.plat-card { background: var(--card-bg); border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); padding: 20px; text-align: center; }
[data-testid="stTextInput"] div[data-baseweb="input"] { background-color: rgba(15, 23, 42, 0.6) !important; border: 1px solid var(--cyan) !important; border-radius: 8px !important; transition: all 0.3s ease; }
[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within { border: 1px solid var(--magenta) !important; box-shadow: 0 0 12px rgba(255, 45, 126, 0.4) !important; }
[data-testid="stTextInput"] input { color: var(--text-primary) !important; }

/* ─── MOBILE RESPONSIVENESS ─── */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.75rem 1rem 0.75rem !important;
    }

    /* Stack all columns vertically */
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        gap: 12px !important;
    }
    [data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* KPI cards: 2-per-row grid */
    .glass-card, .plat-card {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 auto !important;
        padding: 16px !important;
    }
    .kpi-value { font-size: 1.5rem !important; }
    .kpi-label { font-size: 0.7rem !important; }
    .kpi-icon  { font-size: 1.4rem !important; }

    /* Charts: full width, no internal scroll, no toolbar */
    [data-testid="stPlotlyChart"],
    .stPlotlyChart, .js-plotly-plot, .plotly {
        width: 100% !important;
        touch-action: pan-y !important;
        overflow: hidden !important;
        margin-bottom: 16px !important;
    }

    /* Hide ALL plotly modebar buttons (belt-and-suspenders) */
    .modebar, .modebar-container, .modebar-group {
        display: none !important;
    }

    /* Remove plotly's internal top whitespace caused by hidden modebar */
    .js-plotly-plot .plotly .main-svg {
        margin-top: 0 !important;
    }
    .js-plotly-plot .plotly .svg-container {
        margin-top: 0 !important;
    }

    /* Fullscreen button: remove (causes tap-trap on mobile) */
    [data-testid="StyledFullScreenButton"],
    button[title="View fullscreen"] {
        display: none !important;
    }

    /* Section titles: smaller on mobile */
    .section-title {
        font-size: 1rem !important;
        letter-spacing: 1px !important;
    }
    .title-glow { font-size: 1.6rem !important; }

    /* Tables: horizontal scroll */
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] > div {
        overflow-x: auto !important;
        width: 100% !important;
        -webkit-overflow-scrolling: touch !important;
    }
    /* Shrink dataframe font for mobile */
    [data-testid="stDataFrame"] [role="gridcell"],
    [data-testid="stDataFrame"] [role="columnheader"] {
        font-size: 0.75rem !important;
        padding: 6px 8px !important;
        white-space: nowrap !important;
    }

    /* Footer: stack vertically */
    div[style*="justify-content: space-between"] {
        flex-direction: column !important;
        gap: 8px !important;
        text-align: center !important;
    }

    /* Sidebar toggle button: reposition for mobile */
    #cyber-toggle-btn {
        bottom: 20px !important;
        left: 15px !important;
        width: 46px !important;
        height: 46px !important;
    }

    /* BI tool battle: ratio card full width */
    .glass-card[style*="padding:30px"] {
        padding: 16px !important;
    }
}
/* ─── KILL RED STREAMLIT BADGE, KEEP GITHUB ─── */
a[href*="streamlit.io/cloud"],
a[href*="share.streamlit.io"],
a[href*="streamlit.io"] img[alt*="Streamlit"],
.viewerBadge_link[href*="streamlit.io"],
footer a[href*="streamlit.io"],
#badges a[href*="streamlit.io"] {
    display: none !important;
    visibility: hidden !important;
    pointer-events: none !important;
}
</style>
""", unsafe_allow_html=True)

# ─── THE JAVASCRIPT DOM ESCAPE HATCH (INTELLIGENT CLICK ROUTING) ───
components.html("""
<script>
(function() {
    const doc = window.parent.document;
    
    if (doc.getElementById('cyber-toggle-btn')) return;

    // Create custom master controller floating element with SUITCASE ICON
    const btn = doc.createElement('div');
    btn.id = 'cyber-toggle-btn';
    btn.innerHTML = `
        <div class="cyber-inner">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="26" height="26" fill="#00F0FF">
                <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"></path>
            </svg>
        </div>
    `;

    // Inject styles directly onto window root head layer
    const style = doc.createElement('style');
    style.innerHTML = `
        #cyber-toggle-btn {
            position: fixed;
            bottom: 30px;
            left: 30px;
            width: 54px;
            height: 54px;
            border-radius: 12px;
            background: #0F172A;
            z-index: 99999999 !important;
            cursor: pointer;
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s ease;
            overflow: hidden !important; /* CRITICAL FIX: This makes it a tracing line instead of a huge square! */
        }
        #cyber-toggle-btn:active {
            transform: scale(0.92);
        }
        #cyber-toggle-btn::before {
            content: '';
            position: absolute;
            width: 250%; height: 250%;
            top: -75%; left: -75%;
            background: conic-gradient(transparent 0deg, transparent 240deg, rgba(0, 240, 255, 0.9) 240deg, #3B82F6 360deg);
            animation: border-trace 2s linear infinite;
            z-index: 0;
        }
        #cyber-toggle-btn .cyber-inner {
            position: absolute;
            inset: 3px;
            background: #0F172A;
            border-radius: 9px;
            z-index: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.3s;
        }
        #cyber-toggle-btn:hover .cyber-inner {
            background: #1E293B;
        }
        #cyber-toggle-btn svg {
            z-index: 2;
        }
        @keyframes border-trace {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    doc.head.appendChild(style);

    // Smart Toggle Execution Loop
    btn.onclick = function() {
        const closeControl = doc.querySelector('[data-testid="stSidebarCollapseButton"] button') || 
                             doc.querySelector('[data-testid="stSidebarCollapseButton"]');
                             
        const openControl = doc.querySelector('[data-testid="stSidebarCollapsedControl"] button') || 
                            doc.querySelector('[data-testid="stSidebarCollapsedControl"]') ||
                            doc.querySelector('[data-testid="collapsedControl"] button');

        if (closeControl && closeControl.getBoundingClientRect().width > 0) {
            closeControl.click();
        } else if (openControl) {
            openControl.click();
        } else {
            const fallbackHeaderBtn = doc.querySelector('header button');
            if (fallbackHeaderBtn) fallbackHeaderBtn.click();
        }
    };

    doc.body.appendChild(btn);
})();
</script>
""", height=0, width=0)

components.html("""
<script>
(function killStreamlitBadge() {
    function nuke() {
        const doc = window.parent.document;
        // Target all anchors linking to streamlit.io
        doc.querySelectorAll('a[href*="streamlit.io"]').forEach(el => {
            // But preserve any GitHub-related siblings
            if (!el.href.includes('github')) {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                // Also hide the parent li/div if it becomes empty
                const parent = el.parentElement;
                if (parent && parent.children.length === 1) {
                    parent.style.display = 'none';
                }
            }
        });
        // Also nuke any iframe injected by Streamlit Cloud for the badge
        doc.querySelectorAll('iframe').forEach(iframe => {
            try {
                if (iframe.src && iframe.src.includes('streamlit.io')) {
                    iframe.style.display = 'none';
                }
            } catch(e) {}
        });
    }
    // Run immediately + after DOM settles
    nuke();
    setTimeout(nuke, 500);
    setTimeout(nuke, 2000);
    // Watch for dynamic injection
    const obs = new MutationObserver(nuke);
    obs.observe(window.parent.document.body, { childList: true, subtree: true });
})();
</script>
""", height=0, width=0)


# ─── 3. PLOTLY CHART THEME ENGINE ──────────────────────────────────────────────
def fancy_layout(h=380):
    """Generates a perfect dark-mode glass layout for Plotly."""
    return dict(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        height=h,
        font=dict(family='Outfit, sans-serif', color='#F8FAFC', size=13),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False, tickfont=dict(color='#94A3B8')),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zeroline=False, tickfont=dict(color='#94A3B8')),
        hoverlabel=dict(bgcolor='rgba(15, 23, 42, 0.9)', bordercolor='#00F0FF', font=dict(family='JetBrains Mono')),
        legend=dict(font=dict(color='#F8FAFC'), bgcolor='rgba(0,0,0,0)'),
        dragmode=False, # <-- ADD THIS LINE HERE
    )

COLORS = ['#00F0FF', '#FF2D7E', '#7C3AED', '#00FF9D', '#FFD740', '#FF6B35', '#38BDF8', '#F472B6']

# ─── 4. DATA LOADER ────────────────────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def load_data():
    if not os.path.exists(DB_PATH):
        return {k: pd.DataFrame() for k in ['jobs','skills','city','role','company']}
    conn = sqlite3.connect(DB_PATH)
    try:
        return {
            'jobs'   : pd.read_sql("SELECT * FROM jobs", conn),
            'skills' : pd.read_sql("SELECT * FROM weekly_skill_trends ORDER BY week", conn),
            'city'   : pd.read_sql("SELECT * FROM weekly_city_demand ORDER BY week", conn),
            'role'   : pd.read_sql("SELECT * FROM weekly_role_demand ORDER BY week", conn),
            'company': pd.read_sql("SELECT * FROM weekly_company_demand", conn),
        }
    finally:
        conn.close()

data       = load_data()
jobs_df    = data['jobs']
skills_df  = data['skills']
city_df    = data['city']
role_df    = data['role']
company_df = data['company']

# ─── DATA CLEANING: FORCE CAPITALIZATION GLOBALLY ───
if not jobs_df.empty and 'city_normalized' in jobs_df.columns:
    jobs_df['city_normalized'] = jobs_df['city_normalized'].str.title()
if not city_df.empty and 'city' in city_df.columns:
    city_df['city'] = city_df['city'].str.title()

# ─── 5. SIDEBAR FILTERS ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <h2 style='text-align: center; margin-top: 0; background: linear-gradient(90deg, #00F0FF, #FF2D7E); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            Global Filters
        </h2>
    """, unsafe_allow_html=True)
    
    all_cities = sorted(jobs_df["city_normalized"].dropna().unique()) if not jobs_df.empty else []
    all_roles  = sorted(jobs_df["role_category"].dropna().unique())   if not jobs_df.empty else []
    all_weeks  = sorted(skills_df["week"].unique())                   if not skills_df.empty else []
    
    sel_cities = st.multiselect("Cities", all_cities, default=[], placeholder="All cities")
    sel_roles  = st.multiselect("Roles", all_roles, default=[], placeholder="All roles")
    sel_exp    = st.slider("Max Exp (yrs)", 0, 15, 15)
    
    week_range = (all_weeks[0], all_weeks[-1]) if len(all_weeks) >= 2 else (None, None)
    if len(all_weeks) >= 2:
        week_range = st.select_slider("Week Range", options=all_weeks, value=week_range)
    
    st.markdown("---")
    st.markdown(f"<div style='font-family:JetBrains Mono; font-size:0.75rem; color:#94A3B8;'>UPDATED: <span style='color:#00F0FF'>{datetime.now().strftime('%d %b %Y')}</span><br>LIVE DB HOOK ACTIVE</div>", unsafe_allow_html=True)

# Apply Filters
filt = jobs_df.copy()
if not filt.empty:
    if sel_cities: filt = filt[filt["city_normalized"].isin(sel_cities)]
    if sel_roles:  filt = filt[filt["role_category"].isin(sel_roles)]
    filt = filt[filt["exp_min"].fillna(0) <= sel_exp]

sk_filt = skills_df.copy()
if not sk_filt.empty and week_range[0]:
    sk_filt = sk_filt[(sk_filt["week"] >= week_range[0]) & (sk_filt["week"] <= week_range[1])]

# Metrics Setup
total  = len(filt)
avg_s  = round(filt["salary_min_lpa"].dropna().mean(), 1) if not filt.empty and filt["salary_min_lpa"].notna().any() else "N/A"
top_c  = filt["city_normalized"].value_counts().idxmax().title() if not filt.empty and len(filt) else "—"
frsh   = round(100 * filt["is_fresher_role"].sum() / max(len(filt), 1), 1) if not filt.empty else 0
top_sk = sk_filt.groupby("skill")["mention_count"].sum().idxmax().upper() if not sk_filt.empty else "—"
n_wks  = skills_df["week"].nunique() if not skills_df.empty else 0

# ─── 6. MAIN DASHBOARD BODY ────────────────────────────────────────────────────
if jobs_df.empty:
    st.error(f"⚠️ No data found at `{DB_PATH}`. Please run scraper first.")
    st.stop()

st.markdown(f"""
<div class="premium-header">
  <div class="title-glow">India Analytics & AI <span>Job Market Pulse</span></div>
  <div style="font-family:JetBrains Mono; color:#94A3B8; margin-top:8px;">Real-time intelligence · Naukri · LinkedIn · Internshala</div>
  <div class="live-pulse"><div class="pulse-dot"></div> LIVE DATAFEED ({n_wks} WEEKS)</div>
</div>
""", unsafe_allow_html=True)

# KPI Row
c1,c2,c3,c4,c5 = st.columns(5)
metrics = [
    (c1, "📊", f"{total:,}", "Total Jobs Scraped"),
    (c2, "💰", f"₹{avg_s}L", "Avg Min Salary (LPA)"),
    (c3, "🏙️", top_c, "Top Hiring Hub"),
    (c4, "🎓", f"{frsh}%", "Fresher Friendly"),
    (c5, "⚡", top_sk, "Highest Demand Skill")
]
for col, icon, val, label in metrics:
    with col:
        st.markdown(f'<div class="glass-card"><span class="kpi-icon">{icon}</span><div class="kpi-value">{val}</div><div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

# ─── SKILLS INTEL ──────────────────────────────────────────────────────────────
st.markdown('<div class="fancy-divider"></div><div class="section-title">⚡ <span>Skills Intelligence</span></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if not sk_filt.empty:
        t20 = sk_filt.groupby("skill")["mention_count"].sum().sort_values(ascending=True).tail(20).reset_index()
        fig = go.Figure(go.Bar(
            x=t20["mention_count"], y=t20["skill"], orientation='h',
            marker=dict(color=t20["mention_count"], colorscale=['#7C3AED', '#FF2D7E', '#00F0FF']),
            hovertemplate='<b>%{y}</b><br>%{x} mentions<extra></extra>'
        ))
        L = fancy_layout(500); L['title'] = "Top 20 Skills Demanded"
        fig.update_layout(**L)
        L['xaxis_title'] = "Number of Mentions in Job Postings"
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col2:
    if not sk_filt.empty:
        top8 = sk_filt.groupby("skill")["mention_count"].sum().nlargest(8).index.tolist()
        tr = sk_filt[sk_filt["skill"].isin(top8)]
        fig2 = go.Figure()
        for skill, color in zip(top8, COLORS):
            d = tr[tr["skill"]==skill]
            fig2.add_trace(go.Scatter(
                x=d["week"], y=d["mention_count"], name=skill,
                line=dict(color=color, width=3), mode='lines+markers',
                hovertemplate=f'<b>{skill}</b><br>%{{y}} mentions<extra></extra>',
            ))
        L2 = fancy_layout(500); L2['title'] = "Weekly Velocity — Top 8 Skills"
        L2['legend'] = dict(orientation='h', y=-0.2)
        fig2.update_layout(**L2)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

# BI Tool Matchup
if not sk_filt.empty:
    bi = sk_filt[sk_filt["skill"].isin(["power bi","tableau","looker","qlik"])]
    if not bi.empty:
        st.markdown('<div class="section-title" style="margin-top:20px">⚔️ <span>BI Tool Battle</span></div>', unsafe_allow_html=True)
        ca, cb = st.columns([2,1])
        with ca:
            fig3 = go.Figure()
            bi_c = {"power bi":"#00F0FF","tableau":"#FF6B35","looker":"#00FF9D","qlik":"#FF2D7E"}
            for skill in bi["skill"].unique():
                d = bi[bi["skill"]==skill]; c = bi_c.get(skill,"#fff")
                fig3.add_trace(go.Scatter(x=d["week"], y=d["mention_count"], name=skill.title(), line=dict(color=c, width=3), mode='lines+markers'))
            L3 = fancy_layout(280); L3['legend'] = dict(orientation='h', y=1.2)
            fig3.update_layout(**L3)
            L3['xaxis'] = dict(tickangle=-45, nticks=10, gridcolor='rgba(255,255,255,0.05)')
            L3['yaxis_title'] = "Weekly Mentions"
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
        with cb:
            pb = bi[bi.skill=="power bi"]["mention_count"].sum()
            tb = bi[bi.skill=="tableau"]["mention_count"].sum()
            ratio = round(pb/tb, 1) if tb > 0 else "N/A"
            st.markdown(f"""
            <div class='glass-card' style='padding:30px'>
              <div style='font-size:0.8rem; color:var(--text-muted); letter-spacing:2px;'>POWER BI vs TABLEAU</div>
              <div style='font-family:JetBrains Mono; font-size:3rem; font-weight:800; color:var(--cyan); text-shadow: 0 0 20px rgba(0,240,255,0.4);'>{ratio}x</div>
              <div style='font-size:0.9rem; margin-top:10px'>Power BI holds dominant market volume.</div>
            </div>
            """, unsafe_allow_html=True)

# ─── GEO ANALYSIS ──────────────────────────────────────────────────────────────
st.markdown('<div class="fancy-divider"></div><div class="section-title">🗺️ <span>Geo & Market Logistics</span></div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    if not city_df.empty:
        ct = city_df.groupby("city")["job_count"].sum().reset_index().sort_values("job_count", ascending=False)
        fig4 = go.Figure(go.Bar(
            x=ct["city"], y=ct["job_count"],
            marker=dict(color=ct["job_count"], colorscale='Tealgrn'),
        ))
        L4 = fancy_layout(320); L4['title'] = "Job Volume by Hub"
        fig4.update_layout(**L4)
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

with col4:
    if not role_df.empty:
        rt = role_df.groupby("role_category")["job_count"].sum().reset_index()
        fig7 = go.Figure(go.Pie(
            labels=rt["role_category"], values=rt["job_count"], hole=0.7,
            marker=dict(colors=COLORS, line=dict(color='#05050A', width=3)),
            textinfo='label+percent', textposition='outside'
        ))
        L7 = fancy_layout(320); L7['title'] = "Role Category Split"; L7['showlegend'] = False
        L7['margin'].update(l=40, r=40, t=40, b=60) # Adds 80px of extra breathing room on the left/right for the text
        fig7.update_layout(**L7)
        st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': False})

# City Intelligence Matrix
if not city_df.empty:
    st.markdown('<div class="section-title" style="margin-top: 20px;">🏙️ <span>City Intelligence Matrix</span></div>', unsafe_allow_html=True)
    tbl = city_df.groupby("city").agg(Jobs=("job_count","sum"), Salary=("avg_salary_min","mean"), Fresher=("fresher_pct","mean")).reset_index()
    tbl.columns = ["City","Total Jobs","Avg Salary (LPA)","Fresher %"]
    tbl[["Avg Salary (LPA)","Fresher %"]] = tbl[["Avg Salary (LPA)","Fresher %"]].round(1)
    tbl = tbl.sort_values("Total Jobs", ascending=False).reset_index(drop=True)
    st.dataframe(tbl, use_container_width=True, hide_index=True,
        column_config={
            "Total Jobs": st.column_config.ProgressColumn("Total Jobs", min_value=0, max_value=int(tbl["Total Jobs"].max()), format="%d"),
            "Avg Salary (LPA)": st.column_config.NumberColumn("Avg Salary (LPA)", format="%.1f LPA"),
            "Fresher %": st.column_config.ProgressColumn("Fresher %", min_value=0, max_value=100, format="%.1f%%"),
        })

# ─── MARKET INTELLIGENCE ───────────────────────────────────────────────────────
st.markdown('<div class="fancy-divider"></div><div class="section-title">🧠 <span>Market Intelligence</span></div>', unsafe_allow_html=True)

col5, col6 = st.columns([1.2, 1])
with col5:
    if not company_df.empty:
        co = company_df.groupby("company")["job_count"].sum().sort_values(ascending=True).tail(15).reset_index()
        
        bar_colors = [COLORS[i % len(COLORS)] for i in range(len(co))]
        
        fig6 = go.Figure(go.Bar(
            x=co["job_count"], y=co["company"], orientation='h',
            marker=dict(color=bar_colors), 
            hovertemplate='<b>%{y}</b><br>%{x} openings<extra></extra>'
        ))
        L6 = fancy_layout(450); L6['title'] = "Top 15 Hiring Companies"
        L6['xaxis_title'] = "Total Active Job Openings" 
        fig6.update_layout(**L6)
        st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})

with col6:
    if not filt.empty:
        ed = filt["exp_min"].dropna().astype(int).clip(0,12).value_counts().sort_index().reset_index()
        ed.columns = ["Exp","Count"]
        
        fig8 = go.Figure(go.Bar(x=ed["Exp"], y=ed["Count"], marker=dict(color='#3B82F6')))
        
        L8 = fancy_layout(450)
        L8['title'] = "Experience Distribution"
        L8['xaxis'] = dict(
            title="Minimum Years of Experience", 
            dtick=1, 
            gridcolor='rgba(255,255,255,0.05)',
            showline=True, linewidth=1, linecolor='rgba(255,255,255,0.2)'
        )
        L8['yaxis'] = dict(
            title="Number of Roles Available", 
            gridcolor='rgba(255,255,255,0.05)',
            showline=True, linewidth=1, linecolor='rgba(255,255,255,0.2)'
        )
        
        fig8.update_layout(**L8)
        st.plotly_chart(fig8, use_container_width=True, config={'displayModeBar': False})

# ─── ADVANCED CORRELATION ANALYTICS ────────────────────────────────────────────
st.markdown('<div class="fancy-divider"></div><div class="section-title">🧬 <span>Multivariate Analysis</span></div>', unsafe_allow_html=True)

col7, col8 = st.columns(2)

with col7:
    # 1. SKILL VS ROLE HEATMAP
    if not filt.empty and 'skills_extracted' in filt.columns:
        s_df = filt.dropna(subset=['skills_extracted', 'role_category']).copy()
        s_df['skill_list'] = s_df['skills_extracted'].str.split(',')
        s_df = s_df.explode('skill_list')
        s_df['skill_list'] = s_df['skill_list'].str.strip().str.title()
        
        top_12_skills = s_df['skill_list'].value_counts().nlargest(12).index
        s_df_top = s_df[s_df['skill_list'].isin(top_12_skills)]
        
        pivot = pd.crosstab(s_df_top['role_category'], s_df_top['skill_list'])
        
        fig_hm = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=[[0, '#0F172A'], [0.5, '#3B82F6'], [1, '#00F0FF']], 
            hoverongaps=False,
            hovertemplate='<b>Role:</b> %{y}<br><b>Skill:</b> %{x}<br><b>Mentions:</b> %{z}<extra></extra>'
        ))
        L_hm = fancy_layout(450); L_hm['title'] = "Skill Dependency Matrix by Role"
        L_hm['xaxis'] = dict(tickangle=-45, gridcolor='rgba(255,255,255,0)')
        L_hm['yaxis'] = dict(gridcolor='rgba(255,255,255,0)')
        fig_hm.update_layout(**L_hm)
        st.plotly_chart(fig_hm, use_container_width=True, config={'displayModeBar': False})

with col8:
    # 2. SALARY SPREAD BY ROLE (BOX PLOT)
    if not filt.empty and 'salary_min_lpa' in filt.columns:
        sal_df = filt[(filt['salary_min_lpa'] > 0) & (filt['salary_min_lpa'] <= 50)].copy()
        
        fig_box = go.Figure()
        top_roles = sal_df['role_category'].value_counts().nlargest(6).index
        
        for idx, role in enumerate(top_roles):
            role_data = sal_df[sal_df['role_category'] == role]['salary_min_lpa']
            fig_box.add_trace(go.Box(
                y=role_data, 
                name=role,
                marker_color=COLORS[idx % len(COLORS)],
                boxpoints='outliers',
                hovertemplate='<b>%{x}</b><br>Salary: ₹%{y} LPA<extra></extra>'
            ))
            
        L_box = fancy_layout(450)
        L_box['title'] = "Realistic Salary Distribution (LPA)"
        L_box['yaxis_title'] = "Minimum Salary (LPA)"
        L_box['showlegend'] = False 
        fig_box.update_layout(**L_box)
        st.plotly_chart(fig_box, use_container_width=True, config={'displayModeBar': False})

# ─── PLATFORM BREAKDOWN ────────────────────────────────────────────────────────
st.markdown('<div class="section-title" style="margin-top: 20px;">🌐 <span>Platform Breakdown</span></div>', unsafe_allow_html=True)
try:
    conn2 = sqlite3.connect(DB_PATH)
    plat = pd.read_sql("""SELECT CASE
        WHEN job_url LIKE '%linkedin%' THEN 'LinkedIn'
        WHEN job_url LIKE '%naukri%' THEN 'Naukri'
        WHEN job_url LIKE '%internshala%' THEN 'Internshala'
        ELSE 'Other' END as platform, COUNT(*) as count FROM jobs GROUP BY platform""", conn2)
    conn2.close()
    
    pc = st.columns(max(len(plat), 1))
    for i, (_, row) in enumerate(plat.iterrows()):
        with pc[i]:
            st.markdown(f"""
            <div class="plat-card" style="border-top: 2px solid #00F0FF;">
                <div style='font-size:0.75rem; letter-spacing:0.1em; color:var(--text-muted); text-transform:uppercase;'>{row['platform']}</div>
                <div style='font-family:JetBrains Mono; font-size:1.8rem; font-weight:700; color:var(--cyan);'>{row['count']:,}</div>
                <div style='font-size:0.65rem; color:var(--text-muted)'>JOBS SCRAPED</div>
            </div>""", unsafe_allow_html=True)
except Exception as e:
    pass

# ─── LIVE DATA SCRAPER LOG ─────────────────────────────────────────────────────
st.markdown('<div class="fancy-divider"></div><div class="section-title">🔍 <span>Production Database Registry</span></div>', unsafe_allow_html=True)
if not filt.empty:
    search = st.text_input("", placeholder="Search job titles, companies, or tech stacks...", label_visibility="collapsed")
    latest = filt.sort_values("scrape_date", ascending=False).copy()
    if search:
        mask = (latest["job_title"].str.contains(search, case=False, na=False) |
                latest["company"].str.contains(search, case=False, na=False) |
                latest["skills_extracted"].str.contains(search, case=False, na=False))
        latest = latest[mask]
    
    show = [c for c in ["job_title","company","city_normalized","role_category","experience","skills_extracted","scrape_date"] if c in latest.columns]
    disp = latest[show].head(100)
    st.dataframe(disp, use_container_width=True, hide_index=True)
    
# ─── 7. CUSTOM FOOTER ──────────────────────────────────────────────────────────
st.markdown(f"""
<div style='margin-top: 40px; padding: 20px 0; border-top: 1px solid rgba(0, 240, 255, 0.2); display: flex; justify-content: space-between; align-items: center;'>
    <div style='font-family: "JetBrains Mono", monospace; font-size: 0.75rem; color: #94A3B8; letter-spacing: 1px; text-transform: uppercase;'>
        India Analytics & AI Job Market Pulse · <span style='color: #00F0FF;'>Built by Shariq Mukadam</span>
    </div>
    <div style='font-family: "JetBrains Mono", monospace; font-size: 0.75rem; color: #94A3B8; letter-spacing: 1px; text-transform: uppercase;'>
        {total:,} Jobs · {n_wks} Weeks · Naukri · LinkedIn · Internshala
    </div>
</div>
""", unsafe_allow_html=True)