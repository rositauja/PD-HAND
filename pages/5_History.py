import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from core.auth import require_auth

st.set_page_config(page_title="PD-HAND | History", layout="wide")

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

from io import BytesIO
import base64
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm
from core.database import get_user_screenings, delete_all_user_screenings, delete_screening
from core.report_generator import generate_analysis

def generate_pdf(screening_id, date_line, time_line, detected_type, label, confidence, features):
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
    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story  = []
    green      = colors.HexColor("#2E7D32")
    lightgreen = colors.HexColor("#c8e6c9")
    lightgray  = colors.HexColor("#f5f5f5")
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=20, textColor=green, spaceAfter=6)
    head_style  = ParagraphStyle("head",  parent=styles["Normal"], fontSize=11, textColor=green, fontName="Helvetica-Bold", spaceAfter=4)
    body_style  = ParagraphStyle("body",  parent=styles["Normal"], fontSize=9,  textColor=colors.HexColor("#444444"), spaceAfter=3)
    small_style = ParagraphStyle("small", parent=styles["Normal"], fontSize=8,  textColor=colors.HexColor("#666666"))
    story.append(Paragraph("Screening Report", title_style))
    story.append(Spacer(1, 0.3*cm))
    banner_table = Table([[Paragraph(f"<b>Report ID:</b> {screening_id}", body_style), Paragraph(f"<b>Date:</b> {date_line}  <b>Time:</b> {time_line}", body_style)]], colWidths=[8*cm, 8*cm])
    banner_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),lightgreen),("PADDING",(0,0),(-1,-1),10)]))
    story.append(banner_table); story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Screening Summary", head_style))
    summary_table = Table([["Date & Time", f"{date_line}, {time_line}"],["Report ID", screening_id],["Analysis Type","Handwriting Pattern Analysis"],["Handwriting Type",detected_type],["Screening Result",label],["Confidence Score",f"{confidence_pct}%"],["Status","Complete"]], colWidths=[5*cm,11*cm])
    summary_table.setStyle(TableStyle([("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,0),(0,-1),colors.HexColor("#888888")),("TEXTCOLOR",(1,0),(1,-1),colors.HexColor("#333333")),("FONTNAME",(1,0),(1,-1),"Helvetica-Bold"),("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white,lightgray]),("PADDING",(0,0),(-1,-1),6),("LINEBELOW",(0,0),(-1,-2),0.5,colors.HexColor("#e0e0e0"))]))
    story.append(summary_table); story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Analysis Details", head_style))
    analysis_table = Table([[Paragraph(f"<b>Stroke Regularity</b><br/>{stroke_regularity_text}",small_style),Paragraph(f"<b>Drawing Coverage</b><br/>{drawing_coverage_text}",small_style),Paragraph(f"<b>Pattern Complexity</b><br/>{pattern_complexity_text}",small_style)]], colWidths=[5.3*cm,5.3*cm,5.4*cm])
    analysis_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f0faf3")),("BOX",(0,0),(0,-1),0.5,lightgreen),("BOX",(1,0),(1,-1),0.5,lightgreen),("BOX",(2,0),(2,-1),0.5,lightgreen),("PADDING",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(analysis_table); story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Recommendations", head_style))
    rec_table = Table([[Paragraph("<br/>".join(f"• {r}" for r in recommendations), small_style)]], colWidths=[16*cm])
    rec_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f0faf3")),("BOX",(0,0),(-1,-1),0.5,lightgreen),("PADDING",(0,0),(-1,-1),10)]))
    story.append(rec_table); story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Disclaimer", head_style))
    story.append(Paragraph("This report is generated by an AI-based handwriting screening tool and is intended for informational purposes only. The results do not constitute a medical diagnosis. Please consult a qualified healthcare provider for further assessment.", small_style))
    doc.build(story); buffer.seek(0)
    return buffer

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

/* Clear All button */
div[data-testid="stButton"] button {
    background:#eeeeee !important;
    color:#444 !important;
    border:1px solid #d6d6d6 !important;
}

div[data-testid="stButton"] button:hover {
    background:#e5e5e5 !important;
    border-color:#c8c8c8 !important;
    color:#222 !important;
}
            
.history-table { width:100%; border-collapse:collapse; border:1px solid #c8e6c9; border-radius:12px; overflow:hidden; font-size:13px; }
.history-table th { background:#d4edda; color:#1b5e20; font-weight:700; padding:12px 14px; text-align:left; }
.history-table td { padding:10px 14px; border-bottom:1px solid #f0f0f0; color:#444; vertical-align:middle; }
.history-table tr:last-child td { border-bottom:none; }
.history-table tr:hover td { background:#f9fdf9; }
.badge-high { background-color:#FFF3E0; color:#E65100; border:1px solid #FFB74D; border-radius:20px; padding:3px 10px; font-size:12px; font-weight:600; display:inline-flex; align-items:center; gap:4px; }
.badge-low  { background-color:#E8F5E9; color:#2E7D32; border:1px solid #81C784; border-radius:20px; padding:3px 10px; font-size:12px; font-weight:600; display:inline-flex; align-items:center; gap:4px; }
.id-badge   { background:#f0faf3; border:1px solid #c8e6c9; border-radius:20px; padding:3px 10px; font-size:12px; color:#2E7D32; font-weight:600; }
.stat-card  { background:white; border:1px solid #e0e0e0; border-radius:12px; padding:20px; text-align:center; }
.stat-number { font-size:32px; font-weight:800; color:#1b5e20; margin-bottom:4px; }
.stat-number.red { color:#C62828; }
.stat-label { font-size:13px; color:#888; }

div[data-testid="stMainBlockContainer"] { padding: 0px 48px 40px 48px !important; }
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
        <a class="nav-link-btn active" href="/History?uid={user_id}&uname={user_name}" target="_self">🕒 History</a>
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
# HISTORY CONTENT
# ═══════════════════════════════════════════════════════════════════

hdr_col, btn_col = st.columns([3, 1])
with hdr_col:
    st.markdown("""
<h2 style="
    font-weight:800;
    margin:0;
    margin-top:15px;
    color:#1b1b1b;
    opacity:1;
">
    Screening History
</h2>
""", unsafe_allow_html=True)
    st.markdown("""
<div style="
    color:#666;
    font-size:15px;
    margin-top:-2px;
    margin-bottom:14px;
    opacity:1;
">
    View and manage previous screening records
</div>
""", unsafe_allow_html=True)
with btn_col:
    st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
    if st.button("🗑️ Clear All", use_container_width=True):
        delete_all_user_screenings(user_id)
        st.rerun()

records = get_user_screenings(user_id)

if not records:
    st.info("No screening records found. Complete a screening to see history here.")
else:
    # ═══════════════════════════════════════════════════════════════════
    # HANDLE DELETE - FIX: Preserve auth params!
    # ═══════════════════════════════════════════════════════════════════
    if "delete" in st.query_params:
        delete_screening(st.query_params["delete"], user_id)
        
        # PRESERVE auth params before clearing
        st.query_params["uid"] = str(user_id)
        st.query_params["uname"] = user_name
        
        # Remove only delete param
        del st.query_params["delete"]
        
        st.rerun()

    rows_html = ""
    for row in records:
        (screening_id, date_line, time_line, detected_type, label, confidence, age, hand,
         ink_pixels, ink_ratio, num_contours, contour_area, contour_perimeter,
         bounding_box_width, bounding_box_height, aspect_ratio,
         centroid_x, centroid_y, extent, solidity) = row

        features = {"ink_pixels":ink_pixels,"ink_ratio":ink_ratio,"num_contours":num_contours,"contour_area":contour_area,"contour_perimeter":contour_perimeter,"bounding_box_width":bounding_box_width,"bounding_box_height":bounding_box_height,"aspect_ratio":aspect_ratio,"centroid_x":centroid_x,"centroid_y":centroid_y,"extent":extent,"solidity":solidity}
        confidence_pct = int(confidence * 100)
        badge = f'<span class="badge-high">🔴 {label}</span>' if label == "High Likelihood" else f'<span class="badge-low">✅ {label}</span>'
        pdf_b64 = base64.b64encode(generate_pdf(screening_id, date_line, time_line, detected_type, label, confidence, features).read()).decode()

        # ═══════════════════════════════════════════════════════════════════
        # FIX: Delete link now includes uid and uname to preserve auth!
        # ═══════════════════════════════════════════════════════════════════
        rows_html += (
            f"<tr>"
            f"<td>{date_line}<br><span style='color:#aaa;font-size:11px;'>{time_line}</span></td>"
            f"<td><span class='id-badge'>{screening_id}</span></td>"
            f"<td>{detected_type}</td><td>{badge}</td><td><b>{confidence_pct}%</b></td>"
            f"<td>"
            f"<a href='data:application/pdf;base64,{pdf_b64}' download='report_{screening_id}.pdf' style='display:inline-block;margin-bottom:6px;padding:4px 12px;background:#f0faf3;border:1px solid #c8e6c9;border-radius:8px;font-size:12px;color:#2E7D32;text-decoration:none;'>⬇️ PDF</a><br>"
            f"<a href='?delete={screening_id}&uid={user_id}&uname={user_name}' target='_self' style='display:inline-block;padding:4px 12px;background:#fff3f3;border:1px solid #ffcdd2;border-radius:8px;font-size:12px;color:#c62828;text-decoration:none;'>🗑️ Delete</a>"
            f"</td></tr>"
        )

    st.markdown(f"""
    <table class="history-table">
        <thead><tr><th>Date &amp; Time</th><th>Report ID</th><th>Type</th><th>Result</th><th>Confidence</th><th>Actions</th></tr></thead>
        <tbody>{rows_html}</tbody>
    </table>""", unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    total = len(records)
    low_count  = sum(1 for r in records if r[4] == "Low Likelihood")
    high_count = sum(1 for r in records if r[4] == "High Likelihood")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{total}</div><div class="stat-label">Total Screenings</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{low_count}</div><div class="stat-label">Low Likelihood</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-number red">{high_count}</div><div class="stat-label">High Likelihood</div></div>', unsafe_allow_html=True)