import streamlit as st
import math

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pro Football Analytics Engine - Ultimate Edition", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM STYLING
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f17 !important;
        color: #e2e8f0 !important;
    }
    .stApp { background-color: #0b0f17 !important; }
    header[data-testid="stHeader"] { background: rgba(11, 15, 23, 0.8) !important; backdrop-filter: blur(8px); }
    footer { visibility: hidden; }

    .pro-card {
        background: linear-gradient(145deg, #131b2e 0%, #0f1623 100%);
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
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
    .badge-danger { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

    .stButton > button {
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

    div[data-baseweb="input"] { background-color: #1a2332 !important; border-color: #334155 !important; border-radius: 8px !important; color: #ffffff !important; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR PARAMETERS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Lig Parametreleri")
    
    league_preset = st.selectbox("🏆 Hazır Lig Şablonu", ["Özel / Elle Gir", "Süper Lig (TR)", "Premier League (UK)", "La Liga (ES)", "Bundesliga (DE)"], key="league_preset")
    
    if league_preset == "Süper Lig (TR)":
        default_h, default_a, default_cor = 1.55, 1.25, 9.5
    elif league_preset == "Premier League (UK)":
        default_h, default_a, default_cor = 1.58, 1.32, 10.2
    elif league_preset == "La Liga (ES)":
        default_h, default_a, default_cor = 1.42, 1.12, 9.1
    elif league_preset == "Bundesliga (DE)":
        default_h, default_a, default_cor = 1.70, 1.40, 9.8
    else:
        default_h, default_a, default_cor = 1.50, 1.20, 9.5

    league_home_xg = st.number_input("Lig İç Saha Gol Ort.", min_value=0.1, max_value=4.0, value=default_h, step=0.05, key="l_h_xg")
    league_away_xg = st.number_input("Lig Dış Saha Gol Ort.", min_value=0.1, max_value=4.0, value=default_a, step=0.05, key="l_a_xg")
    league_corner_avg = st.number_input("Lig Korner Ortalaması", min_value=5.0, max_value=15.0, value=default_cor, step=0.5, key="l_cor")

    st.markdown("---")
    st.markdown("#### 🧮 Model & Kasa Ayarları")
    bankroll = st.number_input("Toplam Bahis Kasası (₺)", min_value=100, value=10000, step=500, key="bankroll")
    use_dixon_coles = st.checkbox("Dixon-Coles Düzeltmesi", value=True, key="dc_check")
    rho = st.slider("Dixon-Coles Korelasyonu (Rho)", -0.30, 0.0, -0.13, 0.01, key="rho_slider") if use_dixon_coles else 0.0

# ---------------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------------
st.markdown("""
<div style="padding-bottom: 10px;">
    <h1 style="margin:0; font-size: 28px; font-weight: 800; color: #ffffff;">⚽ Professional Football Analytics Engine</h1>
    <p style="margin:4px 0 0 0; color: #94a3b8; font-size: 14px;">Gelişmiş Poisson, Kelly Kriteri & Kadro Etki Modeli</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INPUT FORM
# ---------------------------------------------------------
st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
st.markdown("""<span class="stat-badge badge-primary">Gelişmiş Giriş</span> <h3 style="margin: 8px 0 15px 0;">Takım ve Kadro Durum Verileri</h3>""", unsafe_allow_html=True)

col_h, col_a = st.columns(2)

with col_h:
    st.markdown("#### 🏠 Ev Sahibi Takım")
    home_name = st.text_input("Takım Adı", value="Beşiktaş", key="h_name")
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        home_matches = st.number_input("Oynadığı Maç", min_value=1, value=10, step=1, key="hm_cnt")
    with col_h2:
        home_goals_scored = st.number_input("Attığı Gol", min_value=0, value=20, step=1, key="hg_sc")
    with col_h3:
        home_goals_conceded = st.number_input("Yediği Gol", min_value=0, value=8, step=1, key="hg_cc")
    
    home_missing = st.slider("Ev Sahibi Kadro/Sakatlık Eksik Etkisi (%)", 0, 30, 0, step=5, help="Takımın önemli eksiklerine göre güç düşüşü %'si")

with col_a:
    st.markdown("#### ✈️ Deplasman Takımı")
    away_name = st.text_input("Takım Adı ", value="Trabzonspor", key="a_name")
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        away_matches = st.number_input("Oynadığı Maç ", min_value=1, value=10, step=1, key="am_cnt")
    with col_a2:
        away_goals_scored = st.number_input("Attığı Gol ", min_value=0, value=14, step=1, key="ag_sc")
    with col_a3:
        away_goals_conceded = st.number_input("Yediği Gol ", min_value=0, value=13, step=1, key="ag_cc")
        
    away_missing = st.slider("Deplasman Kadro/Sakatlık Eksik Etkisi (%)", 0, 30, 0, step=5, help="Takımın önemli eksiklerine göre güç düşüşü %'si")

home_att_avg = (home_goals_scored / home_matches) * (1 - (home_missing / 100))
home_def_avg = (home_goals_conceded / home_matches) * (1 + (home_missing / 200)) # Eksik savunmayı zayıflatır
away_att_avg = (away_goals_scored / away_matches) * (1 - (away_missing / 100))
away_def_avg = (away_goals_conceded / away_matches) * (1 + (away_missing / 200))

st.markdown("""<hr style="margin: 15px 0 !important;">""", unsafe_allow_html=True)
st.markdown("#### 💰 Oranlar & Value Bet Analizi")

col_o1, col_o2, col_o3 = st.columns(3)
with col_o1:
    odds_ms1 = st.number_input("MS 1 Oranı", min_value=1.0, value=2.10, step=0.05, key="o_ms1")
with col_o2:
    odds_ms0 = st.number_input("MS 0 Oranı", min_value=1.0, value=3.25, step=0.05, key="o_ms0")
with col_o3:
    odds_ms2 = st.number_input("MS 2 Oranı", min_value=1.0, value=3.10, step=0.05, key="o_ms2")

st.markdown("""</div>""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ENGINE & CALCULATIONS
# ---------------------------------------------------------
def dixon_coles_tau(h, a, xg_h, xg_a, rho_val):
    if not use_dixon_coles: return 1.0
    if h == 0 and a == 0: return 1.0 - (xg_h * xg_a * rho_val)
    elif h == 0 and a == 1: return 1.0 + (xg_h * rho_val)
    elif h == 1 and a == 0: return 1.0 + (xg_a * rho_val)
    elif h == 1 and a == 1: return 1.0 - rho_val
    else: return 1.0

if st.button("🔥 MAÇI KUSURSUZ MODEL İLE ANALİZ ET", use_container_width=True):
    
    # 1. KORREKTE XG POISSON HESAPLAMASI
    home_attack_power = home_att_avg / league_home_xg if league_home_xg > 0 else 1.0
    home_defense_power = home_def_avg / league_home_xg if league_home_xg > 0 else 1.0
    away_attack_power = away_att_avg / league_away_xg if league_away_xg > 0 else 1.0
    away_defense_power = away_def_avg / league_away_xg if league_away_xg > 0 else 1.0

    xg_home = home_attack_power * away_defense_power * league_home_xg
    xg_away = away_attack_power * home_defense_power * league_away_xg
    total_xg = xg_home + xg_away

    # 2. MATRIX HESAPLAMA
    matrix = {}
    for h in range(7):
        for a in range(7):
            p_h = (math.pow(xg_home, h) * math.exp(-xg_home)) / math.factorial(h)
            p_a = (math.pow(xg_away, a) * math.exp(-xg_away)) / math.factorial(a)
            tau = dixon_coles_tau(h, a, xg_home, xg_away, rho)
            matrix[(h, a)] = p_h * p_a * tau

    total_p = sum(matrix.values())
    for k in matrix: matrix[k] /= total_p

    # 3. MAÇ SONUCU VE ALT/ÜST OLASILIKLARI
    p_ms1 = sum(p for (h, a), p in matrix.items() if h > a)
    p_ms0 = sum(p for (h, a), p in matrix.items() if h == a)
    p_ms2 = sum(p for (h, a), p in matrix.items() if h < a)

    p_alt15 = sum(p for (h, a), p in matrix.items() if h + a < 1.5)
    p_ust15 = 1.0 - p_alt15
    p_alt25 = sum(p for (h, a), p in matrix.items() if h + a < 2.5)
    p_ust25 = 1.0 - p_alt25
    p_alt35 = sum(p for (h, a), p in matrix.items() if h + a < 3.5)
    p_ust35 = 1.0 - p_alt35
    
    p_kgvar = sum(p for (h, a), p in matrix.items() if h > 0 and a > 0)
    p_kgyok = 1.0 - p_kgvar

    # İLK YARI GOL OLASILIĞI (Yaklaşık Poisson parametresi xG'nin %45'i)
    iy_total_xg = total_xg * 0.45
    p_iy_05_ust = 1.0 - math.exp(-iy_total_xg)

    # KORNER TAHMİNİ (xG Temelli Korner Endeksi)
    est_corners = league_corner_avg * (total_xg / (league_home_xg + league_away_xg))

    # 4. KELLY KRİTERİ & VALUE BET
    def calc_kelly(prob, odds):
        value = (prob * odds) - 1.0
        if value <= 0: return 0.0, 0.0
        b = odds - 1.0
        fractional_kelly = ((prob * b) - (1.0 - prob)) / b * 0.25 # Fractional %25
        stake = bankroll * max(0.0, fractional_kelly)
        return value, stake

    val1, stake1 = calc_kelly(p_ms1, odds_ms1)
    val0, stake0 = calc_kelly(p_ms0, odds_ms0)
    val2, stake2 = calc_kelly(p_ms2, odds_ms2)

    # REPORT HEADER
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius:16px; padding:25px; border:1px solid #334155; text-align:center; margin-bottom:25px;">
        <span class="stat-badge badge-primary">ANALİZ VE TAHMİN RAPORU</span>
        <h2 style="font-size:30px; font-weight:800; margin: 10px 0 5px 0; color:#ffffff;">{home_name.upper()} vs {away_name.upper()}</h2>
        <p style="color:#94a3b8; font-size:15px; margin:0;">
            Model xG: <b style="color:#38bdf8;">{home_name}: {xg_home:.2f}</b> | <b style="color:#f43f5e;">{away_name}: {xg_away:.2f}</b> &nbsp;•&nbsp; Toplam xG: <b style="color:#34d399;">{total_xg:.2f}</b> &nbsp;•&nbsp; Est. Korner: <b style="color:#fbbf24;">{est_corners:.1f}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 5. KELLY KASA YÖNETİMİ BÖLÜMÜ (YENİ KUSURSUZ ÖZELLİK)
    st.markdown("### 💵 Kelly Kriteri ile Değerli Bahis & Kasa Yönetimi")
    col_k1, col_k2, col_k3 = st.columns(3)

    with col_k1:
        st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
        st.markdown(f"#### MS 1 ({home_name})")
        if val1 > 0:
            st.markdown(f"""<span class="stat-badge badge-success">DEĞERLİ (+%{val1*100:.1f})</span>""", unsafe_allow_html=True)
            st.markdown(f"<h3 style='margin:10px 0; color:#34d399;'>Önerilen Bahis: {stake1:.1f} ₺</h3>", unsafe_allow_html=True)
            st.write(f"Kasa Payı: %{(stake1/bankroll)*100:.2f}")
        else:
            st.markdown("""<span class="stat-badge badge-danger">DEĞERSİZ (PAS)</span>""", unsafe_allow_html=True)
            st.markdown("<h3 style='margin:10px 0; color:#94a3b8;'>0 ₺</h3>", unsafe_allow_html=True)
            st.write("Oran risk/kazanç dengesi altında.")
        st.markdown("""</div>""", unsafe_allow_html=True)

    with col_k2:
        st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
        st.markdown("#### MS 0 (Beraberlik)")
        if val0 > 0:
            st.markdown(f"""<span class="stat-badge badge-success">DEĞERLİ (+%{val0*100:.1f})</span>""", unsafe_allow_html=True)
            st.markdown(f"<h3 style='margin:10px 0; color:#34d399;'>Önerilen Bahis: {stake0:.1f} ₺</h3>", unsafe_allow_html=True)
            st.write(f"Kasa Payı: %{(stake0/bankroll)*100:.2f}")
        else:
            st.markdown("""<span class="stat-badge badge-danger">DEĞERSİZ (PAS)</span>""", unsafe_allow_html=True)
            st.markdown("<h3 style='margin:10px 0; color:#94a3b8;'>0 ₺</h3>", unsafe_allow_html=True)
            st.write("Oran risk/kazanç dengesi altında.")
        st.markdown("""</div>""", unsafe_allow_html=True)

    with col_k3:
        st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
        st.markdown(f"#### MS 2 ({away_name})")
        if val2 > 0:
            st.markdown(f"""<span class="stat-badge badge-success">DEĞERLİ (+%{val2*100:.1f})</span>""", unsafe_allow_html=True)
            st.markdown(f"<h3 style='margin:10px 0; color:#34d399;'>Önerilen Bahis: {stake2:.1f} ₺</h3>", unsafe_allow_html=True)
            st.write(f"Kasa Payı: %{(stake2/bankroll)*100:.2f}")
        else:
            st.markdown("""<span class="stat-badge badge-danger">DEĞERSİZ (PAS)</span>""", unsafe_allow_html=True)
            st.markdown("<h3 style='margin:10px 0; color:#94a3b8;'>0 ₺</h3>", unsafe_allow_html=True)
            st.write("Oran risk/kazanç dengesi altında.")
        st.markdown("""</div>""", unsafe_allow_html=True)

    # 6. DETAYLI İSTATİSTİKLER VE DİĞER PAZARLAR
    st.markdown("### 📊 Detaylı Olasılık Dağılımları & İY / Korner")
    col_m1, col_m2, col_m3 = st.columns(3)

    with col_m1:
        st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
        st.markdown("#### 🎯 Maç Sonucu (1X2)")
        st.write(f"**MS 1 ({home_name}):** %{p_ms1*100:.1f} *(Adil Oran: {1/p_ms1:.2f})*")
        st.write(f"**MS 0 (Beraberlik):** %{p_ms0*100:.1f} *(Adil Oran: {1/p_ms0:.2f})*")
        st.write(f"**MS 2 ({away_name}):** %{p_ms2*100:.1f} *(Adil Oran: {1/p_ms2:.2f})*")
        st.markdown("""</div>""", unsafe_allow_html=True)

    with col_m2:
        st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
        st.markdown("#### ⚽ Alt / Üst Olasılıkları")
        st.write(f"**1.5 Üst:** %{p_ust15*100:.1f} | **1.5 Alt:** %{p_alt15*100:.1f}")
        st.write(f"**2.5 Üst:** %{p_ust25*100:.1f} | **2.5 Alt:** %{p_alt25*100:.1f}")
        st.write(f"**3.5 Üst:** %{p_ust35*100:.1f} | **3.5 Alt:** %{p_alt35*100:.1f}")
        st.markdown("""</div>""", unsafe_allow_html=True)

    with col_m3:
        st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
        st.markdown("#### ⏱️ İY & Korner Pazarları")
        st.write(f"**İlk Yarı 0.5 Üst:** %{p_iy_05_ust*100:.1f}")
        st.write(f"**KG Var:** %{p_kgvar*100:.1f} | **KG Yok:** %{p_kgyok*100:.1f}")
        st.write(f"**Beklenen Korner:** {est_corners:.1f}")
        st.markdown("""</div>""", unsafe_allow_html=True)

    # 7. EN OLASI SKORLAR
    st.markdown("### 🎲 En Olası 5 Skor Tahmini")
    top_scores = sorted(matrix.items(), key=lambda x: x[1], reverse=True)[:5]
    
    score_cols = st.columns(5)
    for idx, ((h, a), prob) in enumerate(top_scores):
        with score_cols[idx]:
            st.markdown(f"""
            <div class="pro-card" style="text-align:center; padding:15px;">
                <span class="stat-badge badge-primary">#{idx+1} Skor</span>
                <h3 style="margin:10px 0 5px 0; font-size:24px;">{h} - {a}</h3>
                <p style="margin:0; color:#34d399; font-weight:700;">%{prob*100:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
