import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import cv2
import numpy as np
import datetime
import random
from PIL import Image

from core.database import create_tables, save_screening, get_user_profile
from core.input_validator import is_valid_handwriting
from core.preprocess import preprocess_spiral, preprocess_meander
from core.features import extract_spiral_features, extract_meander_features
from core.predict import predict_spiral, predict_meander, predict_draw
from core.validation import show_loading
from core.auth import require_auth

create_tables()
st.set_page_config(page_title="PD-HAND | Screening", layout="wide")

# ═══════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════

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

user_id = st.session_state.get("user_id", "")
user_name = st.session_state.get("user_name", "User")
user_phone = st.session_state.get("user_phone", "")
initials = "".join([w[0].upper() for w in user_name.split()[:2]]) or "U"

# ═══════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATIC_DIR = os.path.join(BASE_DIR, "static")
SPIRAL_GUIDE = os.path.join(STATIC_DIR, "spiral_guide.png")
MEANDER_GUIDE = os.path.join(STATIC_DIR, "meander_guide.png")
SPIRAL_PDF_TEMPLATE = os.path.join(STATIC_DIR, "spiral_template.pdf")
MEANDER_PDF_TEMPLATE = os.path.join(STATIC_DIR, "meander_template.pdf")

# ═══════════════════════════════════════════════════════════════════
# STYLING (SIMPLIFIED)
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stDecoration"] { display: none; }
header { display: none !important; }
footer { display: none !important; }

:root {
    --primary: #2E7D32;
    --primary-light: #43A047;
    --primary-glow: #66BB6A;
    --border-light: #c8e6c9;
}

@keyframes heartbeat { 0%,100%{transform:scale(1)} 15%{transform:scale(1.18)} 30%{transform:scale(1)} 45%{transform:scale(1.10)} 60%{transform:scale(1)} }
@keyframes pulse-ring { 0%{transform:scale(0.85);opacity:0.6} 100%{transform:scale(2.0);opacity:0} }

.navbar {
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:16px 48px;
    border-bottom:1px solid var(--border-light);
    background:rgba(255,255,255,0.97);
    position:sticky;
    top:0;
    z-index:100;

    margin-top:-1rem;
    margin-left:-48px;
    margin-right:-48px;
    margin-bottom:0;
}

.nav-logo {
    display:flex;
    align-items:center;
    gap:12px;
}

.logo-icon-wrap {
    position:relative;
    width:44px;
    height:44px;
}

.logo-pulse-ring {
    position:absolute;
    inset:0;
    border-radius:50%;
    background:var(--primary-glow);
    opacity:0.5;
    animation:pulse-ring 2s ease-out infinite;
}

.logo-icon {
    position:relative;
    width:44px;
    height:44px;
    background:linear-gradient(135deg,var(--primary),var(--primary-light));
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
    animation:heartbeat 1.8s ease-in-out infinite;
    box-shadow:0 4px 16px rgba(46,125,50,0.35);
    z-index:1;
}

