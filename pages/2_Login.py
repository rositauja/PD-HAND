# pages/2_Login.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.database import create_tables, verify_user
from core.auth import restore_session

create_tables()

st.set_page_config(page_title="Login — PD-HAND", layout="wide", initial_sidebar_state="collapsed")

restore_session()
if st.session_state.get("authenticated"):
    st.switch_page("pages/3_Home.py")

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
    --primary: #2E7D32; --primary-light: #43A047;
    --primary-glow: #66BB6A; --border-light: #c8e6c9;
    --text-dark: #1b5e20; --text-muted: #2e6b3e;
}
@keyframes heartbeat {
    0%,100%{transform:scale(1)} 15%{transform:scale(1.18)}
    30%{transform:scale(1)} 45%{transform:scale(1.10)} 60%{transform:scale(1)}
}
@keyframes pulse-ring {
    0%{transform:scale(0.85);opacity:0.6} 100%{transform:scale(2.0);opacity:0}
}

.navbar {
    display:flex; justify-content:space-between; align-items:center;
    padding:16px 48px; border-bottom:1px solid var(--border-light);
    background:rgba(255,255,255,0.97); position:sticky; top:0; z-index:100;
}
.nav-logo { display:flex; align-items:center; gap:12px; }
.logo-icon-wrap { position:relative; width:44px; height:44px; display:flex; align-items:center; justify-content:center; }
.logo-pulse-ring { position:absolute; inset:0; border-radius:50%; background:var(--primary-glow); opacity:0.5; animation:pulse-ring 2s ease-out infinite; }
.logo-icon { position:relative; width:44px; height:44px; background:linear-gradient(135deg,var(--primary),var(--primary-light)); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:20px; animation:heartbeat 1.8s ease-in-out infinite; box-shadow:0 4px 16px rgba(46,125,50,0.35); z-index:1; }
.logo-name { font-size:17px; font-weight:800; color:var(--text-dark); }
.logo-sub  { font-size:10px; font-weight:500; color:var(--text-muted); letter-spacing:0.5px; }

.stApp {
    background:linear-gradient(135deg,#f0faf3 0%,#d4edda 50%,#c8e6c9 100%) !important;
}

section.main > div {
    min-height:calc(100vh - 77px);
}

div[data-testid="stForm"] {
    background:white !important; border-radius:20px !important;
    padding:36px 40px !important;
    box-shadow:0 4px 32px rgba(46,125,50,0.12) !important;
    border:none !important;
}
div[data-testid="stTextInput"] input {
    border:1.5px solid #e0e0e0 !important; border-radius:10px !important;
    font-size:16px !important; color:#333 !important; background:white !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color:#2E7D32 !important;
    box-shadow:0 0 0 3px rgba(46,125,50,0.1) !important;
}
div[data-testid="stTextInput"] label p {
    font-size:13px !important; font-weight:600 !important; color:#333 !important;
}

/* Hide browser password autofill suggestions and tooltips */
div[data-testid="stTextInput"] input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 1000px white inset !important;
    -webkit-text-fill-color: #333 !important;
}
            
div[data-testid="stTextInput"] input::placeholder {
    font-size:14px !important;
}

/* Remove "Press Enter to submit form" helper text */
div[data-testid="InputInstructions"] {
    display: none !important;
}

div.stFormSubmitButton > button {
    width:100% !important;
    background:linear-gradient(135deg,#2E7D32,#43A047) !important;
    color:white !important; border:none !important; border-radius:10px !important;
    padding:14px 0 !important; font-size:16px !important; font-weight:700 !important;
    box-shadow:0 4px 16px rgba(46,125,50,0.3) !important; margin-top:8px !important;
    cursor:pointer !important;
}
div.stFormSubmitButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 6px 20px rgba(46,125,50,0.4) !important;
}

.footer { text-align:center; font-size:13px; color:white; font-weight:500; padding:20px 48px 32px; background:#2E7D32; }
</style>

<div class="navbar">
    <div class="nav-logo">
        <div class="logo-icon-wrap"><div class="logo-pulse-ring"></div><div class="logo-icon">&#x270B;</div></div>
        <div><div class="logo-name">PD-HAND</div><div class="logo-sub">FCSIT &middot; UNIMAS</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    st.markdown("""
        <div style="text-align:center; padding:36px 0 24px 0;">
            <div style="width:60px;height:60px;background:linear-gradient(135deg,#2E7D32,#43A047);
                border-radius:50%;display:inline-flex;align-items:center;justify-content:center;
                font-size:26px;box-shadow:0 4px 16px rgba(46,125,50,0.35);margin-bottom:16px;">
                &#x270B;
            </div>
            <div style="font-size:28px;font-weight:800;color:#1a1a1a;margin-bottom:6px;">Welcome back</div>
            <div style="font-size:14px;color:#777;margin-bottom:4px;">Log in to continue your handwriting screening.</div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        phone = st.text_input(
            "Phone Number",
            placeholder="+60 12 3456 7890",
            autocomplete="off"
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••",
            autocomplete="current-password"
        )
        submitted = st.form_submit_button("Login →")

        if submitted:
            if not phone or not password:
                st.error("Please fill in both fields.")
            else:
                user = verify_user(phone, password)
                if user:
                    st.session_state["authenticated"] = True
                    st.session_state["user_id"]       = user["id"]
                    st.session_state["user_name"]     = user["name"]
                    st.session_state["user_phone"]    = user["phone"]
                    st.success(f"Welcome back, {user['name']}!")
                    
                    # Redirect to home with auth params in URL
                    st.query_params.update({
                        "uid": user["id"],
                        "uname": user["name"]
                    })
                    st.switch_page("pages/3_Home.py")
                else:
                    st.error("Invalid phone number or password. Please try again.")

    # Forgot Password & Register Links
    st.markdown("""
        <div style="text-align:center; font-size:14px; color:#777;
                    margin-top:20px; padding-bottom:48px;">
            <div style="margin-bottom:12px;">
                <a href="/Password" target="_self"
                   style="color:#2E7D32; font-weight:600; text-decoration:none; font-size:14px;">
                    Forgot password?
                </a>
            </div>
            <div style="font-size:14px;">
                Don't have an account?
                <a href="/Register" target="_self"
                   style="color:#2E7D32; font-weight:700; text-decoration:none;">
                    Register here
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>', unsafe_allow_html=True)