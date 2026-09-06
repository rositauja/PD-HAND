import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.database import (
    create_tables,
    get_connection,
    get_total_users_count,
    get_active_users_this_month,
    get_screenings_last_30_days,
    get_new_users_last_7_days,
    get_gender_distribution,
    get_dominant_hand_distribution,
    get_age_distribution
)
import pandas as pd
from datetime import datetime, timedelta

create_tables()

st.set_page_config(
    page_title="Admin Analytics — PD-HAND",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH — Same pattern as Home.py:
# 1. Handle logout FIRST
# 2. Restore session from query params if needed (before auth check)
# 3. Require auth
# 4. Then handle navigation
# ═══════════════════════════════════════════════════════════════════════════════

# ── Step 1: Handle logout FIRST ───────────────────────────────────────────
go = st.query_params.get("go", None)

if go == "logout":
    st.session_state.clear()
    st.query_params.clear()
    st.switch_page("pages/7_admin_login.py")
    st.stop()

# ── Step 2: Restore session from query params if session was wiped ────────────
aid = st.query_params.get("aid", None)
aname = st.query_params.get("aname", None)

if aid and aname and not st.session_state.get("admin_authenticated"):
    try:
        st.session_state["admin_authenticated"] = True
        st.session_state["admin_id"] = int(aid)
        st.session_state["admin_name"] = str(aname)
    except (ValueError, TypeError):
        st.switch_page("pages/7_admin_login.py")
        st.stop()

# ── Step 3: Require authentication ────────────────────────────────────────────
if not st.session_state.get("admin_authenticated"):
    st.switch_page("pages/7_admin_login.py")
    st.stop()

# ── Step 4: Get admin info from session ──────────────────────────────────────────
admin_id = st.session_state.get("admin_id", "")
admin_name = st.session_state.get("admin_name", "Admin")

# ── Step 5: Handle navbar page navigation ───────────────────────────────────────
# Only navigate if a different page was explicitly requested
go_page = st.query_params.get("go_page", None)

if go_page == "dashboard":
    st.query_params.clear()
    st.query_params["aid"] = str(admin_id)
    st.query_params["aname"] = admin_name
    st.switch_page("pages/8_admin_dashboard.py")
    st.stop()
elif go_page == "report":
    st.query_params.clear()
    st.query_params["aid"] = str(admin_id)
    st.query_params["aname"] = admin_name
    st.switch_page("pages/10_admin_report.py")
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

[data-testid="stSidebar"]        { display: none; }
[data-testid="collapsedControl"] { display: none; }
[data-testid="stToolbar"]        { display: none; }
[data-testid="stDecoration"]     { display: none; }
[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}
header { display: none !important; }
footer { display: none !important; }

:root {
    --primary: #2E7D32;
    --primary-light: #43A047;
    --primary-glow: #66BB6A;
    --border-light: #c8e6c9;
    --text-dark: #1b5e20;
    --text-muted: #2e6b3e;
    --bg-light: #f5f5f5;
}

@keyframes heartbeat {
    0%,100%{transform:scale(1)} 15%{transform:scale(1.18)}
    30%{transform:scale(1)} 45%{transform:scale(1.10)} 60%{transform:scale(1)}
}
@keyframes pulse-ring {
    0%{transform:scale(0.85);opacity:0.6} 100%{transform:scale(2.0);opacity:0}
}

/* NAVBAR */
.navbar {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:16px 40px;
    margin:0 0 24px 0;
    border-bottom:1px solid var(--border-light);
    background:rgba(255,255,255,0.97);
    position:sticky;
    top:0;
    z-index:100;
}

.nav-logo {
    display:flex;
    align-items:center;
    gap:12px;
}

.logo-icon-wrap {
    position:relative;
    width:44px;
    height:44px;
}

.logo-pulse-ring {
    position:absolute;
    inset:0;
    border-radius:50%;
    background:var(--primary-glow);
    opacity:0.5;
    animation:pulse-ring 2s ease-out infinite;
}

.logo-icon {
    position:relative;
    width:44px;
    height:44px;
    background:linear-gradient(135deg,var(--primary),var(--primary-light));
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
    animation:heartbeat 1.8s ease-in-out infinite;
    box-shadow:0 4px 16px rgba(46,125,50,0.35);
    z-index:1;
}

.logo-name { font-size:17px; font-weight:800; color:#1b5e20; letter-spacing:-0.3px; }
.logo-sub { font-size:10px; font-weight:500; color:#2e6b3e; letter-spacing:0.5px; }
.logo-badge { font-size:10px; font-weight:700; color:white; background:var(--primary); padding:4px 10px; border-radius:999px; margin-left:6px; }

.nav-tabs {
    display:flex;
    gap:28px;
    align-items:center;
}

.nav-tab {
    padding:6px 4px;
    font-size:14px;
    font-weight:500;
    color:#555;
    text-decoration:none !important;
    display:flex;
    align-items:center;
    gap:5px;
    transition:color 0.2s;
    cursor:pointer;
    border:none !important;
}

.nav-tab:hover { color:var(--primary); }
.nav-tab.active { color:var(--primary); font-weight:600; }

.nav-right {
    display:flex;
    align-items:center;
    gap:14px;
}

.admin-info {
    display:flex;
    align-items:center;
    gap:12px;
}

.avatar {
    width:40px;
    height:40px;
    background:linear-gradient(135deg,var(--primary),var(--primary-light));
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:700;
    color:white;
    font-size:16px;
    box-shadow:0 2px 8px rgba(46,125,50,0.3);
    flex-shrink:0;
}

.admin-text {
    font-size:13px;
    display:flex;
    flex-direction:column;
    gap:2px;
}

.admin-name {
    font-weight:700;
    color:#1a1a1a;
}

.admin-role {
    font-size:11px;
    color:#999;
}

.logout-btn {
    font-size:14px;
    font-weight:500;
    color:#333;
    background:white;
    border:1px solid #ddd;
    border-radius:999px;
    padding:7px 14px;
    text-decoration:none;
    transition:all 0.2s;
}

.logout-btn:hover { color:var(--primary); border-color:var(--primary); }

/* MAIN CONTENT */
.main-container {
    padding-top: 20px;
}

.content-wrapper {
    max-width: 1000px;
    margin: 0 auto;
    padding-left: 40px;
    padding-right: 40px;
}

.page-header { margin-bottom:20px; margin-left:-230px;}
.page-title { font-size:32px; font-weight:800; color:#1a1a1a; margin-bottom:8px; }
.page-subtitle { font-size:14px; color:#666; font-weight:500; }

/* STAT CARDS */
.stat-card {
    background:white;
    border:1px solid #e8e8e8;
    border-radius:18px;
    padding:24px;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
    transition:all 0.3s ease;
    position:relative;
    overflow:hidden;
}
.stat-card:hover {
    box-shadow:0 6px 16px rgba(0,0,0,0.1);
    border-color:#d8d8d8;
    transform:translateY(-2px);
}
.stat-label { font-size:11px; font-weight:700; color:#999; text-transform:uppercase; letter-spacing:0.6px; margin-bottom:12px; }
.stat-value { font-size:26px; font-weight:800; color:#1a1a1a; margin-bottom:6px; line-height:1; }
.stat-sub { font-size:13px; color:#888; font-weight:500; }
.stat-icon { position:absolute; top:20px; right:22px; font-size:32px; opacity:0.25; }

div[data-testid="stHorizontalBlock"] {
    gap: 22px !important;
    margin-bottom: 22px;
    margin-left: 60px !important;
    margin-right: 60px !important;
}

div[data-testid="column"] {
    min-width: 0 !important;
}

/* CHART & TABLE CARDS */
.card {
    background:white;
    border:1px solid #e8e8e8;
    border-radius:18px;
    padding:24px;
    box-shadow:0 1px 4px rgba(0,0,0,0.05);
    transition:all 0.3s ease;
}
.card:hover {
    box-shadow:0 6px 16px rgba(0,0,0,0.1);
    border-color:#d8d8d8;
}
.card-title { font-size:16px; font-weight:700; color:#1a1a1a; margin-bottom:6px; }
.card-subtitle { font-size:13px; color:#888; margin-bottom:18px; font-weight:500; }

/* FOOTER */
.footer { text-align:center; font-size:12px; color:white; font-weight:500; padding:16px 40px; background:var(--primary); }

</style>
""", unsafe_allow_html=True)

# Navbar with f-string for variable interpolation
st.markdown(f"""
<!-- NAVBAR -->
<div class="navbar">
    <div class="nav-logo">
        <div class="logo-icon-wrap">
            <div class="logo-pulse-ring"></div>
            <div class="logo-icon">👋</div>
        </div>
        <div>
            <div style="display:flex; align-items:center; gap:6px;">
                <div class="logo-name">PD-HAND</div>
                <div class="logo-badge">ADMIN</div>
            </div>
            <div class="logo-sub">FCSIT · UNIMAS</div>
        </div>
    </div>
    <div class="nav-tabs">
        <a class="nav-tab" href="?go_page=dashboard&aid={admin_id}&aname={admin_name}" target="_self">📊 Dashboard</a>
        <a class="nav-tab active" href="?go_page=analytics&aid={admin_id}&aname={admin_name}" target="_self">📈 Analytics</a>
        <a class="nav-tab" href="?go_page=report&aid={admin_id}&aname={admin_name}" target="_self">📑 Report</a>
    </div>
    <div class="nav-right">
        <div class="admin-info">
            <div class="avatar">AD</div>
            <div class="admin-text">
                <div class="admin-name">Admin</div>
                <div class="admin-role">Administrator</div>
            </div>
        </div>
        <a class="logout-btn" href="?go=logout" target="_self">→ Log out</a>
    </div>
</div>

<!-- MAIN CONTENT -->
<div class="content-wrapper">

<div class="main-container">
    <div class="page-header">
        <div class="page-title">User Analytics</div>
        <div class="page-subtitle">Anonymized demographic breakdowns and platform growth trends.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ──── GET REAL DATA FROM DATABASE ──────────────────────────────────────
total_users = get_total_users_count()
active_users = get_active_users_this_month()

# Calculate new users this month (not last 7 days)
conn = get_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT COUNT(*) as count
    FROM users
    WHERE created_at >= datetime('now', 'start of month')
""")
new_this_month = cursor.fetchone()[0]
conn.close()

# Calculate metrics
active_pct = round((active_users / total_users * 100), 1) if total_users > 0 else 0

# ──── STAT CARDS (3 cards in 1 row) ────────────────────────────────────
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">New This Month</div>
        <div class="stat-value">{new_this_month:,}</div>
        <div class="stat-sub">New registrations</div>
        <div class="stat-icon">👥</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Active This Month</div>
        <div class="stat-value">{active_users:,}</div>
        <div class="stat-sub">{active_pct}% of total users</div>
        <div class="stat-icon">📊</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Total Users</div>
        <div class="stat-value">{total_users:,}</div>
        <div class="stat-sub">All-time registrations</div>
        <div class="stat-icon">👥</div>
    </div>
    """, unsafe_allow_html=True)

# ──── PIE CHARTS & BAR CHART ROW ────────────────────────────────────
pie1, pie2, bar = st.columns(3, gap="large")

with pie1:
    st.markdown("""
    <div class="card">
        <div class="card-title">Gender Distribution</div>
        <div class="card-subtitle">Self-reported by users.</div>
    </div>
    """, unsafe_allow_html=True)
    
    gender_data_list = get_gender_distribution()
    if gender_data_list:
        gender_data = pd.DataFrame(gender_data_list)
        gender_chart = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": gender_data.to_dict('records')},
            "mark": {"type": "arc", "innerRadius": 0},
            "encoding": {
                "theta": {"field": "Count", "type": "quantitative"},
                "color": {"field": "Gender", "type": "nominal", "scale": {"scheme": "greens"}},
                "tooltip": [{"field": "Gender", "type": "nominal"}, {"field": "Count", "type": "quantitative"}]
            }
        }
        st.vega_lite_chart(gender_chart, use_container_width=True)
    else:
        st.info("No gender data available")

with pie2:
    st.markdown("""
    <div class="card">
        <div class="card-title">Dominant Hand</div>
        <div class="card-subtitle">User-reported handedness.</div>
    </div>
    """, unsafe_allow_html=True)
    
    hand_data_list = get_dominant_hand_distribution()
    if hand_data_list:
        hand_data = pd.DataFrame(hand_data_list)
        hand_chart = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "data": {"values": hand_data.to_dict('records')},
            "mark": {"type": "arc", "innerRadius": 0},
            "encoding": {
                "theta": {"field": "Count", "type": "quantitative"},
                "color": {"field": "Hand", "type": "nominal", "scale": {"scheme": "greens"}},
                "tooltip": [{"field": "Hand", "type": "nominal"}, {"field": "Count", "type": "quantitative"}]
            }
        }
        st.vega_lite_chart(hand_chart, use_container_width=True)
    else:
        st.info("No hand data available")

with bar:
    st.markdown("""
    <div class="card">
        <div class="card-title">Age Groups</div>
        <div class="card-subtitle">Distribution across age bands.</div>
    </div>
    """, unsafe_allow_html=True)
    
    age_data_list = get_age_distribution()
    if age_data_list:
        age_data = pd.DataFrame(age_data_list)
        st.bar_chart(age_data.set_index('Age'), color='#2E7D32', height=250)
    else:
        st.info("No age data available")

# ──── TREND CHARTS ROW ────────────────────────────────────────────────
trend1, trend2 = st.columns(2, gap="large")

with trend1:
    st.markdown("""
    <div class="card">
        <div class="card-title">New Users — Last 30 Days</div>
        <div class="card-subtitle">Daily sign-ups over the past month.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get real data from database
    screenings_30days = get_screenings_last_30_days()
    if screenings_30days:
        new_users_data = pd.DataFrame(screenings_30days, columns=['Date', 'New Users'])
        new_users_data['Date'] = pd.to_datetime(new_users_data['Date'])
        new_users_data = new_users_data.set_index('Date')
        st.line_chart(new_users_data, color='#2E7D32', height=300)
    else:
        st.info("No data available for the last 30 days")

with trend2:
    st.markdown("""
    <div class="card">
        <div class="card-title">Active Users — Last 30 Days</div>
        <div class="card-subtitle">Daily active users over the past month.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get real data from database
    screenings_30days = get_screenings_last_30_days()
    if screenings_30days:
        active_users_data = pd.DataFrame(screenings_30days, columns=['Date', 'Active Users'])
        active_users_data['Date'] = pd.to_datetime(active_users_data['Date'])
        active_users_data = active_users_data.set_index('Date')
        st.line_chart(active_users_data, color='#FF9500', height=300)
    else:
        st.info("No data available for the last 30 days")

st.markdown("""
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>
""", unsafe_allow_html=True)