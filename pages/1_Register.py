import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.database import create_tables, register_user
from core.auth import restore_session

create_tables()

st.set_page_config(page_title="Register — PD-HAND", layout="wide", initial_sidebar_state="collapsed")

restore_session()
if st.session_state.get("authenticated"):
    st.switch_page("pages/3_Home.py")

# ── Track form completeness for button state ───────────────────────────────────
if "reg_name"      not in st.session_state: st.session_state.reg_name      = ""
if "reg_phone"     not in st.session_state: st.session_state.reg_phone     = ""
if "reg_password"  not in st.session_state: st.session_state.reg_password  = ""
if "reg_confirm"   not in st.session_state: st.session_state.reg_confirm   = ""
if "reg_dominant"  not in st.session_state: st.session_state.reg_dominant  = None
if "reg_diagnosed" not in st.session_state: st.session_state.reg_diagnosed = None
if "reg_consent1"  not in st.session_state: st.session_state.reg_consent1  = False
if "reg_consent2"  not in st.session_state: st.session_state.reg_consent2  = False

# Button always enabled — validation happens on submit
btn_bg     = "linear-gradient(135deg, #2E7D32, #43A047)"
btn_color  = "white"
btn_cursor = "pointer"
btn_shadow = "0 4px 16px rgba(46,125,50,0.3)"

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
    --primary: #2E7D32; --primary-light: #43A047;
    --primary-glow: #66BB6A; --border-light: #c8e6c9;
    --text-dark: #1b5e20; --text-muted: #2e6b3e;
}}
@keyframes heartbeat {{
    0%,100%{{transform:scale(1)}} 15%{{transform:scale(1.18)}}
    30%{{transform:scale(1)}} 45%{{transform:scale(1.10)}} 60%{{transform:scale(1)}}
}}
@keyframes pulse-ring {{
    0%{{transform:scale(0.85);opacity:0.6}} 100%{{transform:scale(2.0);opacity:0}}
}}

/* NAVBAR */
.navbar {{
    display:flex; justify-content:space-between; align-items:center;
    padding:16px 48px; border-bottom:1px solid var(--border-light);
    background:rgba(255,255,255,0.97); position:sticky; top:0; z-index:100;
}}
.nav-logo {{ display:flex; align-items:center; gap:12px; }}
.logo-icon-wrap {{ position:relative; width:44px; height:44px; display:flex; align-items:center; justify-content:center; }}
.logo-pulse-ring {{ position:absolute; inset:0; border-radius:50%; background:var(--primary-glow); opacity:0.5; animation:pulse-ring 2s ease-out infinite; }}
.logo-icon {{ position:relative; width:44px; height:44px; background:linear-gradient(135deg,var(--primary),var(--primary-light)); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:20px; animation:heartbeat 1.8s ease-in-out infinite; box-shadow:0 4px 16px rgba(46,125,50,0.35); z-index:1; }}
.logo-name {{ font-size:17px; font-weight:800; color:var(--text-dark); }}
.logo-sub  {{ font-size:10px; font-weight:500; color:var(--text-muted); letter-spacing:0.5px; }}

