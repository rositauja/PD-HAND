import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import time
import cv2
import datetime
import random
from core.preprocess import preprocess_spiral, preprocess_meander
from core.features import extract_spiral_features, extract_meander_features
from core.predict import predict_spiral, predict_meander, predict_draw
from core.database import save_screening, get_user_profile
from core.preprocess import preprocess_draw
from core.predict import predict_draw

st.set_page_config(page_title="PD-HAND | Processing", layout="wide")

# ═══════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")
    st.stop()

user_id = st.session_state.get("user_id", "")
user_name = st.session_state.get("user_name", "User")

# ═══════════════════════════════════════════════════════════════════
# CHECK IF COMING FROM VALID SUBMISSION
# ═══════════════════════════════════════════════════════════════════

if "is_processing" not in st.session_state or not st.session_state.is_processing:
    st.switch_page("pages/4_Screening.py")
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# HIDE STREAMLIT UI
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
.stApp {
    background:linear-gradient(135deg,#f0faf3 0%,#d4edda 50%,#c8e6c9 100%) !important;
}
            
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
header { display: none !important; }
footer { display: none !important; }

div[data-testid="stMainBlockContainer"] { 
    padding: 0 !important;
    margin: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# ORIGINAL BEAUTIFUL DESIGN WITH LIVE TRACKING
# ═══════════════════════════════════════════════════════════════════

# Full-screen centered container
col1, col2, col3 = st.columns([1, 1.2, 1])

with col2:
    st.markdown("""
    <div style='text-align: center; padding: 60px 40px;'>
        <h1 style='color: #1b5e20; font-size: 32px; font-weight: 800; margin-bottom: 10px;'>
            Analyzing Your Handwriting
        </h1>
        <p style='color: #666; font-size: 15px; margin-bottom: 30px; line-height: 1.6;'>
            Please wait while we process your sample and generate results...
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Spinner placeholder
    spinner_placeholder = st.empty()
    
    # Progress bar placeholder
    progress_placeholder = st.empty()
    
    # Status items placeholders
    status_placeholder = st.empty()
    
    # Info box
    st.markdown("""
    <div style='background: #f0faf3; border: 1px solid #c8e6c9; border-radius: 12px; padding: 14px 16px; 
                font-size: 12px; color: #555; margin-top: 20px; text-align: center; line-height: 1.6;'>
        ℹ️ This typically takes <strong>2-5 seconds</strong>. Do not close or navigate away from this page.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# REAL PROCESSING WITH LIVE TRACKING
# ═══════════════════════════════════════════════════════════════════

processing_complete = False
processing_error = None

try:
    if "processing_image" in st.session_state and st.session_state.processing_image is not None:
        image = st.session_state.processing_image
        processing_type = st.session_state.processing_type
        processing_source = st.session_state.processing_source
        
        # ─────────────────────────────────────────────────────────
        # STAGE 1: PREPARING (Preprocessing)
        # ─────────────────────────────────────────────────────────
        
        with spinner_placeholder.container():
            st.markdown("""
            <div style='text-align: center; margin: 40px 0;'>
                <div style='position: relative; width: 100px; height: 100px; margin: 0 auto;'>
                    <!-- Glow effect -->
                    <div style='position: absolute; inset: 0; border-radius: 50%; 
                                background: radial-gradient(circle, rgba(102, 187, 106, 0.2) 0%, transparent 70%);
                                animation: pulse 1.5s ease-in-out infinite;'></div>
                    <!-- Spinner -->
                    <div style='position: absolute; inset: 0; border: 7px solid #e0e0e0; 
                                border-top: 7px solid #2E7D32; border-right: 7px solid #43A047;
                                border-radius: 50%; animation: rotate 1.2s linear infinite;'></div>
                </div>
                <style>
                    @keyframes rotate { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
                </style>
            </div>
            """, unsafe_allow_html=True)
        
        with progress_placeholder.container():
            st.progress(0.15)
            st.markdown("<p style='text-align: center; color: #2E7D32; font-weight: 600;'>Preparing...</p>", unsafe_allow_html=True)
        
        with status_placeholder.container():
            st.markdown("""
            <div style='background: #f0faf3; border: 1px solid #c8e6c9; border-radius: 10px; padding: 12px; 
                        text-align: left; font-size: 13px;'>
                <div style='display: flex; gap: 10px; align-items: flex-start; margin-bottom: 8px;'>
                    <div style='background: #2E7D32; color: white; border-radius: 50%; width: 24px; height: 24px; 
                                display: flex; align-items: center; justify-content: center; font-size: 12px; 
                                flex-shrink: 0;'>✓</div>
                    <div style='flex: 1;'>
                        <strong style='color: #2E7D32;'>Preparing</strong><br>
                        <span style='color: #999; font-size: 12px;'>Analyzing your handwriting sample...</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ACTUAL PREPROCESSING
        start_time = time.time()

        if processing_source == "draw":
            from core.preprocess import preprocess_draw
            gray, thresh = preprocess_draw(image)

        else:
            if processing_type == "Spiral":
                gray, thresh = preprocess_spiral(image)
            else:
                gray, thresh = preprocess_meander(image)

        prep_time = time.time() - start_time
        
        time.sleep(0.3)
        
        # ─────────────────────────────────────────────────────────
        # STAGE 2: PROCESSING (Feature Extraction)
        # ─────────────────────────────────────────────────────────
        
        with progress_placeholder.container():
            st.progress(0.50)
            st.markdown("<p style='text-align: center; color: #2E7D32; font-weight: 600;'>Processing...</p>", unsafe_allow_html=True)
        
        with status_placeholder.container():
            st.markdown("""
            <div style='background: #f0faf3; border: 1px solid #c8e6c9; border-radius: 10px; padding: 12px;'>
                <div style='display: flex; gap: 10px; align-items: flex-start; margin-bottom: 8px;'>
                    <div style='background: #2E7D32; color: white; border-radius: 50%; width: 24px; height: 24px; 
                                display: flex; align-items: center; justify-content: center; font-size: 12px; 
                                flex-shrink: 0;'>✓</div>
                    <div style='flex: 1;'>
                        <strong style='color: #2E7D32;'>Preparing</strong><br>
                        <span style='color: #999; font-size: 12px;'>Analyzing your handwriting sample...</span>
                    </div>
                </div>
                <div style='display: flex; gap: 10px; align-items: flex-start;'>
                    <div style='background: #f0faf3; border: 2px solid #c8e6c9; border-radius: 50%; width: 24px; 
                                height: 24px; display: flex; align-items: center; justify-content: center; 
                                font-size: 12px; flex-shrink: 0; color: #2E7D32; font-weight: bold;'>○</div>
                    <div style='flex: 1;'>
                        <strong style='color: #2E7D32;'>Processing</strong><br>
                        <span style='color: #999; font-size: 12px;'>Extracting pattern features...</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ACTUAL FEATURE EXTRACTION
        start_time = time.time()
        if processing_type == "Spiral":
            features = extract_spiral_features(thresh)
        else:
            features = extract_meander_features(thresh)
        feature_time = time.time() - start_time
        
        time.sleep(0.3)
        
        # ─────────────────────────────────────────────────────────
        # STAGE 3: PREDICTING (Model Inference)
        # ─────────────────────────────────────────────────────────
        
        with progress_placeholder.container():
            st.progress(0.85)
            st.markdown("<p style='text-align: center; color: #2E7D32; font-weight: 600;'>Predicting...</p>", unsafe_allow_html=True)
        
        with status_placeholder.container():
            st.markdown("""
            <div style='background: #f0faf3; border: 1px solid #c8e6c9; border-radius: 10px; padding: 12px;'>
                <div style='display: flex; gap: 10px; align-items: flex-start; margin-bottom: 8px;'>
                    <div style='background: #2E7D32; color: white; border-radius: 50%; width: 24px; height: 24px; 
                                display: flex; align-items: center; justify-content: center; font-size: 12px; 
                                flex-shrink: 0;'>✓</div>
                    <div style='flex: 1;'>
                        <strong style='color: #2E7D32;'>Preparing</strong><br>
                        <span style='color: #999; font-size: 12px;'>Analyzing your handwriting sample...</span>
                    </div>
                </div>
                <div style='display: flex; gap: 10px; align-items: flex-start; margin-bottom: 8px;'>
                    <div style='background: #2E7D32; color: white; border-radius: 50%; width: 24px; height: 24px; 
                                display: flex; align-items: center; justify-content: center; font-size: 12px; 
                                flex-shrink: 0;'>✓</div>
                    <div style='flex: 1;'>
                        <strong style='color: #2E7D32;'>Processing</strong><br>
                        <span style='color: #999; font-size: 12px;'>Extracting pattern features...</span>
                    </div>
                </div>
                <div style='display: flex; gap: 10px; align-items: flex-start;'>
                    <div style='background: #f0faf3; border: 2px solid #c8e6c9; border-radius: 50%; width: 24px; 
                                height: 24px; display: flex; align-items: center; justify-content: center; 
                                font-size: 12px; flex-shrink: 0; color: #2E7D32;'>◯</div>
                    <div style='flex: 1;'>
                        <strong style='color: #2E7D32;'>Predicting</strong><br>
                        <span style='color: #999; font-size: 12px;'>Running AI analysis model...</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # ACTUAL MODEL PREDICTION
        start_time = time.time()

        if processing_source == "draw":

            label, confidence, features = predict_draw(
                image,
                processing_type
            )

        else:
            if processing_type == "Spiral":
                label, confidence = predict_spiral(features)
            else:
                label, confidence = predict_meander(features)

        predict_time = time.time() - start_time
        
        # ─────────────────────────────────────────────────────────
        # COMPLETE
        # ─────────────────────────────────────────────────────────
        
        with progress_placeholder.container():
            st.progress(1.0)
            st.markdown("<p style='text-align: center; color: #2E7D32; font-weight: 600;'>Complete ✓</p>", unsafe_allow_html=True)
        
        with status_placeholder.container():
            st.markdown("""
            <div style='background: #f0faf3; border: 1px solid #c8e6c9; border-radius: 10px; padding: 12px;'>
                <div style='display: flex; gap: 10px; align-items: flex-start; margin-bottom: 8px;'>
                    <div style='background: #2E7D32; color: white; border-radius: 50%; width: 24px; height: 24px; 
                                display: flex; align-items: center; justify-content: center; font-size: 12px; 
                                flex-shrink: 0;'>✓</div>
                    <div style='flex: 1;'>
                        <strong style='color: #2E7D32;'>Preparing</strong><br>
                        <span style='color: #999; font-size: 12px;'>Analyzing your handwriting sample...</span>
                    </div>
                </div>
                <div style='display: flex; gap: 10px; align-items: flex-start; margin-bottom: 8px;'>
                    <div style='background: #2E7D32; color: white; border-radius: 50%; width: 24px; height: 24px; 
                                display: flex; align-items: center; justify-content: center; font-size: 12px; 
                                flex-shrink: 0;'>✓</div>
                    <div style='flex: 1;'>
                        <strong style='color: #2E7D32;'>Processing</strong><br>
                        <span style='color: #999; font-size: 12px;'>Extracting pattern features...</span>
                    </div>
                </div>
                <div style='display: flex; gap: 10px; align-items: flex-start;'>
                    <div style='background: #2E7D32; color: white; border-radius: 50%; width: 24px; height: 24px; 
                                display: flex; align-items: center; justify-content: center; font-size: 12px; 
                                flex-shrink: 0;'>✓</div>
                    <div style='flex: 1;'>
                        <strong style='color: #2E7D32;'>Predicting</strong><br>
                        <span style='color: #999; font-size: 12px;'>Running AI analysis model...</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Save results to session state
        screening_id = "SCR-" + str(random.randint(10000, 99999))
        now = datetime.datetime.now()
        st.session_state.result = (
            label, 
            confidence, 
            processing_type, 
            screening_id,
            now.strftime("%d %B %Y"), 
            now.strftime("%I:%M:%S %p"), 
            features
        )
        
        # Save to database
        user_profile = get_user_profile(st.session_state.user_id)
        user_age = user_profile.get("age")
        user_hand = user_profile.get("hand")
        
        save_screening(
            screening_id, 
            st.session_state.user_id, 
            now.strftime("%d %B %Y"),
            now.strftime("%I:%M:%S %p"), 
            processing_type, 
            label, 
            confidence, 
            age=user_age, 
            hand=user_hand, 
            features=features
        )
        
        processing_complete = True
        
        time.sleep(1.0)
        
except Exception as e:
    processing_error = str(e)
    with status_placeholder.container():
        st.error(f"❌ **Processing Error**\n{str(e)}")

# ═══════════════════════════════════════════════════════════════════
# REDIRECT AFTER PROCESSING
# ═══════════════════════════════════════════════════════════════════

if processing_complete:
    st.session_state.is_processing = False
    st.session_state.processing_image = None
    st.session_state.processing_type = None
    st.switch_page("pages/4_Screening.py")
    st.stop()

if processing_error:
    st.session_state.is_processing = False
    if st.button("← Back to Screening", use_container_width=True):
        st.switch_page("pages/4_Screening.py")