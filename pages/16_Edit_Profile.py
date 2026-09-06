import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.database import create_tables, get_user_by_phone, hash_password, hash_security_answer, update_phone_number, reset_password, get_security_questions, verify_security_answers, get_connection
from core.auth import restore_session

create_tables()

st.set_page_config(page_title="Edit Profile — PD-HAND", layout="wide", initial_sidebar_state="collapsed")

# ─── HANDLE LOGOUT & QUERY PARAMS ─────────────────────────────────
go = st.query_params.get("go", None)
if go == "logout":
    st.session_state.clear()
    st.query_params.clear()
    st.switch_page("app.py")
    st.stop()

# ─── AUTH WITH QUERY PARAMS FALLBACK ──────────────────────────────
if not st.session_state.get("authenticated"):
    uid = st.query_params.get("uid", None)
    uname = st.query_params.get("uname", None)
    if uid and uname:
        try:
            st.session_state["authenticated"] = True
            st.session_state["user_id"] = int(uid)
            st.session_state["user_name"] = str(uname)
        except (ValueError, TypeError):
            st.switch_page("app.py")
            st.stop()

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")
    st.stop()

# ─── GET USER INFO FOR NAVBAR ─────────────────────────────────────
user_id = st.session_state.get("user_id", "")
user_name = st.session_state.get("user_name", "User")
initials = "".join([w[0].upper() for w in user_name.split()[:2]]) or "U"

restore_session()
if not st.session_state.get("authenticated"):
    st.switch_page("app.py")
    st.stop()

# ── Page styling ───────────────────────────────────────────────────────────────
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

.nav-links {{
    display:flex;
    gap:28px;
    align-items:center;
}}

.nav-link-btn {{
    font-size:14px;
    font-weight:500;
    color:#555;
    text-decoration:none;
    display:flex;
    align-items:center;
    gap:5px;
    transition:color 0.2s;
}}

.nav-link-btn:hover {{ color:var(--primary); }}
.nav-link-btn.active {{ color:var(--primary); font-weight:700; }}

.nav-right {{
    display:flex;
    align-items:center;
    gap:14px;
}}

.user-avatar {{
    width:38px;
    height:38px;
    border-radius:50%;
    background:linear-gradient(135deg,var(--primary),var(--primary-light));
    color:white;
    font-size:14px;
    font-weight:700;
    display:flex;
    align-items:center;
    justify-content:center;
    box-shadow:0 2px 8px rgba(46,125,50,0.3);
}}

.logout-btn {{
    font-size:14px;
    font-weight:500;
    color:#333;
    background:white;
    border:1px solid #ddd;
    border-radius:999px;
    padding:7px 14px;
    text-decoration:none;
    transition:all 0.2s;
}}

.logout-btn:hover {{ color:var(--primary); border-color:var(--primary); }}

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

