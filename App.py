import streamlit as st
import math
import numpy as np

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

    st.markdown("---")
    st.markdown("#### 🎲 Simülasyon Ayarları")
    n_simulations = st.select_slider("Monte Carlo Simülasyon Sayısı", options=[1000, 5000, 10000, 20000, 50000], value=10000, key="sim_cnt")
    use_dixon_coles = st.checkbox("Dixon-Coles Düzeltmesi", value=True, key="dc_check")
    rho = st.slider("Dixon-Coles Korelasyonu (Rho)", -0.30, 0.0, -0.13, 0.01, key="rho_slider") if use_dixon_coles else 0.0

# ---------------------------------------------------------
# MAIN TITLE
# ---------------------------------------------------------
st.markdown("""
<div style="padding-bottom: 10px;">
    <h1 style="margin:0; font-size: 28px; font-weight: 800; color: #ffffff;">⚽ Professional Football Analytics Engine</h1>
    <p style="margin:4px 0 0 0; color: #94a3b8; font-size: 14px;">Gelişmiş İY/MS, Takım Golleri, Gol Aralığı ve Özel Pazar Analiz Motoru</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INPUT FORM
# ---------------------------------------------------------
st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
st.markdown("""<span class="stat-badge badge-primary">Gelişmiş Giriş</span> <h3 style="margin: 8px 0 15px 0;">Takım Verileri</h3>""", unsafe_allow_html=True)

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
    
    home_missing = st.slider("Ev Sahibi Kadro/Sakatlık Etkisi (%)", 0, 30, 0, step=5)

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
        
    away_missing = st.slider("Deplasman Kadro/Sakatlık Etkisi (%)", 0, 30, 0, step=5)

home_att_avg = (home_goals_scored / home_matches) * (1 - (home_missing / 100))
home_def_avg = (home_goals_conceded / home_matches) * (1 + (home_missing / 200))
away_att_avg = (away_goals_scored / away_matches) * (1 - (away_missing / 100))
away_def_avg = (away_goals_conceded / away_matches) * (1 + (away_missing / 200))

st.markdown("""</div>""", unsafe_allow_html=True)

if st.button("🔥 TÜM ÖZEL VE DETAYLI MARKETLERİ ANALİZ ET", use_container_width=True):
    
    # 1. xG HESAPLAMALARI
    home_attack_power = home_att_avg / league_home_xg if league_home_xg > 0 else 1.0
    home_defense_power = home_def_avg / league_home_xg if league_home_xg > 0 else 1.0
    away_attack_power = away_att_avg / league_away_xg if league_away_xg > 0 else 1.0
    away_defense_power = away_def_avg / league_away_xg if league_away_xg > 0 else 1.0

    xg_home = home_attack_power * away_defense_power * league_home_xg
    xg_away = away_attack_power * home_defense_power * league_away_xg
    total_xg = xg_home + xg_away

    iy_xg_home = xg_home * 0.45
    iy_xg_away = xg_away * 0.45

    # 2. MONTE CARLO SİMÜLASYONU
    sim_home_goals = np.random.poisson(xg_home, n_simulations)
    sim_away_goals = np.random.poisson(xg_away, n_simulations)
    sim_total_goals = sim_home_goals + sim_away_goals

    sim_iy_home = np.random.poisson(iy_xg_home, n_simulations)
    sim_iy_away = np.random.poisson(iy_xg_away, n_simulations)

    # İY Durumları (1, 0, 2)
    iy_res = np.where(sim_iy_home > sim_iy_away, 1, np.where(sim_iy_home == sim_iy_away, 0, 2))
    # MS Durumları (1, 0, 2)
    ms_res = np.where(sim_home_goals > sim_away_goals, 1, np.where(sim_home_goals == sim_away_goals, 0, 2))

    # HEADER DISPLAY
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius:16px; padding:25px; border:1px solid #334155; text-align:center; margin-bottom:25px;">
        <span class="stat-badge badge-primary">{n_simulations:,} SİMÜLE EDİLEN MAÇ RAPORU</span>
        <h2 style="font-size:30px; font-weight:800; margin: 10px 0 5px 0; color:#ffffff;">{home_name.upper()} vs {away_name.upper()}</h2>
        <p style="color:#94a3b8; font-size:15px; margin:0;">
            Model xG: <b style="color:#38bdf8;">{home_name}: {xg_home:.2f}</b> | <b style="color:#f43f5e;">{away_name}: {xg_away:.2f}</b> &nbsp;•&nbsp; Toplam xG: <b style="color:#34d399;">{total_xg:.2f}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. İY / MS KOMBİNASYONLARI (1/1, 1/X, 1/2, X/1 vs.)
    st.markdown("### 🔄 İY / MS (İlk Yarı / Maç Sonucu) Olasılıkları")
    
    iy_ms_combos = [
        ("1 / 1", (iy_res == 1) & (ms_res == 1)),
        ("X / 1", (iy_res == 0) & (ms_res == 1)),
        ("2 / 1", (iy_res == 2) & (ms_res == 1)),
        ("1 / X", (iy_res == 1) & (ms_res == 0)),
        ("X / X", (iy_res == 0) & (ms_res == 0)),
        ("2 / X", (iy_res == 2) & (ms_res == 0)),
        ("1 / 2", (iy_res == 1) & (ms_res == 2)),
        ("X / 2", (iy_res == 0) & (ms_res == 2)),
        ("2 / 2", (iy_res == 2) & (ms_res == 2))
    ]

    c_cols1 = st.columns(3)
    c_cols2 = st.columns(3)
    c_cols3 = st.columns(3)
    all_cols = c_cols1 + c_cols2 + c_cols3

    for idx, (label, cond) in enumerate(iy_ms_combos):
        prob = np.sum(cond) / n_simulations
        fair_odds = 1 / prob if prob > 0 else 0
        with all_cols[idx]:
            st.markdown(f"""
            <div class="pro-card" style="text-align:center; padding:12px;">
                <span class="stat-badge badge-primary">İY / MS</span>
                <h4 style="margin:5px 0; color:#ffffff;">{label}</h4>
                <p style="margin:0; color:#34d399; font-weight:700;">%{prob*100:.1f} <span style="font-weight:400; color:#94a3b8;">(Adil: {fair_odds:.2f})</span></p>
            </div>
            """, unsafe_allow_html=True)

    # 2. TAKIM GOL PAZARLARI (EV 1.5 ÜST, DEP 1.5 ÜST, İY DEP 1.5 ÜST VS.)
    st.markdown("### ⚽ Takım Özel Gol Pazarları (Ev Sahibi & Deplasman)")
    t1, t2 = st.columns(2)

    with t1:
        st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
        st.markdown(f"#### 🏠 {home_name} Özel Gol Pazarları")
        
        p_h_15 = np.sum(sim_home_goals > 1.5) / n_simulations
        p_h_25 = np.sum(sim_home_goals > 2.5) / n_simulations
        p_h_iy_15 = np.sum(sim_iy_home > 1.5) / n_simulations

        st.write(f"**Ev Sahibi 1.5 Üst:** %{p_h_15*100:.1f} *(Adil Oran: {1/p_h_15 if p_h_15>0 else 0:.2f})*")
        st.write(f"**Ev Sahibi 2.5 Üst:** %{p_h_25*100:.1f} *(Adil Oran: {1/p_h_25 if p_h_25>0 else 0:.2f})*")
        st.write(f"**Ev Sahibi İY 1.5 Üst:** %{p_h_iy_15*100:.1f} *(Adil Oran: {1/p_h_iy_15 if p_h_iy_15>0 else 0:.2f})*")
        st.markdown("""</div>""", unsafe_allow_html=True)

    with t2:
        st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
        st.markdown(f"#### ✈️ {away_name} Özel Gol Pazarları")
        
        p_a_15 = np.sum(sim_away_goals > 1.5) / n_simulations
        p_a_25 = np.sum(sim_away_goals > 2.5) / n_simulations
        p_a_iy_15 = np.sum(sim_iy_away > 1.5) / n_simulations

        st.write(f"**Deplasman 1.5 Üst:** %{p_a_15*100:.1f} *(Adil Oran: {1/p_a_15 if p_a_15>0 else 0:.2f})*")
        st.write(f"**Deplasman 2.5 Üst:** %{p_a_25*100:.1f} *(Adil Oran: {1/p_a_25 if p_a_25>0 else 0:.2f})*")
        st.write(f"**Deplasman İY 1.5 Üst:** %{p_a_iy_15*100:.1f} *(Adil Oran: {1/p_a_iy_15 if p_a_iy_15>0 else 0:.2f})*")
        st.markdown("""</div>""", unsafe_allow_html=True)

    # 3. TOPLAM GOL ARALIĞI PAZARLARI (0-1, 2-3, 4-5, 6+)
    st.markdown("### 📊 Toplam Gol Aralığı (TGA)")
    g1, g2, g3, g4 = st.columns(4)

    p_tg_01 = np.sum((sim_total_goals >= 0) & (sim_total_goals <= 1)) / n_simulations
    p_tg_23 = np.sum((sim_total_goals >= 2) & (sim_total_goals <= 3)) / n_simulations
    p_tg_45 = np.sum((sim_total_goals >= 4) & (sim_total_goals <= 5)) / n_simulations
    p_tg_6plus = np.sum(sim_total_goals >= 6) / n_simulations

    with g1:
        st.markdown(f"""
        <div class="pro-card" style="text-align:center;">
            <span class="stat-badge badge-warning">0 - 1 GOL</span>
            <h3 style="margin:10px 0; color:#fbbf24;">%{p_tg_01*100:.1f}</h3>
            <p style="color:#94a3b8; margin:0;">Adil: {1/p_tg_01 if p_tg_01>0 else 0:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown(f"""
        <div class="pro-card" style="text-align:center;">
            <span class="stat-badge badge-success">2 - 3 GOL</span>
            <h3 style="margin:10px 0; color:#34d399;">%{p_tg_23*100:.1f}</h3>
            <p style="color:#94a3b8; margin:0;">Adil: {1/p_tg_23 if p_tg_23>0 else 0:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with g3:
        st.markdown(f"""
        <div class="pro-card" style="text-align:center;">
            <span class="stat-badge badge-primary">4 - 5 GOL</span>
            <h3 style="margin:10px 0; color:#60a5fa;">%{p_tg_45*100:.1f}</h3>
            <p style="color:#94a3b8; margin:0;">Adil: {1/p_tg_45 if p_tg_45>0 else 0:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with g4:
        st.markdown(f"""
        <div class="pro-card" style="text-align:center;">
            <span class="stat-badge badge-danger">6+ GOL</span>
            <h3 style="margin:10px 0; color:#f87171;">%{p_tg_6plus*100:.1f}</h3>
            <p style="color:#94a3b8; margin:0;">Adil: {1/p_tg_6plus if p_tg_6plus>0 else 0:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
