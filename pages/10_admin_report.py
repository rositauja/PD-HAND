import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.database import (
    create_tables,
    get_connection,
    get_total_screenings_count,
    get_screening_results_summary,
    get_gender_distribution,
    get_dominant_hand_distribution,
    get_recent_screenings
)
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

create_tables()

st.set_page_config(
    page_title="Results Report — PD-HAND",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

go = st.query_params.get("go", None)

if go == "logout":
    st.session_state.clear()
    st.query_params.clear()
    st.switch_page("pages/7_admin_login.py")
    st.stop()

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

if not st.session_state.get("admin_authenticated"):
    st.switch_page("pages/7_admin_login.py")
    st.stop()

admin_id = st.session_state.get("admin_id", "")
admin_name = st.session_state.get("admin_name", "Admin")

go_page = st.query_params.get("go_page", None)

if go_page == "dashboard":
    st.query_params.clear()
    st.query_params["aid"] = str(admin_id)
    st.query_params["aname"] = admin_name
    st.switch_page("pages/8_admin_dashboard.py")
    st.stop()
elif go_page == "analytics":
    st.query_params.clear()
    st.query_params["aid"] = str(admin_id)
    st.query_params["aname"] = admin_name
    st.switch_page("pages/9_admin_analytics.py")
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

.header-actions {
    display:flex;
    gap:12px;
    justify-content:flex-end;
    margin-bottom:20px;
    margin-right:-230px;
}

.btn-export {
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding:10px 16px;
    border-radius:999px;
    font-size:14px;
    font-weight:600;
    text-decoration:none;
    transition:all 0.2s;
    border:1px solid #ddd;
    background:white;
    color:#333;
}

.btn-export:hover {
    border-color:#999;
    color:#555;
}

.btn-export.primary {
    background:var(--primary);
    color:white;
    border-color:var(--primary);
}

.btn-export.primary:hover {
    background:var(--primary-light);
    border-color:var(--primary-light);
}

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

/* DETAIL TABLE */
.detail-table {
    width:100%;
    border-collapse:collapse;
    border:1px solid #e8e8e8;
    border-radius:12px;
    overflow:hidden;
    font-size:13px;
}
.detail-table th {
    background:#f0f0f0;
    padding:14px 16px;
    text-align:left;
    font-size:11px;
    font-weight:700;
    color:#666;
    text-transform:uppercase;
    letter-spacing:0.5px;
    border-bottom:1px solid #e8e8e8;
}
.detail-table td {
    padding:12px 16px;
    border-bottom:1px solid #f0f0f0;
    color:#444;
    vertical-align:middle;
}
.detail-table tr:last-child td {
    border-bottom:none;
}
.detail-table tbody tr:hover {
    background:#fafafa;
}
.result-badge {
    display:inline-block;
    padding:6px 12px;
    border-radius:6px;
    font-size:12px;
    font-weight:600;
}
.result-positive { background:#fff3cd; color:#856404; }
.result-negative { background:#d1ecf1; color:#0c5460; }

/* FOOTER */
.footer { text-align:center; font-size:12px; color:white; font-weight:500; padding:16px 40px; background:var(--primary); }

</style>
""", unsafe_allow_html=True)

# ──── PREPARE EXPORT FILES ──────────────────────────────────────
total_screenings = get_total_screenings_count()
results = get_screening_results_summary()
positive_count = results.get("High Likelihood", 0)
negative_count = results.get("Low Likelihood", 0)

recent_data_export = get_recent_screenings(limit=500)

# CSV
export_df = pd.DataFrame(recent_data_export)
csv_data = export_df.to_csv(index=False).encode("utf-8")
csv_b64 = base64.b64encode(csv_data).decode()
csv_filename = f"pdhand_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# PDF
pdf_buffer = BytesIO()
doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
styles = getSampleStyleSheet()
story = [
    Paragraph("PD-HAND Results Report", styles["Title"]),
    Spacer(1, 12),
    Paragraph(f"Total Screenings: {total_screenings}", styles["Normal"]),
    Paragraph(f"Positive: {positive_count}", styles["Normal"]),
    Paragraph(f"Negative: {negative_count}", styles["Normal"]),
]
doc.build(story)
pdf_buffer.seek(0)

pdf_b64 = base64.b64encode(pdf_buffer.read()).decode()
pdf_filename = f"pdhand_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

# Calculate percentages
positive_pct = round((positive_count / total_screenings * 100), 1) if total_screenings > 0 else 0
negative_pct = round((negative_count / total_screenings * 100), 1) if total_screenings > 0 else 0

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
        <a class="nav-tab" href="?go_page=analytics&aid={admin_id}&aname={admin_name}" target="_self">📈 Analytics</a>
        <a class="nav-tab active" href="?go_page=report&aid={admin_id}&aname={admin_name}" target="_self">📑 Report</a>
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
    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;">
        <div class="page-header">
            <div class="page-title">Results Report</div>
            <div class="page-subtitle">Detailed anonymized breakdown of screening outcomes.</div>
        </div>
        <div class="header-actions">
            <a class="btn-export" href="data:text/csv;base64,{csv_b64}" download="{csv_filename}">📊 Export CSV</a>
            <a class="btn-export primary" href="data:application/pdf;base64,{pdf_b64}" download="{pdf_filename}">🔒 Export PDF</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ──── STAT CARDS (3 cards) ────────────────────────────────────
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Total Screenings</div>
        <div class="stat-value">{total_screenings:,}</div>
        <div class="stat-icon">📋</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Positive</div>
        <div class="stat-value">{positive_count:,}</div>
        <div class="stat-sub">{positive_pct}% rate</div>
        <div class="stat-icon">⚠️</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Negative</div>
        <div class="stat-value">{negative_count:,}</div>
        <div class="stat-sub">{negative_pct}% rate</div>
        <div class="stat-icon">✓</div>
    </div>
    """, unsafe_allow_html=True)

# ──── AGE GROUP & CUMULATIVE DETECTIONS (2 columns) ────────────────────────────────────
chart1, chart2 = st.columns(2, gap="large")

with chart1:
    st.markdown("""
    <div class="card">
        <div class="card-title">Results by Age Group</div>
        <div class="card-subtitle">Positive vs negative outcomes per age band.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get age group results from database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            CASE 
                WHEN age < 30 THEN '18-30'
                WHEN age < 40 THEN '30-40'
                WHEN age < 50 THEN '40-50'
                WHEN age < 60 THEN '50-60'
                ELSE '60+'
            END as age_group,
            label,
            COUNT(*) as count
        FROM screenings
        WHERE age IS NOT NULL
        GROUP BY age_group, label
        ORDER BY 
            CASE age_group
                WHEN '18-30' THEN 1
                WHEN '30-40' THEN 2
                WHEN '40-50' THEN 3
                WHEN '50-60' THEN 4
                WHEN '60+' THEN 5
            END
    """)
    age_results = cursor.fetchall()
    conn.close()
    
    if age_results:
        # Pivot data for stacked bar chart
        age_pivot = {}
        for age_group, label, count in age_results:
            if age_group not in age_pivot:
                age_pivot[age_group] = {'negative': 0, 'positive': 0}
            if label == "Low Likelihood":
                age_pivot[age_group]['negative'] = count
            else:
                age_pivot[age_group]['positive'] = count
        
        age_chart_df = pd.DataFrame([
            {'Age Group': k, 'negative': v['negative'], 'positive': v['positive']} 
            for k, v in age_pivot.items()
        ])
        # Dynamically create color list based on number of columns (excluding the index)
        num_cols = len(age_chart_df.columns) - 1  # -1 for the Age Group column
        colors = ['#66BB6A', '#2E7D32'][:num_cols] if num_cols > 0 else ['#2E7D32']
        st.bar_chart(age_chart_df.set_index('Age Group'), color=colors, height=250)
    else:
        st.info("No age group data available")

with chart2:
    st.markdown("""
    <div class="card">
        <div class="card-title">Cumulative Positive Detections</div>
        <div class="card-subtitle">Running total over the last 30 days.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get daily positive detections for last 30 days
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM screenings
        WHERE label = 'High Likelihood' 
        AND created_at >= datetime('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    """)
    daily_positive = cursor.fetchall()
    conn.close()
    
    if daily_positive:
        # Calculate cumulative sum
        cumulative_df = pd.DataFrame(daily_positive, columns=['Date', 'Count'])
        cumulative_df['Date'] = pd.to_datetime(cumulative_df['Date'])
        cumulative_df['Cumulative'] = cumulative_df['Count'].cumsum()
        cumulative_df = cumulative_df.set_index('Date')[['Cumulative']]
        st.line_chart(cumulative_df, color='#FF9500', height=250)
    else:
        st.info("No positive detection data available")

# ──── BREAKDOWN BY DEMOGRAPHICS (3 columns) ────────────────────────────────────
demo1, demo2, demo3 = st.columns(3, gap="large")

with demo1:
    st.markdown("""
    <div class="card">
        <div class="card-title">By Gender</div>
        <div class="card-subtitle">Positive vs negative outcomes by gender.</div>
    </div>
    """, unsafe_allow_html=True)
    
    gender_data = get_gender_distribution()
    if gender_data:
        # Create stacked bar chart data
        gender_df = pd.DataFrame(gender_data)
        # Dynamically create color list based on number of columns (excluding the index)
        num_cols = len(gender_df.columns) - 1  # -1 for the Gender column
        colors = ['#66BB6A', '#2E7D32'][:num_cols] if num_cols > 0 else ['#2E7D32']
        st.bar_chart(gender_df.set_index('Gender'), color=colors, height=250)
    else:
        st.info("No gender data available")

with demo2:
    st.markdown("""
    <div class="card">
        <div class="card-title">By Dominant Hand</div>
        <div class="card-subtitle">Results breakdown by handedness.</div>
    </div>
    """, unsafe_allow_html=True)
    
    hand_data = get_dominant_hand_distribution()
    if hand_data:
        hand_df = pd.DataFrame(hand_data)
        # Dynamically create color list based on number of columns (excluding the index)
        num_cols = len(hand_df.columns) - 1  # -1 for the Hand column
        colors = ['#66BB6A', '#2E7D32'][:num_cols] if num_cols > 0 else ['#2E7D32']
        st.bar_chart(hand_df.set_index('Hand'), color=colors, height=250)
    else:
        st.info("No hand data available")

with demo3:
    st.markdown("""
    <div class="card">
        <div class="card-title">By Pattern</div>
        <div class="card-subtitle">Distribution of pattern types detected.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Get pattern distribution from database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT detected_type, COUNT(*) as count
        FROM screenings
        GROUP BY detected_type
        ORDER BY count DESC
    """)
    pattern_rows = cursor.fetchall()
    conn.close()
    
    if pattern_rows:
        pattern_df = pd.DataFrame(pattern_rows, columns=['Pattern', 'Count'])
        # Single column, so use single color
        st.bar_chart(pattern_df.set_index('Pattern'), color=['#2E7D32'], height=250)
    else:
        st.info("No pattern data available")

# ──── DETAILED SCREENING RECORDS ────────────────────────────────────
table_col = st.columns([1])[0]

with table_col:
    st.markdown("""
    <div class="card">
        <div class="card-title">Detailed Screening Records</div>
        <div class="card-subtitle">Most recent screenings — anonymized.</div>
    </div>
    """, unsafe_allow_html=True)

    recent_data = get_recent_screenings(limit=50)

    if recent_data:
        # Create table HTML
        table_html = """<table class="detail-table">
        <thead>
            <tr>
                <th>Screening ID</th>
                <th>Date</th>
                <th>Result</th>
                <th>Age</th>
                <th>Hand</th>
                <th>Pattern</th>
            </tr>
        </thead>
        <tbody>
        """
        
        for item in recent_data:
            result_class = "result-positive" if item['result'] == "High Likelihood" else "result-negative"
            result_label = "Positive" if item['result'] == "High Likelihood" else "Negative"
            
            try:
                date_obj = pd.to_datetime(item['date'])
                formatted_date = date_obj.strftime("%d %b %Y, %H:%M")
            except:
                formatted_date = item['date']
            
            age = str(item.get('age', '')) if item.get('age') else '—'
            hand = str(item.get('hand', '')) if item.get('hand') else '—'
            pattern = str(item.get('pattern', '')) if item.get('pattern') else '—'
            screening_id = f"SCR-{item.get('date', '').split()[0].replace('-', '')}" if item.get('date') else "—"
            
            table_html += f"""<tr>
                <td>{screening_id}</td>
                <td>{formatted_date}</td>
                <td><span class="result-badge {result_class}">● {result_label}</span></td>
                <td>{age}</td>
                <td>{hand}</td>
                <td>{pattern}</td>
            </tr>
            """
        
        table_html += """</tbody></table>"""
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("No screening records available")

# Footer
st.markdown("""
<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>
""", unsafe_allow_html=True)