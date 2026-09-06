import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.database import create_tables, reset_password, update_phone_number
from core.auth import restore_session

create_tables()

st.set_page_config(page_title="Reset Password — PD-HAND", layout="wide", initial_sidebar_state="collapsed")

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

/* PASSWORD INPUT */
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

/* VALIDATION CHECKLIST */
.validation-box {
    background: #f5f5f5;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    margin-top: 16px;
}

.validation-item {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    font-size: 14px;
    color: #999;
}

.validation-item:last-child {
    margin-bottom: 0;
}

.validation-checkbox {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    background: #e8e8e8;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 12px;
    font-weight: 700;
}

.validation-checkbox.checked {
    background: #2E7D32;
    color: white;
}

/* BUTTON */
div.stFormSubmitButton > button {
    width:100% !important;
    padding:14px 0 !important;
    font-size:16px !important;
    font-weight:700 !important;
    border-radius:10px !important;
    border:none !important;
    cursor:pointer !important;
    transition:all 0.3s !important;
    background:linear-gradient(135deg,#2E7D32,#43A047) !important;
    color:white !important;
    box-shadow:0 4px 16px rgba(46,125,50,0.3) !important;
    margin-top:24px !important;
}

div.stFormSubmitButton > button:hover {
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

.back-login-link {
    text-align: center;
    margin-top: 20px;
}

.back-login-link a {
    color: #666;
    text-decoration: none;
    font-size: 14px;
}

.back-login-link a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# Check if user has verified OTP
if not st.session_state.get("otp_verified"):
    st.switch_page("pages/14_Password_OTP.py")

# Initialize validation state
if "password_strength" not in st.session_state:
    st.session_state.password_strength = {
        "length": False,
        "number": False,
        "letter": False,
        "match": False
    }

col1, col2, col3 = st.columns([1, 1.2, 1])

with col2:
    # Header (only show in full view, hidden in Image 2)
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

    # Progress Indicator (only show in full view, hidden in Image 2)
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
                <div class="step-number completed">✓</div>
                <div class="step-label">New Phone</div>
            </div>
            <div class="progress-step">
                <div class="step-number completed">✓</div>
                <div class="step-label">Verify OTP</div>
            </div>
            <div class="progress-step">
                <div class="step-number active">5</div>
                <div class="step-label">New Password</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Main Card
    st.markdown("""
        <div class="recovery-card">
            <h2>Create a new password</h2>
            <p>Choose a strong password you'll remember. You'll use this to sign in next time.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("reset_password_form"):
        # New Password
        new_password = st.text_input(
            "New password",
            type="password",
            placeholder="At least 8 characters",
            key="new_password",
            label_visibility="visible"
        )

        # Confirm Password
        confirm_password = st.text_input(
            "Confirm new password",
            type="password",
            placeholder="Re-enter password",
            key="confirm_password",
            label_visibility="visible"
        )

        # Real-time validation
        if new_password or confirm_password:
            has_length = len(new_password) >= 8
            has_number = any(c.isdigit() for c in new_password)
            has_letter = any(c.isalpha() for c in new_password)
            passwords_match = new_password == confirm_password and len(new_password) > 0

            st.session_state.password_strength = {
                "length": has_length,
                "number": has_number,
                "letter": has_letter,
                "match": passwords_match
            }

            # Validation Checklist
            st.markdown("""<div class="validation-box">""", unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="validation-item">
                    <div class="validation-checkbox {'checked' if st.session_state.password_strength['length'] else ''}">
                        {'✓' if st.session_state.password_strength['length'] else ''}
                    </div>
                    <span>At least 8 characters</span>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="validation-item">
                    <div class="validation-checkbox {'checked' if st.session_state.password_strength['number'] else ''}">
                        {'✓' if st.session_state.password_strength['number'] else ''}
                    </div>
                    <span>Contains a number</span>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="validation-item">
                    <div class="validation-checkbox {'checked' if st.session_state.password_strength['letter'] else ''}">
                        {'✓' if st.session_state.password_strength['letter'] else ''}
                    </div>
                    <span>Contains a letter</span>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="validation-item">
                    <div class="validation-checkbox {'checked' if st.session_state.password_strength['match'] else ''}">
                        {'✓' if st.session_state.password_strength['match'] else ''}
                    </div>
                    <span>Passwords match</span>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""</div>""", unsafe_allow_html=True)

        submitted = st.form_submit_button("Reset password", use_container_width=True)

        if submitted:
            # Validate all requirements
            if not all(st.session_state.password_strength.values()):
                st.error("Please meet all password requirements before proceeding.")
            else:
                # Get phone from session
                recovery_phone = st.session_state.get("recovery_phone")
                new_phone = st.session_state.get("new_phone")
                
                if recovery_phone and new_phone:
                    # Update phone number
                    if update_phone_number(recovery_phone, new_phone):
                        # Reset password
                        if reset_password(new_phone, new_password):
                            st.success("Password reset successfully! Redirecting to login...")
                            # Clear session
                            st.session_state.recovery_phone = None
                            st.session_state.new_phone = None
                            st.session_state.otp_verified = False
                            st.session_state.recovery_verified = False
                            
                            import time
                            time.sleep(2)
                            st.switch_page("pages/2_Login.py")
                        else:
                            st.error("Failed to reset password. Please try again.")
                    else:
                        st.error("Failed to update phone number. Please try again.")
                else:
                    st.error("Session expired. Please start over.")

    st.markdown("""
        <div class="back-login-link">
            <a href="/Login">← Back to login</a>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>', unsafe_allow_html=True)