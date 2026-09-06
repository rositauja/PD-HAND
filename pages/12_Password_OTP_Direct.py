import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.database import create_tables, verify_otp, get_otp_expiration_time, get_otp_attempts_remaining, generate_otp, reset_password
from core.auth import restore_session
import random
import time

create_tables()

st.set_page_config(page_title="Verify OTP — PD-HAND", layout="wide", initial_sidebar_state="collapsed")

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

.stApp {
    background:linear-gradient(135deg,#f0faf3 0%,#d4edda 50%,#c8e6c9 100%) !important;
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

/* OTP INPUT BOXES */
.otp-container {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin: 32px 0;
}

.otp-input {
    width: 50px;
    height: 50px;
    border: 1.5px solid #e0e0e0;
    border-radius: 10px;
    font-size: 20px;
    text-align: center;
    font-weight: 700;
    background: white;
    color: #333;
}

.otp-input:focus {
    border-color: #2E7D32 !important;
    box-shadow: 0 0 0 3px rgba(46,125,50,0.1) !important;
}

/* TIMER AND RESEND */
.timer-section {
    text-align: center;
    margin: 24px 0;
    font-size: 14px;
    color: #666;
}

.timer-section strong {
    color: #2E7D32;
    font-weight: 700;
}

.resend-link {
    text-align: center;
    margin-top: 16px;
    font-size: 14px;
}

.resend-link a {
    color: #2E7D32;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
}

.resend-link a:hover {
    text-decoration: underline;
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

/* VERIFY BUTTON */
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

# Check if user entered phone number
if not st.session_state.get("recovery_phone"):
    st.switch_page("pages/11_Password.py")

# Initialize session state
if "otp_generated_direct" not in st.session_state:
    st.session_state.otp_generated_direct = False
    st.session_state.otp_code_direct = None

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

    # Progress Indicator (3 steps only)
    st.markdown("""
        <div class="progress-container">
            <div class="progress-step">
                <div class="step-number completed">✓</div>
                <div class="step-label">Phone</div>
            </div>
            <div class="progress-step">
                <div class="step-number active">2</div>
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
            <h2>Enter the verification code</h2>
            <p>We sent a 6-digit code to your registered phone number. Please enter it below.</p>
        </div>
    """, unsafe_allow_html=True)

    # Generate OTP on first load
    if not st.session_state.otp_generated_direct:
        # Generate a 6-digit code
        otp_code = str(random.randint(100000, 999999))
        st.session_state.otp_code_direct = otp_code
        st.session_state.otp_generated_direct = True
        
        # Save to database
        generate_otp(st.session_state.recovery_phone, otp_code)
        
        # Show the OTP in development (remove in production)
        st.info(f"📌 **Development Mode:** Your OTP is `{otp_code}` (valid for 10 minutes)")

    with st.form("otp_direct_form"):
        # OTP Input Fields
        otp_cols = st.columns(6, gap="small")
        otp_inputs = []
        
        for i in range(6):
            with otp_cols[i]:
                digit = st.text_input(
                    f"Digit {i+1}",
                    max_chars=1,
                    key=f"otp_direct_{i}",
                    label_visibility="collapsed",
                    placeholder="•"
                )
                otp_inputs.append(digit)

        # Combine OTP
        otp_entered = "".join(otp_inputs)

        # Timer and Resend
        expiration = get_otp_expiration_time(st.session_state.recovery_phone)
        if expiration > 0:
            minutes = expiration // 60
            seconds = expiration % 60
            st.markdown(f"""
                <div class="timer-section">
                    Resend code in <strong>{minutes}:{seconds:02d}</strong>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="resend-link">
                    Code expired. <a onclick="location.reload()">Request new code</a>
                </div>
            """, unsafe_allow_html=True)

        # Buttons
        col_back, col_verify = st.columns([1, 1])
        
        with col_back:
            back_clicked = st.form_submit_button("← Back", use_container_width=True)
        
        with col_verify:
            verify_clicked = st.form_submit_button("Verify →", use_container_width=True)

        if back_clicked:
            st.session_state.otp_generated_direct = False
            st.switch_page("pages/11_Password.py")

        if verify_clicked:
            if len(otp_entered) != 6 or not otp_entered.isdigit():
                st.error("Please enter a valid 6-digit code.")
            else:
                # Verify OTP
                if verify_otp(st.session_state.recovery_phone, otp_entered):
                    st.success("OTP verified! Proceeding to set new password...")
                    st.session_state.otp_verified_direct = True
                    time.sleep(1)
                    st.switch_page("pages/15_Password_Reset_Direct.py")
                else:
                    attempts = get_otp_attempts_remaining(st.session_state.recovery_phone)
                    if attempts > 0:
                        st.error(f"Invalid code. {attempts} attempts remaining.")
                    else:
                        st.error("Too many failed attempts. Please request a new code.")

st.markdown('<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>', unsafe_allow_html=True)