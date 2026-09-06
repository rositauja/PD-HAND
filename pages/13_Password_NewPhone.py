import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.database import create_tables
from core.auth import restore_session

create_tables()

st.set_page_config(page_title="New Phone Number — PD-HAND", layout="wide", initial_sidebar_state="collapsed")

restore_session()

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

.step-number.completed {
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

/* TIP BOX */
.tip-box {
    background: #f5f5f5;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    font-size: 14px;
    color: #555;
    line-height: 1.5;
}

/* TEXT INPUT */
div[data-testid="stTextInput"] input {
    border:1.5px solid #e0e0e0 !important; 
    border-radius:10px !important;
    font-size:14px !important; 
    color:#333 !important; 
    background:white !important;
    padding:12px 16px !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color:#2E7D32 !important;
    box-shadow:0 0 0 3px rgba(46,125,50,0.1) !important;
}

div[data-testid="stTextInput"] label p {
    font-size:13px !important; 
    font-weight:600 !important; 
    color:#333 !important;
    margin-bottom:8px !important;
}

div[data-testid="stTextInput"] input::placeholder {
    font-size:14px !important;
    color:#999 !important;
}

div[data-testid="InputInstructions"] {
    display: none !important;
}

/* BUTTONS */
div.stFormSubmitButton > button {
    width:100% !important;
    padding:14px 0 !important;
    font-size:16px !important;
    font-weight:700 !important;
    border-radius:10px !important;
    border:none !important;
    cursor:pointer !important;
    transition:all 0.3s !important;
}

/* BACK BUTTON */
div.stFormSubmitButton:first-of-type > button {
    background:#f5f5f5 !important;
    color:#000000 !important;
    border:1px solid #e0e0e0 !important;
    box-shadow:none !important;
}

div.stFormSubmitButton:first-of-type > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 4px 16px rgba(0,0,0,0.1) !important;
    background:#2E7D32 !important;
    color:white !important;
}

/* CONTINUE BUTTON */
div.stFormSubmitButton:last-of-type > button {
    background:linear-gradient(135deg,#2E7D32,#43A047) !important;
    color:white !important;
    box-shadow:0 4px 16px rgba(46,125,50,0.3) !important;
}

div.stFormSubmitButton:last-of-type > button:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 6px 20px rgba(46,125,50,0.4) !important;
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
</style>
""", unsafe_allow_html=True)

# Check if user has completed security questions
if not st.session_state.get("recovery_verified"):
    st.switch_page("pages/12_Password_Security.py")

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

    # Progress Indicator
    st.markdown("""
        <div class="progress-container">
            <div class="progress-step">
                <div class="step-number completed">✓</div>
                <div class="step-label">Phone</div>
            </div>
            <div class="progress-step">
                <div class="step-number completed">✓</div>
                <div class="step-label">Security</div>
            </div>
            <div class="progress-step">
                <div class="step-number active">3</div>
                <div class="step-label">New Phone</div>
            </div>
            <div class="progress-step">
                <div class="step-number">4</div>
                <div class="step-label">Verify OTP</div>
            </div>
            <div class="progress-step">
                <div class="step-number">5</div>
                <div class="step-label">New Password</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Main Card
    st.markdown("""
        <div class="recovery-card">
            <h2>Set a new phone number</h2>
            <p>This will become the phone number used to sign in to your account.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("new_phone_form"):
        # Tip Box
        st.markdown("""
            <div class="tip-box">
                <strong>Tip:</strong> Use a phone number you currently own — we'll send a one-time code to verify it.
            </div>
        """, unsafe_allow_html=True)

        # New Phone Number
        new_phone = st.text_input(
            "New phone number",
            placeholder="+60 12 345 6789",
            key="new_phone_input",
            label_visibility="visible"
        )

        # Confirm Phone Number
        confirm_phone = st.text_input(
            "Confirm new phone number",
            placeholder="Re-enter phone number",
            key="confirm_phone_input",
            label_visibility="visible"
        )

        # Buttons
        col_back, col_continue = st.columns([1, 1])
        
        with col_back:
            back_clicked = st.form_submit_button("← Back", use_container_width=True)
        
        with col_continue:
            send_clicked = st.form_submit_button("Send code →", use_container_width=True)

        if back_clicked:
            st.switch_page("pages/12_Password_Security.py")

        if send_clicked:
            if not new_phone or not confirm_phone:
                st.error("Please fill in both phone number fields.")
            elif new_phone != confirm_phone:
                st.error("Phone numbers do not match. Please try again.")
            else:
                # Store new phone in session and move to next step
                st.session_state.new_phone = new_phone
                st.session_state.otp_generated = False  # Reset OTP flag
                st.success("Phone number verified! Sending verification code...")
                st.switch_page("pages/14_Password_OTP.py")

    st.markdown("""
        <div style="text-align: center; margin-top: 40px;">
            <a href="/Login" style="color: white; text-decoration: none; font-size: 14px; font-weight: 500;">← Back to login</a>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>', unsafe_allow_html=True)