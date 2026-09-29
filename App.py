import streamlit as st
import math
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pro Football Analytics Engine", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ADVANCED CUSTOM STYLING (DARK ULTRA-PRO THEME)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f17 !important;
        color: #e2e8f0 !important;
    }

    .stApp {
        background-color: #0b0f17 !important;
    }

    header[data-testid="stHeader"] { background: rgba(11, 15, 23, 0.8) !important; backdrop-filter: blur(8px); }
    footer { visibility: hidden; }

    .pro-card {
        background: linear-gradient(145deg, #131b2e 0%, #0f1623 100%);
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    .stat-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-primary { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-success { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-warning { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }

    .metric-value-huge {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #60a5fa, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .heatmap-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 4px;
        font-size: 13px;
        margin-top: 10px;
    }
    .heatmap-table th {
        background-color: #1e293b;
        color: #94a3b8;
        padding: 10px;
        font-weight: 600;
        border-radius: 6px;
        text-align: center;
    }
    .heatmap-table td {
        padding: 12px 8px;
        text-align: center;
        border-radius: 6px;
        font-weight: 600;
    }

    .stButton > button, .stDownloadButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 14px 20px !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
    }

    div[data-baseweb="input"] {
        background-color: #1a2332 !important;
        border-color: #334155 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PDF RApor OLUŞTURMA FONKSİYONU
# ---------------------------------------------------------
def generate_pdf_report(home_name, away_name, xg_home, xg_away, p_ms1, p_ms0, p_ms2, banko, ideal, surpriz, top_scores):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1e293b'), alignment=1, spaceAfter=15)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#2563eb'), spaceAfter=10)
    text_style = ParagraphStyle('TextStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#334155'), spaceAfter=6)

    # Başlık
    story.append(Paragraph(f"<b>MAÇ ANALİZ VE TAHMİN RAPORU</b>", title_style))
    story.append(Paragraph(f"<b>{home_name.upper()} vs {away_name.upper()}</b>", title_style))
    story.append(Spacer(1, 10))

    # xG Bilgisi
    data_xg = [
        ["Takım", "Beklenen Gol (xG)"],
        [home_name, f"{xg_home:.2f}"],
        [away_name, f"{xg_away:.2f}"],
        ["Toplam xG", f"{xg_home + xg_away:.2f}"]
    ]
    t_xg = Table(data_xg, colWidths=[200, 200])
    t_xg.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_xg)
    story.append(Spacer(1, 15))

    # Maç Sonu Olasılıkları
    story.append(Paragraph("<b>1. Maç Sonucu Olasılıkları</b>", sub_style))
    data_ms = [
        ["MS 1 (%)", "MS 0 (%)", "MS 2 (%)"],
        [f"%{p_ms1*100:.1f}", f"%{p_ms0*100:.1f}", f"%{p_ms2*100:.1f}"]
    ]
    t_ms = Table(data_ms, colWidths=[130, 130, 130])
    t_ms.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(t_ms)
    story.append(Spacer(1, 15))

    # Stratejik Öneriler
    story.append(Paragraph("<b>2. Algoritmik Strateji Kartı</b>", sub_style))
    story.append(Paragraph(f"• <b>BANKO TERCİH:</b> {banko}", text_style))
    story.append(Paragraph(f"• <b>İDEAL BAHİS:</b> {ideal}", text_style))
    story.append(Paragraph(f"• <b>SÜRPRİZ TERCİH:</b> {surpriz}", text_style))
    story.append(Spacer(1, 15))

    # Olası Skorlar
    story.append(Paragraph("<b>3. En Olası Skorlar</b>", sub_style))
    for idx, ((h, a), prob) in enumerate(top_scores, 1):
        story.append(Paragraph(f"#{idx} Skor: <b>{h} - {a}</b> (Olasılık: %{prob*100:.1f})", text_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# SIDEBAR - CONFIGURATION & PARAMETERS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Lig Parametreleri")
    
    # Hızlı Şablon Seçimi
    league_preset = st.selectbox("🏆 Hazır Lig Şablonu", ["Özel / Elle Gir", "Süper Lig (TR)", "Premier League (UK)", "La Liga (ES)", "Bundesliga (DE)"])
    
    if league_preset == "Süper Lig (TR)":
        default_h, default_a = 1.55, 1.25
    elif league_preset == "Premier League (UK)":
        default_h, default_a = 1.58, 1.32
    elif league_preset == "La Liga (ES)":
        default_h, default_a = 1.42, 1.12
    elif league_preset == "Bundesliga (DE)":
        default_h, default_a = 1.70, 1.40
    else:
        default_h, default_a = 1.50, 1.20

    league_home_xg = st.number_input("Lig İç Saha Gol Ort.", min_value=0.1, max_value=4.0, value=default_h, step=0.05)
    league_away_xg = st.number_input("Lig Dış Saha Gol Ort.", min_value=0.1, max_value=4.0, value=default_a, step=0.05)
    
    st.markdown("---")
    st.markdown("#### 🧮 Model Ayarları")
    use_dixon_coles = st.checkbox("Dixon-Coles Düzeltmesi", value=True)
    rho = st.slider("Dixon-Coles Korelasyonu (Rho)", -0.30, 0.0, -0.13, 0.01) if use_dixon_coles else 0.0

# ---------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------
st.markdown("""
<div style="padding-bottom: 10px;">
    <h1 style="margin:0; font-size: 28px; font-weight: 800; color: #ffffff;">⚽ Professional Football Analytics Engine</h1>
    <p style="margin:4px 0 0 0; color: #94a3b8; font-size: 14px;">Pratik Veri Girişi, Otomatik Analiz ve PDF Raporlama Sistemi</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INPUT FORM
# ---------------------------------------------------------
st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
st.markdown("""<span class="stat-badge badge-primary">Hızlı Giriş</span> <h3 style="margin: 8px 0 15px 0;">Takım Maç İstatistikleri</h3>""", unsafe_allow_html=True)

col_h, col_a = st.columns(2)

with col_h:
    st.markdown("#### 🏠 Ev Sahibi Takım")
    home_name = st.text_input("Takım Adı", value="Beşiktaş", key="h_name")
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        home_matches = st.number_input("Oynadığı Maç", min_value=1, value=10, step=1)
    with col_h2:
        home_goals_scored = st.number_input("Attığı Gol", min_value=0, value=20, step=1)
    with col_h3:
        home_goals_conceded = st.number_input("Yediği Gol", min_value=0, value=8, step=1)

with col_a:
    st.markdown("#### ✈️ Deplasman Takımı")
    away_name = st.text_input("Takım Adı ", value="Trabzonspor", key="a_name")
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        away_matches = st.number_input("Oynadığı Maç ", min_value=1, value=10, step=1)
    with col_a2:
        away_goals_scored = st.number_input("Attığı Gol ", min_value=0, value=14, step=1)
    with col_a3:
        away_goals_conceded = st.number_input("Yediği Gol ", min_value=0, value=13, step=1)

home_att_avg = home_goals_scored / home_matches
home_def_avg = home_goals_conceded / home_matches
away_att_avg = away_goals_scored / away_matches
away_def_avg = away_goals_conceded / away_matches

st.markdown("""<hr style="margin: 15px 0 !important;">""", unsafe_allow_html=True)
st.markdown("#### 💰 Büro Oranları (Value Bet Analizi - İsteğe Bağlı)")

col_o1, col_o2, col_o3 = st.columns(3)
with col_o1:
    odds_ms1 = st.number_input("MS 1 Oranı", min_value=1.0, value=2.10, step=0.05)
with col_o2:
    odds_ms0 = st.number_input("MS 0 Oranı", min_value=1.0, value=3.25, step=0.05)
with col_o3:
    odds_ms2 = st.number_input("MS 2 Oranı", min_value=1.0, value=3.10, step=0.05)

st.markdown("""</div>""", unsafe_allow_html=True)

# ---------------------------------------------------------
# POISSON ENGINE & CALCULATIONS
# ---------------------------------------------------------
def dixon_coles_tau(h, a, xg_h, xg_a, rho_val):
    if not use_dixon_coles: return 1.0
    if h == 0 and a == 0: return 1.0 - (xg_h * xg_a * rho_val)
    elif h == 0 and a == 1: return 1.0 + (xg_h * rho_val)
    elif h == 1 and a == 0: return 1.0 + (xg_a * rho_val)
    elif h == 1 and a == 1: return 1.0 - rho_val
    else: return 1.0

if st.button("🔥 MAÇI DETAYLI ANALİZ ET VE MODELİ ÇALIŞTIR", use_container_width=True):
    
    home_attack_power = home_att_avg / league_home_xg if league_home_xg > 0 else 1.0
    home_defense_power = home_def_avg / league_away_xg if league_away_xg > 0 else 1.0
    away_attack_power = away_att_avg / league_away_xg if league_away_xg > 0 else 1.0
    away_defense_power = away_def_avg / league_home_xg if league_home_xg > 0 else 1.0

    xg_home = home_attack_power * away_defense_power * league_home_xg
    xg_away = away_attack_power * home_defense_power * league_away_xg
    total_xg = xg_home + xg_away

    matrix = {}
    for h in range(7):
        for a in range(7):
            p_h = (math.pow(xg_home, h) * math.exp(-xg_home)) / math.factorial(h)
            p_a = (math.pow(xg_away, a) * math.exp(-xg_away)) / math.factorial(a)
            tau = dixon_coles_tau(h, a, xg_home, xg_away, rho)
            matrix[(h, a)] = p_h * p_a * tau

    total_p = sum(matrix.values())
    for k in matrix: matrix[k] /= total_p

    p_ms1 = sum(p for (h, a), p in matrix.items() if h > a)
    p_ms0 = sum(p for (h, a), p in matrix.items() if h == a)
    p_ms2 = sum(p for (h, a), p in matrix.items() if h < a)

    p_alt15 = sum(p for (h, a), p in matrix.items() if h + a < 1.5)
    p_ust15 = 1.0 - p_alt15
    p_alt25 = sum(p for (h, a), p in matrix.items() if h + a < 2.5)
    p_ust25 = 1.0 - p_alt25
    p_kgvar = sum(p for (h, a), p in matrix.items() if h > 0 and a > 0)

    top_scores = sorted(matrix.items(), key=lambda x: x[1], reverse=True)[:4]

    # Strateji
    banko = f"1.5 Gol Üst (%{p_ust15*100:.1f})" if p_ust15 > 0.75 else f"Çifte Şans 1X (%{(p_ms1+p_ms0)*100:.1f})"
    ideal = f"MS 1 (%{p_ms1*100:.1f})" if p_ms1 > 0.50 else (f"2.5 Üst (%{p_ust25*100:.1f})" if p_ust25 > 0.52 else f"KG Var (%{p_kgvar*100:.1f})")
    surpriz = f"KG Var & 2.5 Üst"

    # DASHBOARD
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius:16px; padding:25px; border:1px solid #334155; text-align:center; margin-bottom:25px;">
        <span class="stat-badge badge-primary">ANALİZ RAPORU</span>
        <h2 style="font-size:30px; font-weight:800; margin: 10px 0 5px 0; color:#ffffff;">{home_name.upper()} vs {away_name.upper()}</h2>
        <p style="color:#94a3b8; font-size:15px; margin:0;">
            Model Beklenen Goller (xG): <b style="color:#38bdf8;">{home_name}: {xg_home:.2f}</b> | <b style="color:#f43f5e;">{away_name}: {xg_away:.2f}</b> &nbsp;•&nbsp; Toplam xG: <b style="color:#34d399;">{total_xg:.2f}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ÖNERİLER KARTI
    st.markdown("### 💡 Model Strateji Önerileri")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"""<div class="pro-card"><span class="stat-badge badge-success">BANKO</span><p style="margin-top:8px; font-weight:700;">{banko}</p></div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""<div class="pro-card"><span class="stat-badge badge-primary">İDEAL</span><p style="margin-top:8px; font-weight:700;">{ideal}</p></div>""", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""<div class="pro-card"><span class="stat-badge badge-warning">SÜRPRİZ</span><p style="margin-top:8px; font-weight:700;">{surpriz}</p></div>""", unsafe_allow_html=True)

    # PDF INDIRME BUTONU (MADDE 6)
    st.markdown("---")
    st.markdown("### 📄 Analiz Raporunu İndir")
    pdf_file = generate_pdf_report(home_name, away_name, xg_home, xg_away, p_ms1, p_ms0, p_ms2, banko, ideal, surpriz, top_scores)
    
    st.download_button(
        label="📥 PDF MAÇ RAPORUNU İNDİR",
        data=pdf_file,
        file_name=f"{home_name}_vs_{away_name}_Analiz_Raporu.pdf",
        mime="application/pdf"
    )
