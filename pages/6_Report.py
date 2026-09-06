import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

st.set_page_config(page_title="PD-HAND | Report", layout="wide")

# ═══════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════

go = st.query_params.get("go", None)
if go == "logout":
    st.session_state.clear()
    st.query_params.clear()
    st.switch_page("app.py")
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
initials = "".join([w[0].upper() for w in user_name.split()[:2]]) or "U"

import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm
from core.report_generator import generate_analysis

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }
[data-testid="stSidebar"]        { display: none; }
[data-testid="collapsedControl"] { display: none; }
[data-testid="stToolbar"]        { display: none; }
[data-testid="stDecoration"]     { display: none; }
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
    padding:16px 40px;
    margin:0 0 24px 0;
    border-bottom:1px solid var(--border-light);
    background:rgba(255,255,255,0.97);
    position:sticky;
    top:0;
    z-index:100;
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
            
.report-banner { background:linear-gradient(135deg,#d4edda,#c8e6c9); border-radius:12px 12px 0 0; padding:20px 24px; text-align:right; color:#1b5e20; font-size:14px; font-weight:600; }
.report-body   { border:1px solid #c8e6c9; border-radius:0 0 12px 12px; overflow:hidden; margin-bottom:24px; }
.report-inner  { display:grid; grid-template-columns:1fr 1.4fr; gap:0; }
.left-panel    { padding:20px; border-right:1px solid #e0e0e0; }
.right-panel   { padding:20px; }
.section-title { font-size:13px; font-weight:700; color:#2E7D32; margin-bottom:12px; }
.summary-row   { display:flex; justify-content:space-between; font-size:12.5px; padding:4px 0; border-bottom:1px solid #f0f0f0; color:#444; }
.summary-row span:first-child { color:#888; }
.summary-row span:last-child  { font-weight:600; text-align:right; }
.analysis-grid { display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-bottom:16px; }
.analysis-card { background:#f0faf3; border:1px solid #c8e6c9; border-radius:10px; padding:10px; font-size:11.5px; color:#444; }
.analysis-card-title { font-weight:700; color:#2E7D32; font-size:12px; margin-bottom:6px; }
.recommendations { background:#f0faf3; border:1px solid #c8e6c9; border-radius:10px; padding:12px; font-size:12.5px; color:#444; }
.recommendations ul { margin:6px 0 0 0; padding-left:16px; line-height:1.75; }
.disclaimer-box { background:#f5f5f5; border-radius:10px; padding:14px 16px; font-size:12px; color:#666; margin-top:16px; display:flex; gap:10px; align-items:flex-start; border:1px solid #e0e0e0; }

div[data-testid="stMainBlockContainer"] { padding: 0 48px 40px 48px !important; }

/* ═══════════════════════════════════════════════════════════════════
   PRINT MODE - Hide UI and optimize report layout for printing
═══════════════════════════════════════════════════════════════════ */
@media print {
    /* Hide all Streamlit and UI elements */
    header,
    footer,
    [data-testid="stSidebar"],
    [data-testid="stToolbar"],
    [data-testid="collapsedControl"],
    [data-testid="stDecoration"],
    .navbar,
    button,
    .stButton,
    .stDownloadButton,
    [role="button"] {
        display: none !important;
    }

    /* Reset body and main container background */
    body,
    html,
    .main,
    .block-container {
        background: white !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Reset main block container */
    div[data-testid="stMainBlockContainer"] {
        padding: 1.5cm 1.5cm 1.5cm 1.5cm !important;
        margin: 0 !important;
    }

    /* Report body styling */
    .report-body {
        border: 1px solid #c8e6c9 !important;
        box-shadow: none !important;
        width: 100% !important;
        page-break-inside: avoid;
        margin-bottom: 0 !important;
    }

    .report-banner {
        border-radius: 12px 12px 0 0 !important;
        page-break-inside: avoid;
    }

    /* Prevent breaking inside sections */
    .report-inner {
        break-inside: avoid;
        page-break-inside: avoid;
    }

    .left-panel,
    .right-panel {
        page-break-inside: avoid;
    }

    /* Preserve colors in print */
    * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
        color-adjust: exact !important;
    }

    /* Hide any margins/padding from Streamlit containers */
    [data-testid="stVerticalBlock"] > div {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Optimize text for printing */
    p, span, div {
        orphans: 2;
        widows: 2;
    }

    /* A4 page sizing */
    @page {
        size: A4;
        margin: 1.5cm;
    }
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
        <a class="nav-link-btn" href="/Screening?uid={user_id}&uname={user_name}" target="_self">🔍 Screening</a>
        <a class="nav-link-btn" href="/History?uid={user_id}&uname={user_name}" target="_self">🕒 History</a>
        <a class="nav-link-btn active" href="/Report?uid={user_id}&uname={user_name}" target="_self">📄 Report</a>
    </div>
    <div class="nav-right">
        <div class="user-avatar">{initials}</div>
        <a class="logout-btn" href="?go=logout&uid={user_id}&uname={user_name}" target="_self">→ Log out</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# GUARD
# ═══════════════════════════════════════════════════════════════════

if "result" not in st.session_state or st.session_state.result is None:
    st.warning("No screening result found. Please complete a screening first.")
    if st.button("Go to Screening"):
        st.query_params["uid"] = str(user_id)
        st.query_params["uname"] = user_name
        st.switch_page("pages/4_Screening.py")
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# UNPACK
# ═══════════════════════════════════════════════════════════════════

label, confidence, detected_type, screening_id, date_line, time_line, features = st.session_state.result
confidence_pct = int(confidence * 100)

analysis = generate_analysis(detected_type, features)
stroke_regularity_text  = analysis["stroke_regularity"]
drawing_coverage_text   = analysis["drawing_coverage"]
pattern_complexity_text = analysis["pattern_complexity"]

recommendations = [
    "Consult with a neurologist or movement disorder specialist",
    "Consider comprehensive neurological evaluation",
    "Document and track any other symptoms for healthcare provider",
    "Schedule follow-up screening in 3-6 months",
] if label == "High Likelihood" else [
    "Continue regular health check-ups",
    "Maintain a healthy lifestyle with regular physical activity",
    "Monitor any changes in handwriting over time",
    "Schedule routine follow-up screening annually",
]

def generate_pdf():
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    story  = []
    green      = colors.HexColor("#2E7D32")
    lightgreen = colors.HexColor("#c8e6c9")
    lightgray  = colors.HexColor("#f5f5f5")
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=20, textColor=green, spaceAfter=6)
    head_style  = ParagraphStyle("head",  parent=styles["Normal"], fontSize=11, textColor=green, fontName="Helvetica-Bold", spaceAfter=4)
    body_style  = ParagraphStyle("body",  parent=styles["Normal"], fontSize=9,  textColor=colors.HexColor("#444444"), spaceAfter=3)
    small_style = ParagraphStyle("small", parent=styles["Normal"], fontSize=8,  textColor=colors.HexColor("#666666"))
    story.append(Paragraph("Screening Report", title_style)); story.append(Spacer(1, 0.3*cm))
    banner_table = Table([[Paragraph(f"<b>Report ID:</b> {screening_id}", body_style), Paragraph(f"<b>Date:</b> {date_line}  <b>Time:</b> {time_line}", body_style)]], colWidths=[8*cm,8*cm])
    banner_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),lightgreen),("PADDING",(0,0),(-1,-1),10)]))
    story.append(banner_table); story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Screening Summary", head_style))
    summary_table = Table([["Date & Time",f"{date_line}, {time_line}"],["Report ID",screening_id],["Analysis Type","Handwriting Pattern Analysis"],["Handwriting Type",detected_type],["Screening Result",label],["Confidence Score",f"{confidence_pct}%"],["Status","Complete"]], colWidths=[5*cm,11*cm])
    summary_table.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(0,-1),colors.HexColor("#888888")),("TEXTCOLOR",(1,0),(1,-1),colors.HexColor("#333333")),("FONTNAME",(1,0),(1,-1),"Helvetica-Bold"),("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white,lightgray]),("PADDING",(0,0),(-1,-1),6),("LINEBELOW",(0,0),(-1,-2),0.5,colors.HexColor("#e0e0e0"))]))
    story.append(summary_table); story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Analysis Details", head_style))
    analysis_table = Table([[Paragraph(f"<b>Stroke Regularity</b><br/>{stroke_regularity_text}",small_style),Paragraph(f"<b>Drawing Coverage</b><br/>{drawing_coverage_text}",small_style),Paragraph(f"<b>Pattern Complexity</b><br/>{pattern_complexity_text}",small_style)]], colWidths=[5.3*cm,5.3*cm,5.4*cm])
    analysis_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f0faf3")),("BOX",(0,0),(0,-1),0.5,lightgreen),("BOX",(1,0),(1,-1),0.5,lightgreen),("BOX",(2,0),(2,-1),0.5,lightgreen),("PADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(analysis_table); story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Recommendations", head_style))
    rec_table = Table([[Paragraph("<br/>".join(f"• {r}" for r in recommendations),small_style)]], colWidths=[16*cm])
    rec_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f0faf3")),("BOX",(0,0),(-1,-1),0.5,lightgreen),("PADDING",(0,0),(-1,-1),10)]))
    story.append(rec_table); story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Disclaimer", head_style))
    story.append(Paragraph("This report is generated by an AI-based handwriting screening tool and is intended for informational purposes only. The results do not constitute a medical diagnosis. Please consult a qualified healthcare provider for further assessment.", small_style))
    doc.build(story); buffer.seek(0)
    return buffer

pdf_buffer = generate_pdf()
pdf_buffer.seek(0)  

hdr_col, _, btn_col1, btn_col2 = st.columns([2.5, 0.5, 1, 1])
with hdr_col:
    st.markdown("<h2 style='font-weight:800; margin:0;'>Screening Report</h2>", unsafe_allow_html=True)
with btn_col1:
    if st.button("🖨️ Print", key="print_btn", use_container_width=True):

        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")

        js_code = f"""
        <script>

        const byteCharacters = atob("{pdf_base64}");
        const byteNumbers = new Array(byteCharacters.length);

        for (let i = 0; i < byteCharacters.length; i++) {{
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }}

        const byteArray = new Uint8Array(byteNumbers);

        const blob = new Blob([byteArray], {{ type: 'application/pdf' }});

        const blobUrl = URL.createObjectURL(blob);

        const printWindow = window.open(blobUrl);

        printWindow.onload = function() {{

            printWindow.document.title = "PD-HAND Screening Report";

            printWindow.focus();

            setTimeout(() => {{
                printWindow.print();
            }}, 500);
        }};

        </script>
        """

        st.components.v1.html(js_code, height=0)

with btn_col2:
    st.download_button(label="⬇️ Download PDF", data=pdf_buffer, file_name=f"screening_report_{screening_id}.pdf", mime="application/pdf", use_container_width=True, type="primary")

st.markdown(f'<div class="report-banner">Report ID: {screening_id}<br>{date_line}</div>', unsafe_allow_html=True)

rec_items = "".join(f"<li>{r}</li>" for r in recommendations)
st.markdown(f"""
<div class="report-body">
    <div class="report-inner">
        <div class="left-panel">
            <div class="section-title">Screening Summary</div>
            <div class="summary-row"><span>Date &amp; Time</span><span>{date_line}, {time_line}</span></div>
            <div class="summary-row"><span>Report ID</span><span>{screening_id}</span></div>
            <div class="summary-row"><span>Analysis Type</span><span>Handwriting Pattern Analysis</span></div>
            <div class="summary-row"><span>Handwriting Type</span><span>{detected_type}</span></div>
            <div class="summary-row"><span>Screening Result</span><span>{label}</span></div>
            <div class="summary-row"><span>Confidence Score</span><span>{confidence_pct}%</span></div>
            <div class="summary-row"><span>Status</span><span>Complete</span></div>
            <div class="disclaimer-box" style="margin-top:20px;">
                <span>&#x2139;&#xFE0F;</span>
                <div><b>Disclaimer</b><br>This report is for informational purposes only and does not constitute a medical diagnosis.</div>
            </div>
        </div>
        <div class="right-panel">
            <div class="section-title">Analysis Details</div>
            <div class="analysis-grid">
                <div class="analysis-card"><div class="analysis-card-title">Stroke Regularity</div>{stroke_regularity_text}</div>
                <div class="analysis-card"><div class="analysis-card-title">Drawing Coverage</div>{drawing_coverage_text}</div>
                <div class="analysis-card"><div class="analysis-card-title">Pattern Complexity</div>{pattern_complexity_text}</div>
            </div>
            <div class="section-title">Recommendations</div>
            <div class="recommendations"><ul>{rec_items}</ul></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
b1, b2, b3 = st.columns([1.5, 1, 1])
with b2:
    if st.button("🏠 Return Home", use_container_width=True):
        st.query_params["uid"] = str(user_id)
        st.query_params["uname"] = user_name
        st.switch_page("pages/3_Home.py")
with b3:
    if st.button("🕐 View History", use_container_width=True):
        st.query_params["uid"] = str(user_id)
        st.query_params["uname"] = user_name
        st.switch_page("pages/5_History.py")