/* TEXT INPUTS */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {{
    border: 1.5px solid #e0e0e0 !important; border-radius: 10px !important;
    font-size: 14px !important; color: #333 !important; background: white !important;
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

/* SELECTBOX */
div[data-testid="stSelectbox"] {{
    margin-bottom: 16px !important;
}}
div[data-testid="stSelectbox"] label p {{
    font-size: 13px !important; font-weight: 600 !important; color: #333 !important;
}}

/* Security question dropdown */
div[data-testid="stSelectbox"] > div {{
    background: #f5f5f5 !important;
    border-radius: 10px !important;
}}

div[data-baseweb="select"] > div {{
    background: #f5f5f5 !important;
    border: 1.5px solid #e0e0e0 !important;
    border-radius: 10px !important;
}}

/* DISABLED FIELDS (view-only) */
/* Disabled fields (iPad fix) */
div[data-testid="stTextInput"] input:disabled {{
    background-color: #E8F5E9 !important;
    color: #2E7D32 !important;
    -webkit-text-fill-color: #2E7D32 !important;
    opacity: 1 !important;
    cursor: not-allowed !important;
}}

/* Remove "Press Enter to submit form" helper text */
div[data-testid="InputInstructions"] {{
    display: none !important;
}}

/* SUBMIT BUTTON */
div.stFormSubmitButton > button {{
    width: 100% !important;
    background: {btn_bg} !important;
    color: {btn_color} !important;
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
div.stFormSubmitButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(46,125,50,0.4) !important;
    filter: brightness(1.08) !important;
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
.step-subtitle {{ font-size: 13px; color: #999; margin-top: 4px; }}

/* PROFILE AVATAR */
.profile-avatar {{
    width: 80px; height: 80px; border-radius: 50%;
    background: linear-gradient(135deg, #2E7D32, #43A047);
    display: flex; align-items: center; justify-content: center;
    font-size: 32px; color: white; margin: 0 auto 16px;
    box-shadow: 0 4px 16px rgba(46,125,50,0.35);
}}

/* BUTTON CONTAINER */
.button-container {{
    display: flex; gap: 12px; justify-content: center; margin-top: 32px;
}}
.btn-secondary {{
    padding: 12px 24px; border-radius: 10px;
    border: 1.5px solid #ddd; background: white;
    color: #333; font-weight: 600; cursor: pointer;
    transition: all 0.3s;
}}
.btn-secondary:hover {{
    border-color: #2E7D32; color: #2E7D32;
}}

/* FOOTER */
.footer {{
    text-align: center; font-size: 13px; color: white;
    font-weight: 500; padding: 20px 48px 32px; background: #2E7D32;
}}

/* INFO TAG */
.info-tag {{
    display: inline-block; background: #e3f2fd; color: #1976d2;
    padding: 2px 8px; border-radius: 4px; font-size: 11px;
    font-weight: 600; margin-left: 8px;
}}
</style>

<div class="navbar">
    <div class="nav-logo">
        <div class="logo-icon-wrap">
            <div class="logo-pulse-ring"></div>
            <div class="logo-icon">👋</div>
        </div>
        <div>
            <div class="logo-name">PD-HAND</div>
            <div class="logo-sub">FCSIT · UNIMAS</div>
        </div>
    </div>
    <div class="nav-links">
        <a class="nav-link-btn" href="/Home?uid={user_id}&uname={user_name}" target="_self">🏠 Home</a>
        <a class="nav-link-btn" href="/Screening?uid={user_id}&uname={user_name}" target="_self">🔍 Screening</a>
        <a class="nav-link-btn" href="/History?uid={user_id}&uname={user_name}" target="_self">🕒 History</a>
    </div>
    <div class="nav-right">
        <div class="user-avatar">{initials}</div>
        <a class="logout-btn" href="?go=logout&uid={user_id}&uname={user_name}" target="_self">→ Log out</a>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2.2, 1])
with col2:

    user_id = st.session_state.get("user_id")
    user_name = st.session_state.get("user_name")
    user_phone = st.session_state.get("user_phone")
    
    # Fallback: if user_phone not in session, get from query params
    if not user_phone:
        user_phone = st.query_params.get("phone", "")
    
    # Last fallback: if still empty, get from database using user_id
    if not user_phone and user_id:
        user_data = get_user_by_phone(user_phone) if user_phone else None
        if not user_data:
            # Query by user_id instead
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT phone FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                user_phone = row[0]

    # Get user profile data
    user_profile = get_user_by_phone(user_phone)
    
    # Get user's BOTH security questions with answers
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, question, answer FROM security_questions WHERE user_id = ?",
        (user_id,)
    )
    security_qs_rows = cursor.fetchall()
    conn.close()
    
    security_qs = [{"id": row[0], "question": row[1], "answer": row[2]} for row in security_qs_rows]

    st.markdown("""
        <div style="text-align:center; padding:36px 0 24px 0;">
            <div class="profile-avatar">👤</div>
            <div style="font-size:28px;font-weight:800;color:#1a1a1a;margin-bottom:6px;">
                Edit Profile
            </div>
            <div style="font-size:14px;color:#777;">
                Keep your account details up to date so we can tailor your handwriting screening.
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("edit_profile_form"):

        # ── STEP 1: PERSONAL INFORMATION ───────────────────────────────────────
        st.markdown("""
        <div class="step-card"><div class="step-header">
            <div class="step-badge">👤</div>
            <div><div class="step-label">STEP 1</div><div class="step-title-text">Personal information</div></div>
        </div></div>""", unsafe_allow_html=True)

        full_name = st.text_input("Full Name", value=user_name if user_name else "", placeholder="Your full name")
        
        # Phone number: show old in grey, allow change in new field
        st.text_input("Current Phone Number", value=user_phone if user_phone else "", disabled=True, 
                     help="This is your registered phone number")
        phone = st.text_input("Change Phone Number (Optional)", value="", placeholder="Enter new phone number if you want to change it")

        # ── STEP 2: SECURITY QUESTIONS (BOTH) ──────────────────────────────────
        st.markdown("""
        <div class="step-card"><div class="step-header">
            <div class="step-badge">🔒</div>
            <div><div class="step-label">STEP 2</div><div class="step-title-text">Security questions</div></div>
        </div></div>""", unsafe_allow_html=True)

        security_questions_list = [
            "What is the name of the town or city you were born?",
            "In what year you were born?",
            "What is the name of the neighborhood where you grew up?",
            "What was your first job?",
            "What is your favorite colour?"
        ]

        # QUESTION 1
        security_questions_list_q1 = security_questions_list

        if security_qs and len(security_qs) > 0:
            current_sq1 = security_qs[0]["question"]

            try:
                sq1_index = security_questions_list.index(current_sq1)
            except ValueError:
                security_questions_list_q1 = [current_sq1] + security_questions_list
                sq1_index = 0
        else:
            sq1_index = 0

        sq1 = st.selectbox("Security Question 1", security_questions_list_q1, index=sq1_index, key="sq1_select")
        sa1 = st.text_input("Security Answer 1", placeholder="Your answer", key="sa1_input")

        # QUESTION 2
        security_questions_list_q2 = security_questions_list

        if security_qs and len(security_qs) > 1:
            current_sq2 = security_qs[1]["question"]

            try:
                sq2_index = security_questions_list.index(current_sq2)
            except ValueError:
                security_questions_list_q2 = [current_sq2] + security_questions_list
                sq2_index = 0
        else:
            sq2_index = 1

        sq2 = st.selectbox("Security Question 2", security_questions_list_q2, index=sq2_index, key="sq2_select")
        sa2 = st.text_input("Security Answer 2", placeholder="Your answer", key="sa2_input")

        # ── STEP 3: CHANGE PASSWORD ───────────────────────────────────────────
        st.markdown("""
        <div class="step-card"><div class="step-header">
            <div class="step-badge">🔐</div>
            <div><div class="step-label">STEP 3</div><div class="step-title-text">Change password</div>
            <div class="step-subtitle">Optional — leave blank to keep your current password</div></div>
        </div></div>""", unsafe_allow_html=True)

        current_pwd = st.text_input("Current Password", type="password", placeholder="Enter current password")
        new_pwd = st.text_input("New Password", type="password", placeholder="At least 6 characters")
        confirm_pwd = st.text_input("Confirm New Password", type="password", placeholder="Re-enter new password")

        col_left, col_right = st.columns(2)
        with col_left:
            cancel_btn = st.form_submit_button("Cancel", use_container_width=True)
        with col_right:
            submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

        if submitted:
            # Validate inputs - make everything optional except what's being changed
            errors = []

            # Full name - optional, only validate if provided
            if full_name and len(full_name.strip()) == 0:
                errors.append("Full name cannot be empty if provided.")

            # Phone number - optional, only validate if provided
            if phone and phone.strip():
                if len(phone) < 9:
                    errors.append("Please enter a valid phone number.")
            
            # Security answers - optional, can change one or both
            has_sa1 = sa1 and len(sa1.strip()) > 0
            has_sa2 = sa2 and len(sa2.strip()) > 0

            # Password change - optional, but if ONE field is filled, verify current password
            has_new_pwd = new_pwd and len(new_pwd.strip()) > 0
            has_confirm_pwd = confirm_pwd and len(confirm_pwd.strip()) > 0
            
            if has_new_pwd or has_confirm_pwd:
                if not current_pwd:
                    errors.append("Please enter your current password to change it.")
                elif len(new_pwd) < 6:
                    errors.append("New password must be at least 6 characters.")
                elif new_pwd != confirm_pwd:
                    errors.append("New passwords do not match.")
                else:
                    # Verify current password
                    from core.database import verify_user
                    verify_result = verify_user(user_phone, current_pwd)
                    if not verify_result:
                        errors.append("Current password is incorrect.")
            
            # Check if user is actually changing something
            is_changing_name = full_name and full_name.strip() != user_name
            is_changing_phone = phone and phone.strip() and phone.strip() != user_phone
            is_changing_security = has_sa1 or has_sa2
            is_changing_password = has_new_pwd and has_confirm_pwd
            
            if not (is_changing_name or is_changing_phone or is_changing_security or is_changing_password):
                errors.append("Please make at least one change to update your profile.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    # Update full name if changed
                    if is_changing_name:
                        cursor.execute(
                            "UPDATE users SET name = ? WHERE id = ?",
                            (full_name.strip(), user_id)
                        )
                        st.session_state.user_name = full_name.strip()
                    
                    # Update phone number if changed
                    if is_changing_phone:
                        phone_updated = update_phone_number(user_phone, phone.strip())
                        if not phone_updated:
                            st.error("Phone number already exists. Please use a different number.")
                            conn.close()
                        else:
                            st.session_state.user_phone = phone.strip()
                    
                    # Update security questions - now independently
                    if has_sa1:
                        if security_qs and len(security_qs) > 0:
                            cursor.execute(
                                "UPDATE security_questions SET question = ?, answer = ? WHERE user_id = ? AND id = ?",
                                (sq1, hash_security_answer(sa1), user_id, security_qs[0]["id"])
                            )
                        else:
                            cursor.execute(
                                "INSERT INTO security_questions (user_id, question, answer) VALUES (?, ?, ?)",
                                (user_id, sq1, hash_security_answer(sa1))
                            )
                    
                    if has_sa2:
                        if security_qs and len(security_qs) > 1:
                            cursor.execute(
                                "UPDATE security_questions SET question = ?, answer = ? WHERE user_id = ? AND id = ?",
                                (sq2, hash_security_answer(sa2), user_id, security_qs[1]["id"])
                            )
                        else:
                            cursor.execute(
                                "INSERT INTO security_questions (user_id, question, answer) VALUES (?, ?, ?)",
                                (user_id, sq2, hash_security_answer(sa2))
                            )
                    
                    # Update password if changed
                    if is_changing_password:
                        cursor.execute(
                            "UPDATE users SET password = ? WHERE id = ?",
                            (hash_password(new_pwd), user_id)
                        )
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ Profile updated successfully!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Error updating profile: {str(e)}")

        elif cancel_btn:
            st.query_params["uid"] = str(user_id)
            st.query_params["uname"] = user_name
            st.switch_page("pages/3_Home.py")

st.markdown('<div class="footer">For research and educational use. Not a substitute for professional medical advice.</div>', unsafe_allow_html=True)