#validation.py
import streamlit as st
import time

def show_loading():
    st.markdown("""
    <style>
    .loading-card {
        background: linear-gradient(135deg, #d4edda, #c8e6c9);
        border-radius: 16px;
        padding: 48px 24px;
        text-align: center;
        margin: 20px auto;
    }
    .loading-icons {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin-bottom: 24px;
    }
    .loading-icon {
        width: 72px;
        height: 72px;
        background: #66BB6A;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
    }
    .loading-title {
        font-size: 28px;
        font-weight: 800;
        color: #1b5e20;
        margin-bottom: 8px;
    }
    .loading-subtitle {
        font-size: 14px;
        color: #4a7c59;
        margin-bottom: 24px;
    }
    .loading-footer {
        font-size: 13px;
        color: #4a7c59;
        margin-top: 20px;
    }
    .dot-row {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-top: 16px;
    }
    .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #81C784;
    }
    .dot.active { background: #1565C0; }
    </style>
    """, unsafe_allow_html=True)

    placeholder = st.empty()
    steps = [
        (10,  "Preprocessing image..."),
        (30,  "Extracting features..."),
        (60,  "Analysing handwriting patterns..."),
        (85,  "Running model prediction..."),
        (100, "Done!"),
    ]

    for pct, msg in steps:
        dot1 = "active" if pct <= 30  else ""
        dot2 = "active" if pct <= 60  else ""
        dot3 = "active" if pct <= 100 else ""

        placeholder.markdown(f"""
        <div class="loading-card">
            <div class="loading-icons">
                <div class="loading-icon">✏️</div>
                <div class="loading-icon">📊</div>
            </div>
            <div class="loading-title">Analyzing Handwriting</div>
            <div class="loading-subtitle">{msg}</div>
            <div style="background:#b2dfdb; border-radius:999px; height:6px; width:60%; margin:0 auto;">
                <div style="background:#1b5e20; width:{pct}%; height:6px; border-radius:999px; transition: width 0.4s;"></div>
            </div>
            <div style="font-size:13px; color:#4a7c59; margin-top:8px;">{pct}% complete</div>
            <div class="dot-row">
                <div class="dot {dot1}"></div>
                <div class="dot {dot2}"></div>
                <div class="dot {dot3}"></div>
            </div>
            <div class="loading-footer">Please wait while our AI analyses the handwriting sample....</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.6)

    placeholder.empty()