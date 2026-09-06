import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.auth import restore_session, require_auth

st.set_page_config(page_title="PD-HAND | Parkinson's Early Detection", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
# AUTH — The key insight:
# /Home?go=screening is a RERUN of pages/3_Home.py, NOT a new session.
# st.session_state persists across reruns within the same browser tab.
# So session_state["authenticated"] will still be True after clicking a link
# that stays on /Home — it only gets wiped if the tab is closed/refreshed.
#
# The only remaining issue: Streamlit sometimes starts a NEW WebSocket
# connection on certain navigation events, which does wipe session_state.
# Solution: we use st.query_params to pass user info alongside ?go=,
# so we can restore the session even if it gets wiped.
# ══════════════════════════════════════════════════════════════════════════════

# ── Step 1: Handle navigation FIRST ───────────────────────────────────────────
go = st.query_params.get("go", None)

if go == "logout":
    st.session_state.clear()
    st.query_params.clear()
    st.switch_page("app.py")
    st.stop()

if go == "edit_profile":
    require_auth()
    user_id = st.session_state.get("user_id", "")
    user_name = st.session_state.get("user_name", "User")
    user_phone = st.session_state.get("user_phone", "")
    st.query_params["uid"] = str(user_id)
    st.query_params["uname"] = user_name
    st.query_params["phone"] = user_phone
    st.switch_page("pages/16_Edit_Profile.py")
    st.stop()

# ── Step 2: Require authentication ────────────────────────────────────────────
require_auth()

# ── Step 3: Get user info from session ──────────────────────────────────────────
user_id   = st.session_state.get("user_id", "")
user_name = st.session_state.get("user_name", "User")
user_phone = st.session_state.get("user_phone", "")
initials  = "".join([w[0].upper() for w in user_name.split()[:2]])

# Handle page navigation after user info exists
if go == "screening":
    st.query_params["uid"] = str(user_id)
    st.query_params["uname"] = user_name
    st.switch_page("pages/4_Screening.py")
    st.stop()
if go == "history":
    st.query_params["uid"] = str(user_id)
    st.query_params["uname"] = user_name
    st.switch_page("pages/5_History.py")
    st.stop()

from core.auth import get_auth_qs

auth = get_auth_qs()

# ── Page HTML ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* {{ font-family: 'Inter', sans-serif !important; box-sizing: border-box; }}
[data-testid="stSidebar"]        {{ display: none; }}
[data-testid="collapsedControl"] {{ display: none; }}
[data-testid="stToolbar"]        {{ display: none; }}
[data-testid="stDecoration"]     {{ display: none; }}
[data-testid="stMainBlockContainer"] {{ padding: 0 !important; max-width: 100% !important; }}
header {{ display: none !important; }}
footer {{ display: none !important; }}
:root {{
    --primary: #2E7D32; --primary-light: #43A047; --primary-glow: #66BB6A;
    --bg-hero-start: #f0faf3; --bg-hero-mid: #d4edda; --bg-hero-end: #c8e6c9;
    --text-dark: #1b5e20; --text-muted: #2e6b3e; --border-light: #c8e6c9;
}}
@keyframes heartbeat {{ 0%,100%{{transform:scale(1)}} 15%{{transform:scale(1.18)}} 30%{{transform:scale(1)}} 45%{{transform:scale(1.10)}} 60%{{transform:scale(1)}} }}
@keyframes pulse-ring {{ 0%{{transform:scale(0.85);opacity:0.6}} 100%{{transform:scale(2.0);opacity:0}} }}
@keyframes ecg {{ 0%{{stroke-dashoffset:1200}} 100%{{stroke-dashoffset:0}} }}
@keyframes fade-up {{ 0%{{opacity:0;transform:translateY(22px)}} 100%{{opacity:1;transform:translateY(0)}} }}
@keyframes float-slow {{ 0%,100%{{transform:translateY(0) translateX(0)}} 50%{{transform:translateY(-22px) translateX(12px)}} }}
@keyframes float-slower {{ 0%,100%{{transform:translateY(0) translateX(0)}} 50%{{transform:translateY(16px) translateX(-16px)}} }}

.navbar {{ display:flex; justify-content:space-between; align-items:center; padding:16px 48px; border-bottom:1px solid var(--border-light); background:rgba(255,255,255,0.97); position:sticky; top:0; z-index:100; }}
.nav-logo {{ display:flex; align-items:center; gap:12px; }}
.logo-icon-wrap {{ position:relative; width:44px; height:44px; display:flex; align-items:center; justify-content:center; }}
.logo-pulse-ring {{ position:absolute; inset:0; border-radius:50%; background:var(--primary-glow); opacity:0.5; animation:pulse-ring 2s ease-out infinite; }}
.logo-icon {{ position:relative; width:44px; height:44px; background:linear-gradient(135deg,var(--primary),var(--primary-light)); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:20px; animation:heartbeat 1.8s ease-in-out infinite; box-shadow:0 4px 16px rgba(46,125,50,0.35); z-index:1; }}
.logo-name {{ font-size:17px; font-weight:800; color:var(--text-dark); letter-spacing:-0.3px; }}
.logo-sub  {{ font-size:10px; font-weight:500; color:var(--text-muted); letter-spacing:0.5px; }}
.nav-links {{ display:flex; gap:28px; align-items:center; }}
.nav-right {{ display:flex; align-items:center; gap:14px; }}
.nav-link-btn {{ font-size:14px; font-weight:500; color:#555; text-decoration:none; padding:6px 4px; display:flex; align-items:center; gap:5px; transition:color 0.2s; }}
.nav-link-btn:hover {{ color:var(--primary); }}
.nav-link-btn.active {{ color:var(--primary); font-weight:600; }}
.user-avatar {{ width:38px; height:38px; border-radius:50%; background:linear-gradient(135deg,var(--primary),var(--primary-light)); color:white; font-size:14px; font-weight:700; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 8px rgba(46,125,50,0.3); transition: transform 0.2s, box-shadow 0.2s; }}
.user-avatar:hover {{ transform: scale(1.08); box-shadow: 0 4px 12px rgba(46,125,50,0.4); }}
.logout-btn {{ display:flex; align-items:center; gap:6px; font-size:14px; font-weight:500; color:#333; background:white; border:1px solid #ddd; border-radius:999px; padding:7px 14px; text-decoration:none; transition:all 0.2s; }}
.logout-btn:hover {{ color:var(--primary); border-color:var(--primary); }}

.hero {{ background:linear-gradient(135deg,var(--bg-hero-start) 0%,var(--bg-hero-mid) 50%,var(--bg-hero-end) 100%); padding:80px 48px 64px; text-align:center; position:relative; overflow:hidden; display:flex; flex-direction:column; align-items:center; justify-content:center; }}
.hero-orb {{ position:absolute; border-radius:50%; background:radial-gradient(circle,rgba(102,187,106,0.22),transparent 70%); pointer-events:none; }}
.hero-orb-1 {{ width:320px; height:320px; top:-100px; left:-80px; animation:float-slow 14s ease-in-out infinite; }}
.hero-orb-2 {{ width:220px; height:220px; bottom:-50px; right:-50px; animation:float-slower 18s ease-in-out infinite; }}
.hero-badge {{ display:inline-flex; align-items:center; gap:6px; background:rgba(255,255,255,0.78); border:1px solid var(--border-light); border-radius:999px; padding:7px 18px; font-size:13.5px; font-weight:600; color:var(--text-muted); margin-bottom:28px; animation:fade-up 0.6s ease-out both; }}
.hero-title {{ font-size:clamp(36px,5vw,56px); font-weight:800; color:#1a1a1a; line-height:1.15; margin-bottom:20px; animation:fade-up 0.7s ease-out 0.1s both; }}
.hero-title-green {{ background:linear-gradient(135deg,var(--primary),var(--primary-glow)); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.hero-subtitle {{ font-size:17px; color:#3a3a3a; line-height:1.75; font-weight:500; max-width:560px; margin:0 auto 36px; animation:fade-up 0.7s ease-out 0.2s both; }}
.hero-buttons {{ display:flex; justify-content:center; gap:14px; margin-bottom:36px; animation:fade-up 0.7s ease-out 0.3s both; }}
.btn-primary {{ background:linear-gradient(135deg,var(--primary),var(--primary-light)); color:white !important; padding:14px 30px; border-radius:999px; font-size:16px; font-weight:600; text-decoration:none; display:inline-flex; align-items:center; gap:8px; box-shadow:0 4px 20px rgba(46,125,50,0.35); transition:transform 0.2s,box-shadow 0.2s; }}
.btn-primary:hover {{ transform:translateY(-2px); box-shadow:0 8px 28px rgba(46,125,50,0.45); }}
.btn-secondary {{ background:white; color:#222 !important; padding:14px 30px; border-radius:999px; font-size:16px; font-weight:600; text-decoration:none; border:1.5px solid #bbb; display:inline-flex; align-items:center; gap:8px; transition:transform 0.2s,border-color 0.2s; }}
.btn-secondary:hover {{ transform:translateY(-2px); border-color:var(--primary); color:var(--primary) !important; }}
.trust-bar {{ display:flex; justify-content:center; gap:28px; animation:fade-up 0.7s ease-out 0.4s both; margin-bottom:40px; }}
.trust-item {{ display:flex; align-items:center; gap:6px; font-size:14px; color:var(--text-muted); font-weight:600; }}

.ecg-wrap {{ width:100%; overflow:visible; background:transparent; margin-top:-90px; position:relative; z-index:2; padding-bottom:30px; }}
.ecg-svg  {{ width:100%; height:72px; display:block; }}
.ecg-path {{ fill:none; stroke:var(--primary); stroke-width:1.8; stroke-dasharray:1200; animation:ecg 5s ease-in-out infinite; opacity:0.55; }}

.how-section {{ padding:64px 48px 48px; text-align:center; background:white; position:relative; z-index:3; }}
.process-label {{ font-size:12px; font-weight:700; letter-spacing:2.5px; color:var(--primary); text-transform:uppercase; margin-bottom:10px; }}
.how-title {{ font-size:38px; font-weight:800; color:#1a1a1a; margin-bottom:10px; }}
.how-sub   {{ font-size:15px; color:#444; margin-bottom:44px; font-weight:500; }}
.cards-row {{ display:grid; grid-template-columns:repeat(3,1fr); gap:22px; max-width:860px; margin:0 auto 40px; }}
.step-card {{ background:white; border:1px solid #eee; border-radius:20px; padding:28px 22px; text-align:left; box-shadow:0 4px 24px -8px rgba(46,125,50,0.09); transition:transform 0.25s,box-shadow 0.25s; position:relative; overflow:hidden; cursor:default; }}
.step-card:hover {{ transform:translateY(-6px); box-shadow:0 14px 40px -8px rgba(46,125,50,0.18); }}
.step-card::before {{ content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,var(--primary),var(--primary-glow)); opacity:0; transition:opacity 0.25s; }}
.step-card:hover::before {{ opacity:1; }}
.step-num {{ position:absolute; top:18px; right:18px; font-size:38px; font-weight:800; color:#c8c8c8; line-height:1; }}
.step-icon-wrap {{ width:50px; height:50px; background:linear-gradient(135deg,var(--primary),var(--primary-light)); border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:22px; margin-bottom:18px; box-shadow:0 4px 14px rgba(46,125,50,0.28); }}
.step-title {{ font-size:17px; font-weight:700; color:#1a1a1a; margin-bottom:8px; }}
.step-desc  {{ font-size:14px; color:#444; line-height:1.65; }}
.footer {{ text-align:center; font-size:13px; color:white; font-weight:500; padding:20px 48px 32px; background:#2E7D32; }}
</style>

<div class="navbar">
    <div class="nav-logo">
        <div class="logo-icon-wrap"><div class="logo-pulse-ring"></div><div class="logo-icon">&#x270B;</div></div>
        <div><div class="logo-name">PD-HAND</div><div class="logo-sub">FCSIT &middot; UNIMAS</div></div>
    </div>
    <div class="nav-links">
        <a class="nav-link-btn active" href="?uid={user_id}&uname={user_name}"              target="_self">&#127968; Home</a>
        <a class="nav-link-btn"        href="?go=screening&uid={user_id}&uname={user_name}" target="_self">&#128269; Screening</a>
        <a class="nav-link-btn"        href="?go=history&uid={user_id}&uname={user_name}"   target="_self">&#128336; History</a>
    </div>
    <div class="nav-right">
        <a href="?go=edit_profile&uid={user_id}&uname={user_name}&phone={user_phone}" target="_self" style="text-decoration:none;">
            <div class="user-avatar">{initials}</div>
        </a>
        <a class="logout-btn" href="?go=logout" target="_self">&#x2192; Log out</a>
    </div>
</div>

<div class="hero">
    <div class="hero-orb hero-orb-1"></div>
    <div class="hero-orb hero-orb-2"></div>
    <div class="hero-badge">&#10024; AI-powered neurological screening</div>
    <div class="hero-title">Parkinson's <span class="hero-title-green">Early<br>Detection</span><br>Through Handwriting</div>
    <div class="hero-subtitle">A clinically inspired AI tool that analyzes subtle tremor patterns in your handwriting to help detect early signs of Parkinson's &mdash; in under a minute.</div>
    <div class="hero-buttons">
        <a class="btn-primary"   href="?go=screening&uid={user_id}&uname={user_name}" target="_self">Start Screening &#8594;</a>
        <a class="btn-secondary" href="?go=history&uid={user_id}&uname={user_name}"   target="_self">View History</a>
    </div>
    <div class="trust-bar">
        <div class="trust-item">&#129516; Clinically Inspired</div>
        <div class="trust-item">&#9889; Results in 60s</div>
    </div>
</div>

<div class="ecg-wrap">
    <svg class="ecg-svg" viewBox="0 0 1200 64" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path class="ecg-path" d="M0,32 L100,32 L120,32 L138,8 L150,56 L162,4 L174,60 L186,32 L210,32 L310,32 L330,32 L348,8 L360,56 L372,4 L384,60 L396,32 L420,32 L520,32 L540,32 L558,8 L570,56 L582,4 L594,60 L606,32 L630,32 L730,32 L750,32 L768,8 L780,56 L792,4 L804,60 L816,32 L840,32 L940,32 L960,32 L978,8 L990,56 L1002,4 L1014,60 L1026,32 L1050,32 L1150,32 L1200,32"/>
    </svg>
</div>

<div class="how-section">
    <div class="process-label">PROCESS</div>
    <div class="how-title">How It Works</div>
    <div class="how-sub">A simple three-step process for preliminary Parkinson's screening.</div>
    <div class="cards-row">
        <div class="step-card"><div class="step-num">01</div><div class="step-icon-wrap">&#9999;&#65039;</div><div class="step-title">Provide Sample</div><div class="step-desc">Upload or draw a spiral or meander pattern. Our system automatically detects which type was provided.</div></div>
        <div class="step-card"><div class="step-num">02</div><div class="step-icon-wrap">&#129504;</div><div class="step-title">AI Analysis</div><div class="step-desc">Our model analyzes tremor patterns, stroke characteristics, and micrographia indicators.</div></div>
        <div class="step-card"><div class="step-num">03</div><div class="step-icon-wrap">&#128202;</div><div class="step-title">Get Results</div><div class="step-desc">Receive a detailed screening result with a confidence score and clear next steps.</div></div>
    </div>
</div>

<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>
""", unsafe_allow_html=True)