import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.database import create_tables, get_user_by_phone
from core.auth import restore_session

create_tables()

st.set_page_config(page_title="Forgot Password — PD-HAND", layout="wide", initial_sidebar_state="collapsed")

restore_session()

# Initialize session state for recovery flow
if "recovery_phone" not in st.session_state:
    st.session_state.recovery_phone = None

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
    --primary: #2E7D32;
    --primary-light: #43A047;
    --primary-glow: #66BB6A;
    --border-light: #c8e6c9;
    --text-dark: #1b5e20;
    --text-muted: #2e6b3e;
}

section.main > div {
    background: linear-gradient(135deg, #f5fdf7 0%, #e8f5e9 50%, #d4edda 100%) !important;
    min-height: 100vh;
}

div[data-testid="stForm"] {
    background:white !important; 
    border-radius:20px !important;
    padding:36px 40px !important;
    box-shadow:0 4px 32px rgba(46,125,50,0.12) !important;
    border:none !important;
}

.recovery-header {
    text-align: center;
    margin-bottom: 32px;
    margin-top: 40px;
}

.logo-icon {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #2E7D32, #43A047);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    box-shadow: 0 4px 16px rgba(46,125,50,0.35);
    margin: 0 auto 20px;
}
        
.stApp {
    background:linear-gradient(135deg,#f0faf3 0%,#d4edda 50%,#c8e6c9 100%) !important;
}

.header-text {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 16px;
}

.header-title {
    font-size: 20px;
    font-weight: 800;
    color: #1b5e20;
    margin: 0;
}

.header-badge {
    font-size: 11px;
    font-weight: 700;
    color: white;
    background: #2E7D32;
    padding: 6px 12px;
    border-radius: 999px;
}

.header-sub {
    font-size: 12px;
    color: #2e6b3e;
    letter-spacing: 0.5px;
}

/* PROGRESS INDICATOR */
.progress-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0;
    margin: 32px auto 48px;
    padding: 0 20px;
    max-width: 100%;
}

.progress-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    flex: 1;
    position: relative;
}

.progress-step:not(:last-child)::after {
    content: '';
    position: absolute;
    top: 19px;
    left: 50%;
    width: 100%;
    height: 2px;
    background: #ddd;
    z-index: 0;
}

.step-number {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: white;
    border: 2px solid #e8e8e8;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    color: #999;
    font-size: 15px;
    z-index: 1;
    position: relative;
}

.step-number.active {
    background: #2E7D32;
    color: white;
    border-color: #2E7D32;
}

.step-label {
    font-size: 12px;
    font-weight: 600;
    color: #333;
    white-space: nowrap;
}

/* MAIN CARD */
.recovery-card {
    background: transparent;
    border-radius: 16px;
    padding: 0;
    box-shadow: none;
    margin: 0 auto 32px;
}

.recovery-card h2 {
    font-size: 32px;
    font-weight: 800;
    color: #1a1a1a;
    margin: 0 0 12px 0;
    text-align: center;
}

.recovery-card p {
    font-size: 15px;
    color: #666;
    text-align: center;
    margin: 0;
    line-height: 1.6;
}

/* TEXT INPUT */
div[data-testid="stTextInput"] input {
    border:1.5px solid #e0e0e0 !important; 
    border-radius:10px !important;
    font-size:14px !important; 
    color:#333 !important; 
    background:white !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color:#2E7D32 !important;
    box-shadow:0 0 0 3px rgba(46,125,50,0.1) !important;
}

div[data-testid="stTextInput"] label p {
    font-size:13px !important; 
    font-weight:600 !important; 
    color:#333 !important;
}

div[data-testid="stTextInput"] input:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 1000px white inset !important;
    -webkit-text-fill-color: #333 !important;
}
            
div[data-testid="stTextInput"] input::placeholder {
    font-size:14px !important;
}

div[data-testid="InputInstructions"] {
    display: none !important;
}

/* BUTTONS */
div.stFormSubmitButton > button {
    width:100% !important;
    background:linear-gradient(135deg,#2E7D32,#43A047) !important;
    color:white !important; 
    border:none !important; 
    border-radius:10px !important;
    padding:14px 0 !important; 
    font-size:16px !important; 
    font-weight:700 !important;
    box-shadow:0 4px 16px rgba(46,125,50,0.3) !important; 
    margin-top:8px !important;
    cursor:pointer !important;
}

div.stFormSubmitButton > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 6px 20px rgba(46,125,50,0.4) !important;
}

.hint-text {
    font-size: 13px;
    color: #999;
    text-align: center;
    margin-top: 12px;
    padding: 0 16px;
}

.link-section {
    text-align: center;
    margin-top: 20px;
    font-size: 14px;
    color: #666;
}

.link-section a {
    color: #2E7D32;
    font-weight: 600;
    text-decoration: none;
}

.link-section a:hover {
    text-decoration: underline;
}

.footer {
    text-align: center;
    font-size: 13px;
    color: white;
    font-weight: 500;
    padding: 20px 40px 32px;
    background: #2E7D32;
    margin-top: 60px;
}

.back-link {
    text-align: center;
    padding-top: 20px;
    font-size: 14px;
}

.back-link a {
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: opacity 0.3s;
}

.back-link a:hover {
    opacity: 0.8;
}
</style>
""", unsafe_allow_html=True)

# Main Container
col1, col2, col3 = st.columns([1, 1.2, 1])

with col2:
    # Header
    st.markdown("""
        <div class="recovery-header">
            <div class="logo-icon">👋</div>
            <div class="header-text">
                <div style="text-align: center;">
                    <div class="header-title">PD-HAND</div>
                </div>
                <div class="header-badge">ACCOUNT RECOVERY</div>
            </div>
            <div class="header-sub">FCSIT · UNIMAS</div>
        </div>
    """, unsafe_allow_html=True)

    # Progress Indicator (3 steps)
    st.markdown("""
        <div class="progress-container">
            <div class="progress-step">
                <div class="step-number active">1</div>
                <div class="step-label">Phone</div>
            </div>
            <div class="progress-step">
                <div class="step-number">2</div>
                <div class="step-label">Verify OTP</div>
            </div>
            <div class="progress-step">
                <div class="step-number">3</div>
                <div class="step-label">New Password</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Main Card
    st.markdown("""
        <div class="recovery-card">
            <h2>Forgot your password?</h2>
            <p>No problem. Enter the phone number linked to your account and we'll help you recover access.</p>
        </div>
    """, unsafe_allow_html=True)

    # Form
    with st.form("phone_recovery_form"):
        phone = st.text_input(
            "Phone number",
            placeholder="+60 12 345 6789",
            key="recovery_phone_input"
        )

        submitted = st.form_submit_button("Continue →")

        st.markdown("""
            <div class="hint-text">
                Use the same phone number you used when registering.
            </div>
        """, unsafe_allow_html=True)

        if submitted:
            if not phone:
                st.error("Please enter your phone number.")
            else:
                # Check if user exists
                user = get_user_by_phone(phone)
                if user:
                    # Store phone in session and move to OTP page (fast path)
                    st.session_state.recovery_phone = phone
                    st.success("Phone number verified! Sending OTP...")
                    st.switch_page("pages/12_Password_OTP_Direct.py")
                else:
                    st.error("No account found with this phone number. Please check and try again.")

    st.markdown("""
        <div class="link-section">
            Changed your phone number? <a href="/Password_Direct">New phone number</a>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="link-section">
            Remembered your password? <a href="/Login">Sign in</a>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>', unsafe_allow_html=True)