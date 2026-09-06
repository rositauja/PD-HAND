# pages/7_admin_landing.py — Admin landing page
import streamlit as st

st.set_page_config(
    page_title="PD-HAND Admin | Anonymized Analytics",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Handle navigation via query params 
go = st.query_params.get("go", None)

if go == "admin_login":
    st.switch_page("pages/7_admin_login.py")
    st.stop()

# Check if already authenticated as admin
if st.session_state.get("admin_authenticated"):
    st.switch_page("pages/8_admin_dashboard.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

[data-testid="stSidebar"]        { display: none; }
[data-testid="collapsedControl"] { display: none; }
[data-testid="stToolbar"]        { display: none; }
[data-testid="stDecoration"]     { display: none; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; max-width: 100% !important; }
header { display: none !important; }
footer { display: none !important; }

:root {
    --primary:       #2E7D32;
    --primary-light: #43A047;
    --primary-glow:  #66BB6A;
    --bg-hero-start: #f0faf3;
    --bg-hero-mid:   #d4edda;
    --bg-hero-end:   #c8e6c9;
    --text-dark:     #1b5e20;
    --text-muted:    #2e6b3e;
    --border-light:  #c8e6c9;
}
@keyframes heartbeat {
    0%,100%{transform:scale(1)} 15%{transform:scale(1.18)}
    30%{transform:scale(1)} 45%{transform:scale(1.10)} 60%{transform:scale(1)}
}
@keyframes pulse-ring {
    0%{transform:scale(0.85);opacity:0.6} 100%{transform:scale(2.0);opacity:0}
}
@keyframes fade-up {
    0%{opacity:0;transform:translateY(22px)} 100%{opacity:1;transform:translateY(0)}
}
@keyframes float-slow {
    0%,100%{transform:translateY(0) translateX(0)} 50%{transform:translateY(-22px) translateX(12px)}
}
@keyframes float-slower {
    0%,100%{transform:translateY(0) translateX(0)} 50%{transform:translateY(16px) translateX(-16px)}
}

/* NAVBAR */
.navbar {
    display:flex; justify-content:space-between; align-items:center;
    padding:16px 48px; border-bottom:1px solid var(--border-light);
    background:rgba(255,255,255,0.97); position:sticky; top:0; z-index:100;
}
.nav-logo { display:flex; align-items:center; gap:12px; }
.logo-icon-wrap { position:relative; width:44px; height:44px; display:flex; align-items:center; justify-content:center; }
.logo-pulse-ring { position:absolute; inset:0; border-radius:50%; background:var(--primary-glow); opacity:0.5; animation:pulse-ring 2s ease-out infinite; }
.logo-icon { position:relative; width:44px; height:44px; background:linear-gradient(135deg,var(--primary),var(--primary-light)); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:20px; animation:heartbeat 1.8s ease-in-out infinite; box-shadow:0 4px 16px rgba(46,125,50,0.35); z-index:1; }
.logo-name { font-size:17px; font-weight:800; color:var(--text-dark); letter-spacing:-0.3px; }
.logo-sub  { font-size:10px; font-weight:500; color:var(--text-muted); letter-spacing:0.5px; }
.logo-badge { font-size:11px; font-weight:700; letter-spacing:0.5px; color:white; background:var(--primary); padding:4px 10px; border-radius:999px; margin-left:12px; }

/* HERO */
.hero {
    background:linear-gradient(135deg,var(--bg-hero-start) 0%,var(--bg-hero-mid) 50%,var(--bg-hero-end) 100%);
    padding:80px 48px 48px; text-align:center; position:relative;
    overflow:visible; display:flex; flex-direction:column; align-items:center; justify-content:center;
}
.hero-orb { position:absolute; border-radius:50%; background:radial-gradient(circle,rgba(102,187,106,0.22),transparent 70%); pointer-events:none; z-index:1; }
.hero-orb-1 { width:320px; height:320px; top:-100px; left:-80px; animation:float-slow 14s ease-in-out infinite; }
.hero-orb-2 { width:220px; height:220px; bottom:-50px; right:-50px; animation:float-slower 18s ease-in-out infinite; }
.hero-badge { display:inline-flex; align-items:center; gap:6px; background:rgba(255,255,255,0.78); border:1px solid var(--border-light); border-radius:999px; padding:7px 18px; font-size:13.5px; font-weight:600; color:var(--text-muted); margin-bottom:28px; animation:fade-up 0.6s ease-out both; position:relative; z-index:2; }
.hero-title { font-size:clamp(36px,5vw,56px); font-weight:800; color:#1a1a1a; line-height:1.15; margin-bottom:20px; animation:fade-up 0.7s ease-out 0.1s both; position:relative; z-index:2; }
.hero-title-green { background:linear-gradient(135deg,var(--primary),var(--primary-glow)); -webkit-background-clip:text; background-clip:text; color:transparent; }
.hero-subtitle { font-size:17px; color:#3a3a3a; line-height:1.75; font-weight:500; max-width:560px; margin:0 auto 24px; animation:fade-up 0.7s ease-out 0.2s both; position:relative; z-index:2; }
.hero-buttons { display:flex; flex-direction:row; align-items:center; justify-content:center; gap:16px; margin-bottom:36px; position:relative; z-index:2; animation:fade-up 0.7s ease-out 0.3s both; }
.btn-primary { background:linear-gradient(135deg,var(--primary),var(--primary-light)); color:white !important; padding:14px 30px; border-radius:999px; font-size:16px; font-weight:600; text-decoration:none !important; display:inline-flex; align-items:center; justify-content:center; gap:8px; box-shadow:0 4px 20px rgba(46,125,50,0.35); transition:transform 0.2s, box-shadow 0.2s; }
.btn-primary:hover { transform:translateY(-2px); box-shadow:0 8px 28px rgba(46,125,50,0.45); }
.trust-bar { display:flex; justify-content:center; gap:28px; margin-bottom:32px; position:relative; z-index:2; }
.trust-item { display:flex; align-items:center; gap:6px; font-size:14px; color:var(--text-muted); font-weight:600; }

/* HOW IT WORKS */
.how-section { padding:64px 48px 48px; text-align:center; background:white; position:relative; z-index:3; }
.process-label { font-size:12px; font-weight:700; letter-spacing:2.5px; color:var(--primary); text-transform:uppercase; margin-bottom:10px; }
.how-title { font-size:38px; font-weight:800; color:#1a1a1a; margin-bottom:10px; }
.how-sub   { font-size:15px; color:#444; margin-bottom:44px; font-weight:500; }
.cards-row { display:grid; grid-template-columns:repeat(3,1fr); gap:22px; max-width:860px; margin:0 auto 40px; }
.step-card { background:white; border:1px solid #eee; border-radius:20px; padding:28px 22px; text-align:left; box-shadow:0 4px 24px -8px rgba(46,125,50,0.09); transition:transform 0.25s,box-shadow 0.25s; position:relative; overflow:hidden; cursor:default; }
.step-card:hover { transform:translateY(-6px); box-shadow:0 14px 40px -8px rgba(46,125,50,0.18); }
.step-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,var(--primary),var(--primary-glow)); opacity:0; transition:opacity 0.25s; }
.step-card:hover::before { opacity:1; }
.step-num { position:absolute; top:18px; right:18px; font-size:38px; font-weight:800; color:#c8c8c8; line-height:1; }
.step-icon-wrap { width:50px; height:50px; background:linear-gradient(135deg,var(--primary),var(--primary-light)); border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:22px; margin-bottom:18px; box-shadow:0 4px 14px rgba(46,125,50,0.28); }
.step-title { font-size:17px; font-weight:700; color:#1a1a1a; margin-bottom:8px; }
.step-desc  { font-size:14px; color:#444; line-height:1.65; }
.footer { text-align:center; font-size:13px; color:white; font-weight:500; padding:20px 48px 32px; background:#2E7D32; }
</style>

<!-- NAVBAR -->
<div class="navbar">
    <div class="nav-logo">
        <div class="logo-icon-wrap"><div class="logo-pulse-ring"></div><div class="logo-icon">&#x270B;</div></div>
        <div>
            <div style="display:flex; align-items:center; gap:8px;">
                <div class="logo-name">PD-HAND</div>
                <div class="logo-badge">ADMIN</div>
            </div>
            <div class="logo-sub">FCSIT &middot; UNIMAS</div>
        </div>
    </div>
</div>

<!-- HERO -->
<div class="hero">
    <div class="hero-orb hero-orb-1"></div>
    <div class="hero-orb hero-orb-2"></div>
    <div class="hero-badge">&#128179; Anonymized analytics portal</div>
    <div class="hero-title">Screening <span class="hero-title-green">Analytics<br>& Insights</span><br>For Administrators</div>
    <div class="hero-subtitle">Access aggregated health statistics and screening trends. View anonymized demographic data, results breakdowns, and growth metrics. No personal data is exposed.</div>
    <div class="hero-buttons">
        <a class="btn-primary" href="?go=admin_login" target="_self">Admin Login &#8594;</a>
    </div>
    <div class="trust-bar">
        <div class="trust-item">&#128274; Privacy-Focused</div>
        <div class="trust-item">&#128202; Data-Driven</div>
    </div>
</div>

<div class="how-section">
    <div class="process-label">FEATURES</div>
    <div class="how-title">Admin Portal Capabilities</div>
    <div class="how-sub">Comprehensive tools for monitoring system health and screening trends.</div>
    <div class="cards-row">
        <div class="step-card">
            <div class="step-num">01</div>
            <div class="step-icon-wrap">📊</div>
            <div class="step-title">Dashboard</div>
            <div class="step-desc">Real-time statistics, screening counts, user growth, and recent activity overview at a glance.</div>
        </div>
        <div class="step-card">
            <div class="step-num">02</div>
            <div class="step-icon-wrap">📈</div>
            <div class="step-title">User Analytics</div>
            <div class="step-desc">Demographic breakdowns by age, gender, and dominant hand. Visualize user growth trends over time.</div>
        </div>
        <div class="step-card">
            <div class="step-num">03</div>
            <div class="step-icon-wrap">📑</div>
            <div class="step-title">Results Report</div>
            <div class="step-desc">Comprehensive screening results breakdown by demographics. Export data to PDF or CSV for external analysis.</div>
        </div>
    </div>
</div>
<div class="footer">For administrative use only. Data is anonymized and compliant with privacy regulations.</div>
""", unsafe_allow_html=True)