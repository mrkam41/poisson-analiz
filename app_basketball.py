import streamlit as st
import math

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pro Basketball Analytics & Predictive Engine", 
    page_icon="🏀", 
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
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .pro-card:hover {
        border-color: #f97316;
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
    .badge-primary { background: rgba(249, 115, 22, 0.15); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.3); }
    .badge-success { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-warning { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }

    .metric-value-huge {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #fb923c, #f97316);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label-sub {
        font-size: 12px;
        color: #94a3b8;
        font-weight: 500;
        margin-top: 2px;
    }

    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #ea580c 0%, #c2410c 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 14px 20px !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(234, 88, 12, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #c2410c 0%, #9a3412 100%) !important;
        box-shadow: 0 6px 20px rgba(234, 88, 12, 0.6) !important;
        transform: translateY(-2px);
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
# NORMAL DISTRIBUTIONAL CDF (GAUSSIAN FOR HANDICAP)
# ---------------------------------------------------------
def normal_cdf(x, mean, std_dev):
    """Cumulative distribution function for standard normal distribution."""
    return 0.5 * (1.0 + math.erf((x - mean) / (std_dev * math.sqrt(2.0))))

# ---------------------------------------------------------
# SIDEBAR - CONFIGURATION & PARAMETERS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Lig Parametreleri")
    
    league_avg_pts = st.number_input("Lig Takım Ort. Sayı (48 dk/40 dk)", min_value=60.0, max_value=140.0, value=82.5, step=0.5, help="Ligdeki bir takımın maç başı ortalama sayısı (Euroleague: ~80, NBA: ~114)")
    league_pace = st.number_input("Lig Ort. Tempo (Pace)", min_value=60.0, max_value=120.0, value=72.0, step=0.5, help="1 maçtaki ortalama hücum/zilliyet sayısı")
    home_advantage = st.number_input("Ev Sahibi Avantajı (Sayı)", min_value=0.0, max_value=10.0, value=3.2, step=0.1)

    st.markdown("---")
    st.markdown("#### 🎯 Model Ayarları")
    score_std_dev = st.number_input("Sayı Sapma Değeri (Std Dev)", min_value=5.0, max_value=25.0, value=11.5, step=0.5, help="Basketbolda skor dağılımı varyansı")

    st.markdown("---")
    st.caption("🔥 Pro Basketball Engine v1.0 | Advanced Pace & Rating Model")

# ---------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 10px;">
    <div>
        <h1 style="margin:0; font-size: 28px; font-weight: 800; color: #ffffff;">🏀 Professional Basketball Analytics Engine</h1>
        <p style="margin:4px 0 0 0; color: #94a3b8; font-size: 14px;">Tempo (Pace), Hücum/Savunma Ratingi ve Alt/Üst - Handikap Hesaplama Sistemi</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# INPUT FORM
# ---------------------------------------------------------
st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
st.markdown("""<span class="stat-badge badge-primary">Hızlı Giriş</span> <h3 style="margin: 8px 0 15px 0;">Takım İstatistikleri ve Maç Çizgileri</h3>""", unsafe_allow_html=True)

col_h, col_a = st.columns(2)

with col_h:
    st.markdown("#### 🏠 Ev Sahibi Takım")
    home_name = st.text_input("Ev Sahibi Takım Adı", value="Fenerbahçe Beko", key="h_name")
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        home_off_rating = st.number_input("Attığı Ort. Sayı", min_value=40.0, max_value=150.0, value=86.4, step=0.5)
    with col_h2:
        home_def_rating = st.number_input("Yediği Ort. Sayı", min_value=40.0, max_value=150.0, value=78.2, step=0.5)
    with col_h3:
        home_pace = st.number_input("Takım Temposu (Pace)", min_value=50.0, max_value=120.0, value=71.5, step=0.5)

with col_a:
    st.markdown("#### ✈️ Deplasman Takımı")
    away_name = st.text_input("Deplasman Takım Adı", value="Anadolu Efes", key="a_name")
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        away_off_rating = st.number_input("Attığı Ort. Sayı ", min_value=40.0, max_value=150.0, value=83.1, step=0.5)
    with col_a2:
        away_def_rating = st.number_input("Yediği Ort. Sayı ", min_value=40.0, max_value=150.0, value=81.0, step=0.5)
    with col_a3:
        away_pace = st.number_input("Takım Temposu (Pace) ", min_value=50.0, max_value=120.0, value=73.0, step=0.5)

st.markdown("""<hr style="margin: 15px 0 !important;">""", unsafe_allow_html=True)
st.markdown("#### 💰 Büronun Açtığı Bahis Çizgileri (Line Check)")

col_l1, col_l2, col_l3 = st.columns(3)
with col_l1:
    line_total = st.number_input("Büro Toplam Sayı Limiti (Örn: 164.5)", min_value=100.0, max_value=260.0, value=164.5, step=0.5)
with col_l2:
    line_handicap = st.number_input("Ev Sahibi Handikapı (Örn: -4.5 veya +2.5)", min_value=-30.0, max_value=30.0, value=-3.5, step=0.5)
with col_l3:
    odds_home = st.number_input("Ev Sahibi Oranı", min_value=1.0, value=1.85, step=0.05)

st.markdown("""</div>""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CALCULATION ENGINE
# ---------------------------------------------------------
if st.button("🔥 BASKETBOL MAÇINI ANALİZ ET VE TAHMİNLERİ ÜRET", use_container_width=True):
    
    # Expected Pace
    exp_pace = (home_pace * away_pace) / league_pace if league_pace > 0 else league_pace
    pace_factor = exp_pace / league_pace if league_pace > 0 else 1.0

    # Off / Def Efficiency relative to league
    home_off_eff = home_off_rating / league_avg_pts
    home_def_eff = home_def_rating / league_avg_pts
    away_off_eff = away_off_rating / league_avg_pts
    away_def_eff = away_def_rating / league_avg_pts

    # Project Scores
    proj_home_pts = (home_off_eff * away_def_eff * league_avg_pts * pace_factor) + (home_advantage / 2)
    proj_away_pts = (away_off_eff * home_def_eff * league_avg_pts * pace_factor) - (home_advantage / 2)
    
    total_proj_pts = proj_home_pts + proj_away_pts
    expected_margin = proj_home_pts - proj_away_pts

    # Period Breakdown
    ht_home_pts = proj_home_pts * 0.49
    ht_away_pts = proj_away_pts * 0.49
    q1_home_pts = proj_home_pts * 0.245
    q1_away_pts = proj_away_pts * 0.245

    # Probability Calculations
    # Total Points Over/Under
    prob_over = 1.0 - normal_cdf(line_total, total_proj_pts, score_std_dev)
    prob_under = 1.0 - prob_over

    # Handicap Cover Probability (Home Team Covers)
    # Target difference > -line_handicap
    prob_home_cover = 1.0 - normal_cdf(-line_handicap, expected_margin, score_std_dev / 1.414)
    prob_away_cover = 1.0 - prob_home_cover

    # Win Moneyline Probabilities
    prob_home_win = 1.0 - normal_cdf(0, expected_margin, score_std_dev / 1.414)
    prob_away_win = 1.0 - prob_home_win

    fair_home_ml = 1.0 / prob_home_win if prob_home_win > 0 else 0
    fair_away_ml = 1.0 / prob_away_win if prob_away_win > 0 else 0

    # ---------------------------------------------------------
    # DISPLAY DASHBOARD
    # ---------------------------------------------------------
    st.markdown("---")
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius:16px; padding:25px; border:1px solid #334155; text-align:center; margin-bottom:25px;">
        <span class="stat-badge badge-primary">BASKETBOL ANALİZ RAPORU</span>
        <h2 style="font-size:30px; font-weight:800; margin: 10px 0 5px 0; color:#ffffff;">{home_name.upper()} vs {away_name.upper()}</h2>
        <p style="color:#94a3b8; font-size:15px; margin:0;">
            Tahmini Skor: <b style="color:#fb923c;">{home_name}: {proj_home_pts:.1f}</b> | <b style="color:#38bdf8;">{away_name}: {proj_away_pts:.1f}</b> &nbsp;•&nbsp; Beklenen Toplam Sayı: <b style="color:#34d399;">{total_proj_pts:.1f}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # METRICS TOP CARDS
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
        <div class="pro-card">
            <span class="stat-badge badge-primary">MAÇKAZANANI (ML)</span>
            <div class="metric-value-huge" style="margin-top:10px;">%{prob_home_win*100:.1f} - %{prob_away_win*100:.1f}</div>
            <div class="metric-label-sub">Adil Oranlar: <b>{fair_home_ml:.2f}</b> (Ev) / <b>{fair_away_ml:.2f}</b> (Dep)</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="pro-card">
            <span class="stat-badge badge-success">TOPLAM SAYI ({line_total})</span>
            <div class="metric-value-huge" style="margin-top:10px; color:#34d399;">%{prob_over*100:.1f} ÜST</div>
            <div class="metric-label-sub">ALT İhtimali: <b>%{prob_under*100:.1f}</b> | Model Farkı: <b>{total_proj_pts - line_total:+.1f} Sayı</b></div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="pro-card">
            <span class="stat-badge badge-warning">HANDİKAP ({line_handicap:+.1f})</span>
            <div class="metric-value-huge" style="margin-top:10px; color:#fbbf24;">%{prob_home_cover*100:.1f}</div>
            <div class="metric-label-sub">Ev Sahibi Handikap Kaplama Olasılığı</div>
        </div>
        """, unsafe_allow_html=True)

    # DETAILS & STRATEGY
    sc1, sc2 = st.columns(2)

    with sc1:
        st.markdown(f"""
        <div class="pro-card">
            <h4 style="margin:0 0 15px 0; color:#fb923c;">⏱️ Yarı ve Periyot Projeksiyonları</h4>
            <table style="width:100%; font-size:14px;">
                <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px 0;">İlk Yarı Beklenen Skor</td><td style="text-align:right;"><b>{ht_home_pts:.1f} - {ht_away_pts:.1f}</b> (Toplam: {(ht_home_pts+ht_away_pts):.1f})</td></tr>
                <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px 0;">1. Periyot Beklenen Skor</td><td style="text-align:right;"><b>{q1_home_pts:.1f} - {q1_away_pts:.1f}</b> (Toplam: {(q1_home_pts+q1_away_pts):.1f})</td></tr>
                <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px 0;">Beklanan Maç Temposu (Pace)</td><td style="text-align:right;"><b>{exp_pace:.1f} Top Kullanımı</b></td></tr>
                <tr><td style="padding:8px 0;">Sayı Marjı (Margin)</td><td style="text-align:right;"><b style="color:#34d399;">{home_name if expected_margin > 0 else away_name} {abs(expected_margin):.1f} Fark Yapabilir</b></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with sc2:
        # Strategy logic
        if total_proj_pts > (line_total + 3.0):
            pick_total = f"TOPLAM SAYI ÜST {line_total} (Model Tahmini: {total_proj_pts:.1f})"
        elif total_proj_pts < (line_total - 3.0):
            pick_total = f"TOPLAM SAYI ALT {line_total} (Model Tahmini: {total_proj_pts:.1f})"
        else:
            pick_total = f"Çizgi Dengede ({line_total} civarı nötr)"

        if prob_home_cover > 0.58:
            pick_handicap = f"{home_name} {line_handicap:+.1f} Handikapı Kaplar"
        elif prob_away_cover > 0.58:
            pick_handicap = f"{away_name} {-line_handicap:+.1f} Handikapı Kaplar"
        else:
            pick_handicap = "Handikap Çizgisi Riskli/Başabaş"

        st.markdown(f"""
        <div class="pro-card">
            <h4 style="margin:0 0 15px 0; color:#34d399;">🛡️ Algoritmik Basketbol Stratejisi</h4>
            <div style="margin-bottom:12px;">
                <span class="stat-badge badge-success">SAYI LİMİTİ ÖNERİSİ</span>
                <p style="margin:5px 0 0 0; font-size:15px; font-weight:600; color:#ffffff;">{pick_total}</p>
            </div>
            <div style="margin-bottom:12px;">
                <span class="stat-badge badge-primary">HANDİKAP ÖNERİSİ</span>
                <p style="margin:5px 0 0 0; font-size:15px; font-weight:600; color:#ffffff;">{pick_handicap}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