.logo-name { font-size:17px; font-weight:800; color:#1b5e20; letter-spacing:-0.3px; }
.logo-sub { font-size:10px; font-weight:500; color:#2e6b3e; letter-spacing:0.5px; }

.nav-links {
    display:flex;
    gap:28px;
    align-items:center;
}

.nav-link-btn {
    font-size:14px;
    font-weight:500;
    color:#555;
    text-decoration:none;
    display:flex;
    align-items:center;
    gap:5px;
    transition:color 0.2s;
}

.nav-link-btn:hover { color:var(--primary); }
.nav-link-btn.active { color:var(--primary); font-weight:700; }

.nav-right {
    display:flex;
    align-items:center;
    gap:14px;
}

.user-avatar {
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
    transition:transform 0.2s, box-shadow 0.2s;
    cursor:pointer;
}

.user-avatar:hover {
    transform:scale(1.08);
    box-shadow:0 4px 12px rgba(46,125,50,0.4);
}

.logout-btn {
    font-size:14px;
    font-weight:500;
    color:#333;
    background:white;
    border:1px solid #ddd;
    border-radius:999px;
    padding:7px 14px;
    text-decoration:none;
    transition:all 0.2s;
}

.logout-btn:hover { color:var(--primary); border-color:var(--primary); }

.stApp {
    background:#f7f7f7 !important;
}
            
.hero-banner {
    background:linear-gradient(135deg,#d4edda,#c8e6c9);
    border-radius:18px;
    padding:42px 28px;
    text-align:center;
    margin:20px 0 28px 0;
}

.hero-banner h1 { font-size:34px; font-weight:800; color:#1b5e20; margin:0 0 10px 0; }
.hero-banner p { font-size:15px; color:#4a7c59; margin:0; line-height:1.65; }

.tip-card {
    background:#f0faf3;
    border:1px solid var(--border-light);
    border-radius:14px;
    padding:18px 20px;
    margin-bottom:16px;
}

.tip-card-title { font-size:13px; font-weight:800; color:#2E7D32; margin-bottom:10px; }
.tip-card ul { margin:0; padding-left:20px; font-size:14px; color:#444; line-height:1.9; }

.choice-card {
    border-radius:16px;
    padding:20px 12px;
    text-align:center;
    cursor:pointer;
    text-decoration:none;
    display:block;
    transition:all 0.2s;
}

.choice-card:hover { transform:translateY(-2px); }

.device-notice {
    background-color:#FFF8E1;
    border:1px solid #FFE082;
    border-radius:12px;
    padding:12px 14px;
    font-size:13px;
    color:#5D4037;
    margin-bottom:14px;
    display:flex;
    gap:8px;
}

.result-card {
    border-radius:16px;
    overflow:hidden;
    box-shadow:0 2px 12px rgba(0,0,0,0.08);
    margin-bottom:20px;
}

.card-header {
    background:linear-gradient(135deg,#66BB6A,#43A047);
    padding:16px 20px;
    display:flex;
    justify-content:flex-start;
    color:white;
}

/* Secondary buttons (untouched tab) */
div[data-testid="stButton"] button[kind="secondary"] {
    background:#eeeeee !important;
    color:#444 !important;
    border:1px solid #d6d6d6 !important;
}

div[data-testid="stButton"] button[kind="secondary"]:hover {
    background:#e5e5e5 !important;
    border-color:#c8c8c8 !important;
    color:#222 !important;
}

.card-header-left h2 { margin:0; font-size:18px; font-weight:700; }
.card-header-left p { margin:4px 0 0 0; font-size:13px; opacity:0.9; }
.card-header-right { text-align:right; font-size:13px; }

.card-body { padding:24px 20px; background-color:#f9fdf9; }
.score-section { display:flex; align-items:center; justify-content:center; gap:30px; margin-bottom:20px; }

.badge-high { background-color:#FFF3E0; color:#E65100; border:1.5px solid #FFB74D; border-radius:20px; padding:8px 18px; font-size:15px; font-weight:600; display:inline-flex; align-items:center; gap:6px; }
.badge-low { background-color:#E8F5E9; color:#2E7D32; border:1.5px solid #81C784; border-radius:20px; padding:8px 18px; font-size:15px; font-weight:600; display:inline-flex; align-items:center; gap:6px; }

.indicator-box { background:white; border-radius:10px; padding:14px 16px; margin-top:4px; border:1px solid #e0e0e0; }
.indicator-title { font-weight:600; font-size:14px; margin-bottom:6px; display:flex; align-items:center; gap:6px; }
.indicator-text { font-size:13px; color:#555; margin:0; }

.disclaimer-box { background-color:#F5F5F5; border-radius:10px; padding:14px 16px; font-size:13px; color:#555; margin-top:16px; display:flex; gap:10px; }

div[data-testid="stMainBlockContainer"] { padding: 0 48px 40px 48px !important; }
            
/* FIX OUTER WHITE PADDING AROUND DRAWING CANVAS */
iframe {
    width: 620px !important;
    max-width: 620px !important;
    min-width: 620px !important;

    height: 280px !important;
    max-height: 280px !important;

    display: block !important;
    margin: 0 !important;

    border: none !important;
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# NAVBAR
# ═══════════════════════════════════════════════════════════════════

st.markdown(f"""
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
        <a class="nav-link-btn active" href="?go=screening&uid={user_id}&uname={user_name}" target="_self">🔍 Screening</a>
        <a class="nav-link-btn" href="/History?uid={user_id}&uname={user_name}" target="_self">🕒 History</a>
    </div>
    <div class="nav-right">
        <a href="?go=edit_profile&uid={user_id}&uname={user_name}&phone={user_phone}" target="_self" style="text-decoration:none;">
            <div class="user-avatar">{initials}</div>
        </a>
        <a class="logout-btn" href="?go=logout&uid={user_id}&uname={user_name}" target="_self">→ Log out</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════

if "result" not in st.session_state: st.session_state.result = None
if "input_tab" not in st.session_state: st.session_state.input_tab = "Draw"
if "upload_method" not in st.session_state: st.session_state.upload_method = None
if "draw_type" not in st.session_state: st.session_state.draw_type = None
if "upload_key" not in st.session_state: st.session_state.upload_key = 0
if "upload_pattern" not in st.session_state: st.session_state.upload_pattern = None

selected_method = st.query_params.get("method", None)
selected_type = st.query_params.get("draw_type", None)
selected_upload_pattern = st.query_params.get("upload_pattern", None)

if selected_method and st.session_state.upload_method != selected_method:
    st.session_state.upload_method = selected_method
    st.session_state.input_tab = "Upload"
    st.rerun()

if selected_type and st.session_state.draw_type != selected_type:
    st.session_state.draw_type = selected_type
    st.session_state.input_tab = "Draw"
    st.rerun()

if selected_upload_pattern and st.session_state.upload_pattern != selected_upload_pattern:
    st.session_state.upload_pattern = selected_upload_pattern
    st.session_state.input_tab = "Upload"
    st.rerun()

# ═══════════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero-banner">
    <h1>Handwriting Screening</h1>
    <p>Provide a handwriting sample for AI-powered analysis.<br>
       You can draw directly or upload a photo of your handwriting.</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════

if st.session_state.result is None:
    left_col, right_col = st.columns([0.9, 1.7], gap="large")

    with left_col:
        st.markdown("""
        <div class="tip-card">
            <div class="tip-card-title">🌀 Spiral Drawing Tips</div>
            <ul>
                <li>Trace over the spiral guideline</li>
                <li>Keep spacing consistent</li>
                <li>Draw naturally without rushing</li>
                <li>Use consistent pressure</li>
            </ul>
        </div>
        <div class="tip-card">
            <div class="tip-card-title">〰️ Meander Drawing Tips</div>
            <ul>
                <li>Trace over the guideline</li>
                <li>Keep lines straight and even</li>
                <li>Draw without lifting the pen</li>
                <li>Use consistent pressure</li>
            </ul>
        </div>
        <div class="tip-card">
            <div class="tip-card-title">📷 Upload Tips</div>
            <ul>
                <li>Use high-contrast images</li>
                <li>Plain white paper works best</li>
                <li>Good lighting, no shadows</li>
                <li>Crop to show only the drawing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        tb1, tb2 = st.columns(2)
        with tb1:
            if st.button("✏️ Draw", key="tab_draw", use_container_width=True,
                        type="primary" if st.session_state.input_tab == "Draw" else "secondary"):
                st.session_state.input_tab = "Draw"
                st.session_state.upload_method = None
                st.session_state.upload_pattern = None
                st.query_params.clear()
                st.rerun()

        with tb2:
            if st.button("⬆️ Upload", key="tab_upload", use_container_width=True,
                        type="primary" if st.session_state.input_tab == "Upload" else "secondary"):
                st.session_state.input_tab = "Upload"
                st.session_state.draw_type = None
                st.query_params.clear()
                st.rerun()

        if st.session_state.input_tab == "Draw":
            try:
                from streamlit_drawable_canvas import st_canvas
            except ImportError:
                st.error("⚠️ streamlit-drawable-canvas not installed. Run: pip install streamlit-drawable-canvas")
                st.stop()

            st.markdown('<div class="device-notice"><span>⚠️</span><div><b>For best accuracy</b>, use a stylus-enabled device (iPad with Apple Pencil or touchscreen with stylus).</div></div>', unsafe_allow_html=True)

            st.markdown("<p style='font-size:20px; font-weight:700; color:#444; margin-bottom:10px;'>Step 1: Select pattern</p>", unsafe_allow_html=True)

            spiral_selected = st.session_state.draw_type == "Spiral"
            meander_selected = st.session_state.draw_type == "Meander"

            st.markdown(f"""
            <div style="display:flex; gap:14px; margin-bottom:18px;">
                <a class="choice-card" href="?draw_type=Spiral&uid={user_id}&uname={user_name}" target="_self"
                   style="flex:1; border:2.5px solid {'#43A047' if spiral_selected else '#c8e6c9'}; background:{'#f0faf3' if spiral_selected else 'white'};">
                    <div style="font-size:28px; margin-bottom:8px;">🌀</div>
                    <div style="font-size:14px; font-weight:800; color:#2E7D32;">Spiral</div>
                </a>
                <a class="choice-card" href="?draw_type=Meander&uid={user_id}&uname={user_name}" target="_self"
                   style="flex:1; border:2.5px solid {'#43A047' if meander_selected else '#c8e6c9'}; background:{'#f0faf3' if meander_selected else 'white'};">
                    <div style="font-size:28px; margin-bottom:8px;">〰️</div>
                    <div style="font-size:14px; font-weight:800; color:#2E7D32;">Meander</div>
                </a>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.draw_type:
                st.markdown(f"<p style='font-size:20px; font-weight:700; color:#444; margin-bottom:10px;'>Step 2: Trace over the {st.session_state.draw_type} guideline</p>", unsafe_allow_html=True)

                # Canvas sizing constants - fitted to guideline without extra white space
                CANVAS_WIDTH = 620
                CANVAS_HEIGHT = 280

                try:
                    guide_path = SPIRAL_GUIDE if st.session_state.draw_type == "Spiral" else MEANDER_GUIDE
                    if not os.path.exists(guide_path):
                        st.error(f"❌ Guide not found: {guide_path}")
                        st.stop()
                    bg_image = Image.open(guide_path).convert("RGBA").resize(
                        (CANVAS_WIDTH, CANVAS_HEIGHT)
                    )
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.stop()

                clear_canvas = st.button("✕ Clear", key="clear_canvas")

                try:
                    canvas_result = st_canvas(
                        fill_color="rgba(255,255,255,0)", stroke_width=3, stroke_color="#000000",
                        background_image=bg_image, update_streamlit=True, background_color="#ffffff",
                        height=CANVAS_HEIGHT, width=CANVAS_WIDTH, drawing_mode="freedraw",
                        key="canvas" if not clear_canvas else f"canvas_{random.randint(0,99999)}",
                        display_toolbar=False,
                    )
                except Exception as e:
                    st.error(f"❌ Canvas error: {str(e)}")
                    st.stop()

                _, btn_col = st.columns([1, 1])
                with btn_col:
                    submit_draw = st.button("➤ Submit for Analysis", key="submit_draw", type="primary", use_container_width=True)

                if submit_draw:
                    if canvas_result.image_data is None:
                        st.warning("Please draw something first.")
                    else:
                        img_array = canvas_result.image_data.astype(np.uint8)

                        rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
                        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

                        _, cleaned = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)

                        image = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
                        gray_check = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                        if np.mean(gray_check) >= 254:
                            st.warning("Canvas is empty. Please trace over the guideline.")
                        else:
                            # Set processing state and redirect to validation page
                            st.session_state.is_processing = True
                            st.session_state.processing_stage = 0
                            st.session_state.processing_image = image
                            st.session_state.processing_type = st.session_state.draw_type
                            st.session_state.processing_source = "draw"
                            
                            st.query_params["uid"] = str(user_id)
                            st.query_params["uname"] = user_name
                            st.switch_page("pages/17_Validation.py")
                            st.stop()

        else:  # UPLOAD TAB
            image = None
            
            # ── STEP 1: SELECT PATTERN ──────────────────────────────────────────
            st.markdown("<p style='font-size:20px; font-weight:700; color:#444; margin-bottom:10px;'>Step 1: Select pattern</p>", unsafe_allow_html=True)

            spiral_selected = st.session_state.get("upload_pattern") == "spiral"
            meander_selected = st.session_state.get("upload_pattern") == "meander"

            st.markdown(f"""
            <div style="display:flex; gap:14px; margin-bottom:18px;">
                <a class="choice-card" href="?upload_pattern=spiral&uid={user_id}&uname={user_name}" target="_self"
                   style="flex:1; border:2.5px solid {'#43A047' if spiral_selected else '#c8e6c9'}; background:{'#f0faf3' if spiral_selected else 'white'};">
                    <div style="font-size:28px; margin-bottom:8px;">🌀</div>
                    <div style="font-size:14px; font-weight:800; color:#2E7D32;">Spiral</div>
                </a>
                <a class="choice-card" href="?upload_pattern=meander&uid={user_id}&uname={user_name}" target="_self"
                   style="flex:1; border:2.5px solid {'#43A047' if meander_selected else '#c8e6c9'}; background:{'#f0faf3' if meander_selected else 'white'};">
                    <div style="font-size:28px; margin-bottom:8px;">〰️</div>
                    <div style="font-size:14px; font-weight:800; color:#2E7D32;">Meander</div>
                </a>
            </div>
            """, unsafe_allow_html=True)

            # Only show Steps 2 & 3 after pattern is selected
            if st.session_state.get("upload_pattern"):
                
                # ── STEP 2: PRINT TEMPLATE ──────────────────────────────────────────
                st.markdown("<p style='font-size:20px; font-weight:700; color:#444; margin-bottom:10px;'>Step 2: Print template</p>", unsafe_allow_html=True)
                
                tpl_sel = st.session_state.upload_method == "Template"
                
                st.markdown(f"""
                <div style="display:flex; gap:14px; margin-bottom:18px;">
                    <a class="choice-card" href="?upload_pattern={st.session_state.upload_pattern}&method=Template&uid={user_id}&uname={user_name}" target="_self"
                       style="flex:1; border:2.5px solid {'#43A047' if tpl_sel else '#c8e6c9'}; background:{'#f0faf3' if tpl_sel else 'white'};">
                        <div style="font-size:28px;">🖨️</div>
                        <div style="font-size:14px; font-weight:800; color:#2E7D32;">Print Template</div>
                        <div style="font-size:12px; color:#888; margin-top:4px;">Download & print</div>
                    </a>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.upload_method == "Template":
                    st.markdown("""
                    <div style="background:#f0faf3; border:1px solid #c8e6c9; border-radius:14px; padding:16px; margin-bottom:16px;">
                        <div style="font-size:13px; font-weight:800; color:#2E7D32; margin-bottom:8px;">📋 How to use:</div>
                        <ol style="margin:0; padding-left:18px; font-size:13px; color:#444; line-height:1.85;">
                            <li>Download the PDF template</li>
                            <li>Print on A4 paper</li>
                            <li>Trace over the guideline with a pen</li>
                            <li>Take a clear photo</li>
                            <li>Upload the photo using Upload Image</li>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)

                    # Determine which template to download based on selected pattern
                    selected_pattern = st.session_state.upload_pattern
                    pdf_template_path = SPIRAL_PDF_TEMPLATE if selected_pattern == "spiral" else MEANDER_PDF_TEMPLATE
                    pdf_filename = "PD-HAND_Spiral_Template.pdf" if selected_pattern == "spiral" else "PD-HAND_Meander_Template.pdf"

                    if os.path.exists(pdf_template_path):
                        with open(pdf_template_path, "rb") as pdf_file:
                            st.download_button("⬇️ Download PDF Template", pdf_file.read(),
                                             file_name=pdf_filename, mime="application/pdf",
                                             use_container_width=True)
                    else:
                        st.warning(f"⚠️ Template PDF not found")

                # ── STEP 3: UPLOAD OR TAKE PHOTO ────────────────────────────────────
                st.markdown("<p style='font-size:20px; font-weight:700; color:#444; margin-bottom:10px;'>Step 3: Upload image or take photo</p>", unsafe_allow_html=True)

                file_sel = st.session_state.upload_method == "File"
                cam_sel = st.session_state.upload_method == "Camera"

                st.markdown(f"""
                <div style="display:flex; gap:14px; margin-bottom:18px;">
                    <a class="choice-card" href="?upload_pattern={st.session_state.upload_pattern}&method=File&uid={user_id}&uname={user_name}" target="_self"
                       style="flex:1; border:2.5px solid {'#43A047' if file_sel else '#c8e6c9'}; background:{'#f0faf3' if file_sel else 'white'};">
                        <div style="font-size:28px;">📁</div>
                        <div style="font-size:14px; font-weight:800; color:#2E7D32;">Upload Image</div>
                        <div style="font-size:12px; color:#888; margin-top:4px;">JPG, PNG, BMP</div>
                    </a>
                    <a class="choice-card" href="?upload_pattern={st.session_state.upload_pattern}&method=Camera&uid={user_id}&uname={user_name}" target="_self"
                       style="flex:1; border:2.5px solid {'#43A047' if cam_sel else '#c8e6c9'}; background:{'#f0faf3' if cam_sel else 'white'};">
                        <div style="font-size:28px;">📷</div>
                        <div style="font-size:14px; font-weight:800; color:#2E7D32;">Take Photo</div>
                        <div style="font-size:12px; color:#888; margin-top:4px;">Use camera</div>
                    </a>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.upload_method == "File":
                    col_del, _ = st.columns([1, 3])
                    with col_del:
                        if st.button("🗑️ Clear", key="delete_file"):
                            st.session_state.upload_key += 1
                            st.rerun()

                    uploaded_file = st.file_uploader("Supports JPG, PNG, BMP", type=["png","jpg","jpeg","bmp"],
                                                     key=f"file_uploader_{st.session_state.upload_key}")
                    if uploaded_file:
                        try:
                            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                            if image is not None:
                                st.image(image, channels="BGR", caption="Uploaded image", width=430)
                            else:
                                st.error("❌ Cannot read this file.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

                elif st.session_state.upload_method == "Camera":
                    camera_photo = st.camera_input("Point camera at drawing and capture", key="camera_input")
                    if camera_photo:
                        try:
                            file_bytes = np.asarray(bytearray(camera_photo.read()), dtype=np.uint8)
                            cam_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                            if cam_image is not None:
                                image = cam_image
                            else:
                                st.error("❌ Could not read the photo.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

                if st.session_state.upload_method in ["File", "Camera"]:
                    _, btn_col = st.columns([1, 1])
                    with btn_col:
                        submit_upload = st.button("➤ Submit for Analysis", key="submit_upload", type="primary", use_container_width=True)

                    if submit_upload:
                        if image is None:
                            st.warning("Please upload or take a photo first.")
                        else:
                            # Set processing state and redirect to validation page
                            st.session_state.is_processing = True
                            st.session_state.processing_stage = 0
                            st.session_state.processing_image = image
                            st.session_state.processing_type = st.session_state.upload_pattern.capitalize()
                            st.session_state.processing_source = "upload"

                            st.query_params["uid"] = str(user_id)
                            st.query_params["uname"] = user_name
                            st.switch_page("pages/17_Validation.py")
                            st.stop()

# ═══════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════

if st.session_state.result is not None:
    label, confidence, detected_type, screening_id, date_line, time_line, features = st.session_state.result
    confidence_pct = int(confidence * 100)

    if label == "Low Likelihood":
        badge_class = "badge-low"
        badge_icon = "✅"
        indicator_icon = "✅"
        indicator_color = "#2E7D32"
        message_title = "Low Indicators Detected"
        message_text = "Analysis did not identify concerning patterns. For screening purposes only."
        arc_color = "#66BB6A"
    else:
        badge_class = "badge-high"
        badge_icon = "🔴"
        indicator_icon = "🔴"
        indicator_color = "#C62828"
        message_title = "Elevated Indicators Detected"
        message_text = "Analysis detected concerning patterns. Consult with a healthcare professional."
        arc_color = "#EF5350"

    radius = 36
    circumference = 2 * 3.14159 * radius
    dash = (confidence_pct / 100) * circumference
    gap = circumference - dash
    offset = circumference * 0.25

    svg = f'<svg width="90" height="90" viewBox="0 0 90 90"><circle cx="45" cy="45" r="{radius}" fill="none" stroke="#e0e0e0" stroke-width="7"/><circle cx="45" cy="45" r="{radius}" fill="none" stroke="{arc_color}" stroke-width="7" stroke-dasharray="{round(dash,1)} {round(gap,1)}" stroke-dashoffset="{round(offset,1)}" stroke-linecap="round"/><text x="45" y="50" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">{confidence_pct}%</text></svg>'

    st.markdown("<h2 style='text-align:center; font-weight:800;'>Screening Complete</h2>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="result-card">
        <div class="card-header" style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div class="card-header-left">
                <h2>Screening Results</h2>
                <p>ID: {screening_id} | Type: {detected_type}</p>
            </div>
            <div class="card-header-right" style="text-align: right; padding-top: 8px; white-space: nowrap; font-weight: bold;">{date_line}<br>{time_line}</div>
        </div>
        <div class="card-body">
            <div class="score-section">{svg}<span class="{badge_class}">{badge_icon} {label}</span></div>
            <div class="indicator-box">
                <div class="indicator-title" style="color:{indicator_color};">{indicator_icon} {message_title}</div>
                <p class="indicator-text">{message_text}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        sub1, sub2 = st.columns(2)
        with sub1:
            if st.button("📄 Generate Report", use_container_width=True):
                st.query_params["uid"] = str(user_id)
                st.query_params["uname"] = user_name
                st.switch_page("pages/6_Report.py")
        with sub2:
            if st.button("➡️ New Screening", use_container_width=True):
                st.session_state.result = None
                st.session_state.upload_method = None
                st.session_state.draw_type = None
                st.rerun()

    st.markdown("""
    <div class="disclaimer-box">
        <span>ℹ️</span>
        <div><b>Disclaimer:</b> This screening tool is for preliminary assessment only and not a substitute for professional medical diagnosis.</div>
    </div>
    """, unsafe_allow_html=True)