/* PAGE BACKGROUND */
[data-testid="stAppViewContainer"] {{
    background: linear-gradient(135deg, #f0faf3 0%, #d4edda 50%, #c8e6c9 100%) !important;
}}
[data-testid="stApp"] {{
    background: linear-gradient(135deg, #f0faf3 0%, #d4edda 50%, #c8e6c9 100%) !important;
}}

/* FORM CARD */
div[data-testid="stForm"] {{
    background: white !important; border-radius: 20px !important;
    padding: 36px 40px !important;
    box-shadow: 0 4px 32px rgba(46,125,50,0.12) !important;
    border: none !important;
}}

/* TEXT INPUTS — CLEAN SOFT VERSION */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-baseweb="input"] input {{
    border: 1.5px solid #dfe5df !important;
    border-radius: 10px !important;

    font-size: 14px !important;
    color: #333 !important;

    background: #ffffff !important;

    box-shadow: none !important;
    outline: none !important;
}}

/* REMOVE DEFAULT BLACK BORDER WRAPPER */
div[data-baseweb="input"] {{
    border: none !important;
    box-shadow: none !important;
}}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {{
    border-color: #2E7D32 !important;
    box-shadow: 0 0 0 3px rgba(46,125,50,0.1) !important;
}}
div[data-testid="stTextInput"] label p,
div[data-testid="stNumberInput"] label p {{
    font-size: 13px !important; font-weight: 600 !important; color: #333 !important;
}}

/* FIX MISSING LABEL TEXT ON IPAD SAFARI */
label:not(div.stFormSubmitButton *),
p:not(div.stFormSubmitButton *),
div[data-testid="stMarkdownContainer"] p {{
    color: #333 !important;
}}

/* SECURITY QUESTION LABELS */
div[data-testid="stSelectbox"] label {{
    color: #333 !important;
    font-weight: 600 !important;
}}

/* HELPER TEXT */
div[data-testid="stMarkdownContainer"] {{
    color: #666 !important;
}}
            
/* Remove "Press Enter to submit form" helper text */
div[data-testid="InputInstructions"] {{
    display: none !important;
}}

/* NUMBER INPUT BUTTONS (+ and -) */
div[data-testid="stNumberInput"] button {{
    background: #2E7D32 !important;
    color: white !important;
    border: none !important;
}}

div[data-testid="stNumberInput"] button:hover {{
    background: #43A047 !important;
    color: white !important;
}}

/* SELECTBOX / SECURITY QUESTIONS — FIX FOR SAFARI/IPAD */
div[data-baseweb="select"] > div {{
    background: #E8F5E9 !important;
    border: 1.5px solid #C8E6C9 !important;
    border-radius: 10px !important;
    color: #1a1a1a !important;
    box-shadow: none !important;
}}

/* Selected text in dropdown */
div[data-baseweb="select"] span {{
    color: #1a1a1a !important;
    font-size: 14px !important;
}}

/* Dropdown arrow icon */
div[data-baseweb="select"] svg {{
    fill: #2E7D32 !important;
}}

/* PASSWORD EYE BUTTON — CONNECTED VERSION */

/* Remove grey wrapper */
div[data-testid="stTextInput"] div:has(button) {{
    background: transparent !important;
    border: none !important;
}}

/* Style eye button */
div[data-testid="stTextInput"] button {{
    background: #2E7D32 !important;
    color: white !important;
    border: none !important;

    width: 56px !important;
    min-width: 56px !important;

    height: 42px !important;
    min-height: 42px !important;

    border-radius: 0 10px 10px 0 !important;

    margin: 0 !important;
    padding: 0 !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    box-shadow: none !important;
}}

/* Hover */
div[data-testid="stTextInput"] button:hover {{
    background: #43A047 !important;
    color: white !important;
}}

/* RADIO BUTTONS — SAFE VERSION FOR IPAD */
div[data-testid="stRadio"] > label {{
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #1a1a1a !important;
    margin-bottom: 6px !important;
}}

div[data-testid="stRadio"] {{
    margin-bottom: 8px !important;
}}

div[data-testid="stRadio"] label p {{
    font-size: 14px !important;
    color: #444 !important;
}}

/* CHECKBOX TEXT */
div[data-testid="stCheckbox"] label p {{
    font-size: 13.5px !important;
    color: #444 !important;
}}

/* FORCE CHECKBOX BOX GREEN — MULTIPLE SELECTORS */
div[data-testid="stCheckbox"] div[role="checkbox"] {{
    background-color: #43A047 !important;
    background: #43A047 !important;
}}

/* Fill the checkbox completely */
div[data-testid="stCheckbox"] svg {{
    fill: white !important;
    stroke: none !important;
}}

/* Target the inner container */
div[data-testid="stCheckbox"] div[role="checkbox"] > * {{
    background-color: #43A047 !important;
}}

/* Fallback for native input */
div[data-testid="stCheckbox"] input[type="checkbox"] {{
    accent-color: #43A047 !important;
    appearance: none !important;
    width: 18px !important;
    height: 18px !important;
    background: #43A047 !important;
    border: none !important;
    border-radius: 4px !important;
    cursor: pointer !important;
}}

/* SUBMIT BUTTON — dynamic color based on form completeness */
div.stFormSubmitButton > button {{
    width: 100% !important;
    background: {btn_bg} !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 0 !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    box-shadow: {btn_shadow} !important;
    cursor: {btn_cursor} !important;
    margin-top: 8px !important;
    transition: all 0.3s !important;
}}

/* Register button hover effect */
div.stFormSubmitButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(46,125,50,0.4) !important;
    filter: brightness(1.08) !important;
    transition: all 0.3s ease !important;
}}

