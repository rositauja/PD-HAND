import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.database import create_tables, get_security_questions, verify_security_answers
from core.auth import restore_session

create_tables()

st.set_page_config(page_title="Security Questions — PD-HAND", layout="wide", initial_sidebar_state="collapsed")

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
            
.stApp {
    background:linear-gradient(135deg,#f0faf3 0%,#d4edda 50%,#c8e6c9 100%) !important;
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

/* QUESTION CARD */
.question-card {
    background: #f8faf9;
    border: 1.5px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
}

.question-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}

.question-icon {
    width: 28px;
    height: 28px;
    background: #2E7D32;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 16px;
    flex-shrink: 0;
}

.question-text {
    font-size: 15px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0;
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

div[data-testid="stTextInput"] input::placeholder {
    font-size:14px !important;
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
button[kind="secondaryFormSubmit"] {
    background:#f7f7f7 !important;
    color:#000000 !important;
    border:1px solid #e5e5e5 !important;
    box-shadow:none !important;
}

button[kind="secondaryFormSubmit"]:hover {
    background:#ffffff !important;
    color:#2E7D32 !important;
    border:1px solid #2E7D32 !important;
    box-shadow:none !important;
}

/* CONTINUE BUTTON */
button[kind="primaryFormSubmit"] {
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

.back-login {
    text-align: center;
    margin-top: 20px;
    font-size: 14px;
}

.back-login a {
    color: white;
    text-decoration: none;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# Check if user has phone number in session
if not st.session_state.get("recovery_phone"):
    st.switch_page("pages/11_Password.py")

# Initialize session state
if "sec_a1" not in st.session_state:
    st.session_state.sec_a1 = ""
if "sec_a2" not in st.session_state:
    st.session_state.sec_a2 = ""

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
                <div class="step-number active">2</div>
                <div class="step-label">Security</div>
            </div>
            <div class="progress-step">
                <div class="step-number">3</div>
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
            <h2>Verify your identity</h2>
            <p>Please answer the security questions you set up when you created your account.</p>
        </div>
    """, unsafe_allow_html=True)

    # Get security questions from database
    phone = st.session_state.recovery_phone
    questions = get_security_questions(phone)

    if not questions or len(questions) < 2:
        st.error("Security questions not found. Please contact support.")
    else:
        with st.form("security_form"):
            # Question 1
            st.markdown(f"""
                <div class="question-card">
                    <div class="question-header">
                        <div class="question-icon">🔒</div>
                        <div class="question-text">Question 1: {questions[0]['question']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            answer1 = st.text_input(
                "Your answer",
                placeholder="Your answer",
                key="sec_a1",
                label_visibility="collapsed"
            )

            # Question 2
            st.markdown(f"""
                <div class="question-card">
                    <div class="question-header">
                        <div class="question-icon">🔒</div>
                        <div class="question-text">Question 2: {questions[1]['question']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            answer2 = st.text_input(
                "Your answer",
                placeholder="Your answer",
                key="sec_a2",
                label_visibility="collapsed"
            )

            # Buttons
            col_back, col_continue = st.columns([1, 1])
            
            with col_back:
                back_clicked = st.form_submit_button(
                    "← Back",
                    use_container_width=True,
                    type="secondary"
                )

            with col_continue:
                continue_clicked = st.form_submit_button(
                    "Continue →",
                    use_container_width=True,
                    type="primary"
                )

            if back_clicked:
                st.switch_page("pages/11_Password.py")

            if continue_clicked:
                if not answer1 or not answer2:
                    st.error("Please answer both security questions.")
                else:
                    # Verify answers
                    answers_dict = {"a1": answer1, "a2": answer2}
                    if verify_security_answers(phone, answers_dict):
                        st.success("Identity verified! Proceeding to next step...")
                        st.session_state.recovery_verified = True
                        st.switch_page("pages/13_Password_NewPhone.py")
                    else:
                        st.error("Your answers are incorrect. Please try again.")

    st.markdown("""
        <div style="text-align: center; margin-top: 40px;">
            <a href="/Login" style="color: white; text-decoration: none; font-size: 14px; font-weight: 500;">← Back to login</a>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>', unsafe_allow_html=True)