/* FORCE BUTTON TEXT WHITE — override label rules */
div.stFormSubmitButton > button,
div.stFormSubmitButton > button * {{
    color: white !important;
}}

/* STEP CARDS */
.step-card {{
    background: #E8F5E9 !important;
    border: 1px solid #C8E6C9 !important;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 16px rgba(46,125,50,0.06);
}}
.step-header {{ display: flex; align-items: center; gap: 14px; }}
.step-badge {{
    width: 36px; height: 36px; border-radius: 50%;
    background: linear-gradient(135deg, #2E7D32, #43A047);
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 16px; flex-shrink: 0;
}}
.step-label {{ font-size: 11px; font-weight: 600; color: #999; letter-spacing: 1px; text-transform: uppercase; }}
.step-title-text {{ font-size: 16px; font-weight: 700; color: #1a1a1a; }}

/* FOOTER */
.footer {{
    text-align: center; font-size: 13px; color: white;
    font-weight: 500; padding: 20px 48px 32px; background: #2E7D32;
}}

/* RESPONSIVE PATCH FOR IPAD/TABLET */
@media screen and (max-width: 1024px) {{
    div[data-testid="stForm"] {{
        padding: 24px 20px !important;
    }}

    .navbar {{
        padding: 14px 20px !important;
    }}

    .footer {{
        padding: 18px 16px 24px !important;
    }}
}}
</style>

<div class="navbar">
    <div class="nav-logo">
        <div class="logo-icon-wrap">
            <div class="logo-pulse-ring"></div>
            <div class="logo-icon">&#x270B;</div>
        </div>
        <div>
            <div class="logo-name">PD-HAND</div>
            <div class="logo-sub">FCSIT &middot; UNIMAS</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2.2, 1])
with col2:

    st.markdown("""
        <div style="text-align:center; padding:36px 0 24px 0;">
            <div style="width:60px;height:60px;background:linear-gradient(135deg,#2E7D32,#43A047);
                border-radius:50%;display:inline-flex;align-items:center;justify-content:center;
                font-size:26px;box-shadow:0 4px 16px rgba(46,125,50,0.35);margin-bottom:16px;">
                &#x270B;
            </div>
            <div style="font-size:28px;font-weight:800;color:#1a1a1a;margin-bottom:6px;">
                Create your account
            </div>
            <div style="font-size:14px;color:#777;">
                A few quick details so we can tailor your handwriting screening.
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("register_form"):

        # ── STEP 1 ─────────────────────────────────────────────────────────────
        st.markdown("""
        <div class="step-card"><div class="step-header">
            <div class="step-badge">&#128100;</div>
            <div><div class="step-label">STEP 1</div><div class="step-title-text">Account information</div></div>
        </div></div>""", unsafe_allow_html=True)

        name     = st.text_input("Name",        placeholder="Your name",          key="reg_name")
        phone    = st.text_input("Phone Number",     placeholder="01xxxxxxxxx",        key="reg_phone")
        password = st.text_input("Password",         type="password", placeholder="At least 6 characters", key="reg_password")
        confirm  = st.text_input("Confirm password", type="password", placeholder="Re-enter password",      key="reg_confirm")

        # ── STEP 2 ─────────────────────────────────────────────────────────────
        st.markdown("""
        <div class="step-card"><div class="step-header">
            <div class="step-badge">&#128100;</div>
            <div><div class="step-label">STEP 2</div><div class="step-title-text">Basic profile</div></div>
        </div></div>""", unsafe_allow_html=True)

        age      = st.number_input("Age", min_value=1, max_value=120, step=1, value=1)
        dominant = st.radio("Dominant hand", ["Right", "Left", "Ambidextrous"], index=None, horizontal=False, key="reg_dominant")
        gender   = st.radio("Gender", ["Male", "Female", "Prefer not to say"], index=None, horizontal=False)

        # ── STEP 3 ─────────────────────────────────────────────────────────────
        st.markdown("""
        <div class="step-card"><div class="step-header">
            <div class="step-badge">&#9889;</div>
            <div><div class="step-label">STEP 3</div><div class="step-title-text">Parkinson's background</div></div>
        </div></div>""", unsafe_allow_html=True)

        diagnosed = st.radio("Have you been diagnosed with Parkinson's Disease?", ["Yes", "No"], index=None, horizontal=False, key="reg_diagnosed")
        year_diagnosed = None
        if diagnosed == "Yes":
            year_diagnosed = st.number_input("Year of diagnosis", min_value=1900, max_value=2025, step=1, value=None)
        family = st.radio("Family history of Parkinson's Disease?", ["Yes", "No", "Unsure"], index=None, horizontal=False)

        # ── STEP 4: SECURITY QUESTIONS ─────────────────────────────────────────
        st.markdown("""
        <div class="step-card"><div class="step-header">
            <div class="step-badge">&#128274;</div>
            <div><div class="step-label">STEP 4</div><div class="step-title-text">Security questions</div></div>
        </div></div>""", unsafe_allow_html=True)

        st.caption("Answer these 2 questions to help recover your account if you forget your password.")
        
        security_questions = [
            "What is the name of the town or city you were born?",
            "In what year you were born?",
            "What is the name of the neighborhood where you grew up?",
            "What was your first job?",
            "What is your favorite colour?"
        ]

        sq1 = st.selectbox("Security Question 1", security_questions, index=0)
        sa1 = st.text_input("Answer to Question 1", placeholder="Your answer", key="sq_a1")

        sq2 = st.selectbox("Security Question 2", security_questions, index=1)
        sa2 = st.text_input("Answer to Question 2", placeholder="Your answer", key="sq_a2")

        # ── STEP 5: CONSENT ────────────────────────────────────────────────────
        st.markdown("""
        <div class="step-card"><div class="step-header">
            <div class="step-badge">&#9989;</div>
            <div><div class="step-label">STEP 5</div><div class="step-title-text">Consent</div></div>
        </div></div>""", unsafe_allow_html=True)

        consent1 = st.checkbox("I understand that this system is for screening and research purposes only and does not provide a medical diagnosis.", key="reg_consent1")
        consent2 = st.checkbox("I consent to my data being stored for screening and research purposes.", key="reg_consent2")
        if not (consent1 and consent2):
            st.caption("Please accept both consent statements to continue.")

        submitted = st.form_submit_button("Register →")

        if submitted:
            if not name or not phone or not password or not confirm:
                st.error("Please fill in all required fields.")
            elif not dominant:
                st.error("Please select your dominant hand.")
            elif not diagnosed:
                st.error("Please answer the Parkinson diagnosis question.")
            elif not sa1 or not sa2:
                st.error("Please answer both security questions.")
            elif not (consent1 and consent2):
                st.error("Please accept both consent statements.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                security_data = {
                    "q1": sq1, "a1": sa1,
                    "q2": sq2, "a2": sa2
                }
                success = register_user(name, phone, password, age=age, dominant_hand=dominant, security_questions=security_data)
                if success:
                    st.success("Account created successfully! Redirecting to login...")
                    st.switch_page("pages/2_Login.py")
                else:
                    st.error("An account with this phone number already exists. Please log in.")

    # ── Plain text link — no button box ───────────────────────────────────────
    st.markdown("""
        <div style="text-align:center; font-size:14px; color:#777;
                    margin-top:20px; padding-bottom:48px; font-size:17px;">
            Already have an account?
            <a href="/Login" target="_self"
               style="color:#2E7D32; font-weight:700; text-decoration:none;">
                Log in here
            </a>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>', unsafe_allow_html=True)