import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pro Football Engine - Mobile Edition", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="collapsed" # Mobilde varsayılan kapalı sidebar
)

# ---------------------------------------------------------
# MOBILE-FIRST CUSTOM STYLING (CSS)
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
    header[data-testid="stHeader"] { background: rgba(11, 15, 23, 0.9) !important; backdrop-filter: blur(8px); }
    footer { visibility: hidden; }

    /* Mobil için optimize edilmiş Card yapısı */
    .pro-card {
        background: linear-gradient(145deg, #131b2e 0%, #0f1623 100%);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .stat-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .badge-primary { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-success { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-warning { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-danger { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

    /* Mobilde Buton Boyutlandırma */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px 16px !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
    }

    /* Mobilde küçük ekranlar için yazı boyutu düzenlemesi */
    @media (max-width: 640px) {
        h1 { font-size: 22px !important; }
        h2 { font-size: 18px !important; }
        h3 { font-size: 16px !important; }
        .pro-card { padding: 10px; }
    }

    div[data-baseweb="input"] { background-color: #1a2332 !important; border-color: #334155 !important; border-radius: 8px !important; }
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR PARAMETERS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Lig & Model Ayarları")
    
    league_preset = st.selectbox("🏆 Lig Şablonu", ["Özel / Elle Gir", "Süper Lig (TR)", "Premier League (UK)", "La Liga (ES)", "Bundesliga (DE)"], key="league_preset")
    
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

    league_home_xg = st.number_input("Lig Ev Ort. Gol", min_value=0.1, max_value=4.0, value=default_h, step=0.05, key="l_h_xg")
    league_away_xg = st.number_input("Lig Dep Ort. Gol", min_value=0.1, max_value=4.0, value=default_a, step=0.05, key="l_a_xg")

    st.markdown("---")
    n_simulations = st.select_slider("Simülasyon Sayısı", options=[1000, 5000, 10000, 20000], value=10000, key="sim_cnt")
    bankroll = st.number_input("Kasa (₺)", min_value=100, value=10000, step=500, key="bankroll")
    use_dixon_coles = st.checkbox("Dixon-Coles Düzeltmesi", value=True, key="dc_check")
    rho = st.slider("Rho (Korelasyon)", -0.30, 0.0, -0.13, 0.01, key="rho_slider") if use_dixon_coles else 0.0

# ---------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------
st.markdown("""
<div style="text-align: center; padding-bottom: 10px;">
    <h1 style="margin:0; color: #ffffff; font-weight:800;">⚽ Football Analytics Pro</h1>
    <p style="margin:4px 0 0 0; color: #94a3b8; font-size: 13px;">Mobil Uyumlu & Visual Grafik Engine</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# INPUT FORM (MOBIL FRIENDLY)
# ---------------------------------------------------------
st.markdown("""<div class="pro-card">""", unsafe_allow_html=True)
st.markdown("""<span class="stat-badge badge-primary">Giriş Paneli</span>""", unsafe_allow_html=True)

col_h, col_a = st.columns(2)

with col_h:
    st.markdown("##### 🏠 Ev Sahibi")
    home_name = st.text_input("Takım", value="Beşiktaş", key="h_name")
    home_matches = st.number_input("Maç", min_value=1, value=10, key="hm_cnt")
    home_goals_scored = st.number_input("Attığı", min_value=0, value=20, key="hg_sc")
    home_goals_conceded = st.number_input("Yediği", min_value=0, value=8, key="hg_cc")
    home_missing = st.slider("Ev Eksik Etkisi %", 0, 30, 0, step=5)

with col_a:
    st.markdown("##### ✈️ Deplasman")
    away_name = st.text_input("Takım ", value="Trabzonspor", key="a_name")
    away_matches = st.number_input("Maç ", min_value=1, value=10, key="am_cnt")
    away_goals_scored = st.number_input("Attığı ", min_value=0, value=14, key="ag_sc")
    away_goals_conceded = st.number_input("Yediği ", min_value=0, value=13, key="ag_cc")
    away_missing = st.slider("Dep Eksik Etkisi %", 0, 30, 0, step=5)

home_att_avg = (home_goals_scored / home_matches) * (1 - (home_missing / 100))
home_def_avg = (home_goals_conceded / home_matches) * (1 + (home_missing / 200))
away_att_avg = (away_goals_scored / away_matches) * (1 - (away_missing / 100))
away_def_avg = (away_goals_conceded / away_matches) * (1 + (away_missing / 200))

st.markdown("##### 💰 Oranlar")
col_o1, col_o2, col_o3 = st.columns(3)
with col_o1: odds_ms1 = st.number_input("MS 1", min_value=1.0, value=2.10, step=0.05)
with col_o2: odds_ms0 = st.number_input("MS 0", min_value=1.0, value=3.25, step=0.05)
with col_o3: odds_ms2 = st.number_input("MS 2", min_value=1.0, value=3.10, step=0.05)

st.markdown("""</div>""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DIXON-COLES FUNCTION
# ---------------------------------------------------------
def dixon_coles_tau(h, a, xg_h, xg_a, rho_val):
    if not use_dixon_coles: return 1.0
    if h == 0 and a == 0: return 1.0 - (xg_h * xg_a * rho_val)
    elif h == 0 and a == 1: return 1.0 + (xg_h * rho_val)
    elif h == 1 and a == 0: return 1.0 + (xg_a * rho_val)
    elif h == 1 and a == 1: return 1.0 - rho_val
    else: return 1.0

# ---------------------------------------------------------
# RUN CALCULATION
# ---------------------------------------------------------
if st.button("🔥 ANALİZ ET & GRAFİKLERİ YÜKLE", use_container_width=True):
    
    # xG Hesapları
    home_attack_power = home_att_avg / league_home_xg if league_home_xg > 0 else 1.0
    home_defense_power = home_def_avg / league_home_xg if league_home_xg > 0 else 1.0
    away_attack_power = away_att_avg / league_away_xg if league_away_xg > 0 else 1.0
    away_defense_power = away_def_avg / league_away_xg if league_away_xg > 0 else 1.0

    xg_home = home_attack_power * away_defense_power * league_home_xg
    xg_away = away_attack_power * home_defense_power * league_away_xg
    total_xg = xg_home + xg_away

    iy_xg_home = xg_home * 0.45
    iy_xg_away = xg_away * 0.45

    # Monte Carlo Simülasyonu
    sim_home_goals = np.random.poisson(xg_home, n_simulations)
    sim_away_goals = np.random.poisson(xg_away, n_simulations)
    sim_total_goals = sim_home_goals + sim_away_goals

    sim_iy_home = np.random.poisson(iy_xg_home, n_simulations)
    sim_iy_away = np.random.poisson(iy_xg_away, n_simulations)

    p_sim_ms1 = np.sum(sim_home_goals > sim_away_goals) / n_simulations
    p_sim_ms0 = np.sum(sim_home_goals == sim_away_goals) / n_simulations
    p_sim_ms2 = np.sum(sim_home_goals < sim_away_goals) / n_simulations

    iy_res = np.where(sim_iy_home > sim_iy_away, 1, np.where(sim_iy_home == sim_iy_away, 0, 2))
    ms_res = np.where(sim_home_goals > sim_away_goals, 1, np.where(sim_home_goals == sim_away_goals, 0, 2))

    # Skorsal Matris (0-5 gol arası matris hazırlama)
    max_g = 6
    matrix = np.zeros((max_g, max_g))
    for h in range(max_g):
        for a in range(max_g):
            p_h = (math.pow(xg_home, h) * math.exp(-xg_home)) / math.factorial(h)
            p_a = (math.pow(xg_away, a) * math.exp(-xg_away)) / math.factorial(a)
            tau = dixon_coles_tau(h, a, xg_home, xg_away, rho)
            matrix[h, a] = p_h * p_a * tau
    matrix /= np.sum(matrix)

    # MATCH SUMMARY HEADER
    st.markdown("---")
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius:14px; padding:15px; border:1px solid #334155; text-align:center; margin-bottom:15px;">
        <h2 style="margin:0; color:#ffffff;">{home_name.upper()} vs {away_name.upper()}</h2>
        <p style="color:#94a3b8; font-size:13px; margin:5px 0 0 0;">
            xG: <b style="color:#38bdf8;">{xg_home:.2f}</b> - <b style="color:#f43f5e;">{xg_away:.2f}</b> | Toplam: <b style="color:#34d399;">{total_xg:.2f}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. VISUAL GRAPHICS (MOBİL BARS & HEATMAP)
    st.markdown("### 📊 Görsel Analiz & Grafikler")

    # A) TARAF OLASILIKLARI PASTA/BAR GRAFİĞİ
    fig_prob = go.Figure(data=[
        go.Bar(
            x=[home_name, "Beraberlik", away_name],
            y=[p_sim_ms1*100, p_sim_ms0*100, p_sim_ms2*100],
            text=[f"%{p_sim_ms1*100:.1f}", f"%{p_sim_ms0*100:.1f}", f"%{p_sim_ms2*100:.1f}"],
            textposition='auto',
            marker_color=['#3b82f6', '#f59e0b', '#ef4444']
        )
    ])
    fig_prob.update_layout(
        title="Maç Sonucu Olasılık Dağılımı (%)",
        template="plotly_dark",
        height=280,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_prob, use_container_width=True)

    # B) SKOR ISI HARİTASI (HEATMAP)
    fig_heatmap = px.imshow(
        matrix * 100,
        labels=dict(x=f"{away_name} Gol", y=f"{home_name} Gol", color="Olasılık (%)"),
        x=[str(i) for i in range(max_g)],
        y=[str(i) for i in range(max_g)],
        color_continuous_scale="Viridis",
        text_auto=".1f"
    )
    fig_heatmap.update_layout(
        title="Skor Matrisi Isı Haritası (%)",
        template="plotly_dark",
        height=330,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # 2. POPÜLER KOMBİNE PAZARLAR (KG VAR & 2.5 ÜST)
    st.markdown("### 🔥 KG Var & Alt/Üst Kombinasyonları")
    is_kg_var = (sim_home_goals > 0) & (sim_away_goals > 0)
    is_ust_25 = sim_total_goals > 2.5
    is_ust_15 = sim_total_goals > 1.5

    p_kg_var_25_ust = np.sum(is_kg_var & is_ust_25) / n_simulations
    p_kg_var_15_ust = np.sum(is_kg_var & is_ust_15) / n_simulations
    p_kg_var_25_alt = np.sum(is_kg_var & (~is_ust_25)) / n_simulations
    p_kg_yok_25_alt = np.sum((~is_kg_var) & (~is_ust_25)) / n_simulations

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class="pro-card" style="text-align:center;">
            <span class="stat-badge badge-success">POPÜLER</span>
            <h4 style="margin:5px 0; color:#fff;">KG Var & 2.5 Üst</h4>
            <h2 style="margin:2px 0; color:#34d399;">%{p_kg_var_25_ust*100:.1f}</h2>
            <p style="margin:0; color:#94a3b8; font-size:12px;">Adil: <b>{1/p_kg_var_25_ust if p_kg_var_25_ust>0 else 0:.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="pro-card" style="text-align:center;">
            <span class="stat-badge badge-primary">KOMBİNE</span>
            <h4 style="margin:5px 0; color:#fff;">KG Var & 1.5 Üst</h4>
            <h2 style="margin:2px 0; color:#60a5fa;">%{p_kg_var_15_ust*100:.1f}</h2>
            <p style="margin:0; color:#94a3b8; font-size:12px;">Adil: <b>{1/p_kg_var_15_ust if p_kg_var_15_ust>0 else 0:.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)

    m3, m4 = st.columns(2)
    with m3:
        st.markdown(f"""
        <div class="pro-card" style="text-align:center;">
            <span class="stat-badge badge-warning">KOMBİNE</span>
            <h4 style="margin:5px 0; color:#fff;">KG Var & 2.5 Alt</h4>
            <h2 style="margin:2px 0; color:#fbbf24;">%{p_kg_var_25_alt*100:.1f}</h2>
            <p style="margin:0; color:#94a3b8; font-size:12px;">Adil: <b>{1/p_kg_var_25_alt if p_kg_var_25_alt>0 else 0:.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="pro-card" style="text-align:center;">
            <span class="stat-badge badge-danger">KOMBİNE</span>
            <h4 style="margin:5px 0; color:#fff;">KG Yok & 2.5 Alt</h4>
            <h2 style="margin:2px 0; color:#f87171;">%{p_kg_yok_25_alt*100:.1f}</h2>
            <p style="margin:0; color:#94a3b8; font-size:12px;">Adil: <b>{1/p_kg_yok_25_alt if p_kg_yok_25_alt>0 else 0:.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)

    # 3. KELLY KASA DEĞER ANALİZİ
    st.markdown("### 💵 Kelly Value Bet Önerileri")
    def calc_kelly(prob, odds):
        val = (prob * odds) - 1.0
        if val <= 0: return 0.0, 0.0
        b = odds - 1.0
        fk = ((prob * b) - (1.0 - prob)) / b * 0.25
        return val, bankroll * max(0.0, fk)

    v1, s1 = calc_kelly(p_sim_ms1, odds_ms1)
    v0, s0 = calc_kelly(p_sim_ms0, odds_ms0)
    v2, s2 = calc_kelly(p_sim_ms2, odds_ms2)

    k_col1, k_col2, k_col3 = st.columns(3)
    with k_col1:
        st.markdown(f"<div class='pro-card'><b>MS 1:</b> {'<span class=\"badge-success\">DEĞERLİ</span>' if v1>0 else '<span class=\"badge-danger\">PAS</span>'}<br>Öneri: <b>{s1:.0f} ₺</b></div>", unsafe_allow_html=True)
    with k_col2:
        st.markdown(f"<div class='pro-card'><b>MS 0:</b> {'<span class=\"badge-success\">DEĞERLİ</span>' if v0>0 else '<span class=\"badge-danger\">PAS</span>'}<br>Öneri: <b>{s0:.0f} ₺</b></div>", unsafe_allow_html=True)
    with k_col3:
        st.markdown(f"<div class='pro-card'><b>MS 2:</b> {'<span class=\"badge-success\">DEĞERLİ</span>' if v2>0 else '<span class=\"badge-danger\">PAS</span>'}<br>Öneri: <b>{s2:.0f} ₺</b></div>", unsafe_allow_html=True)

    # 4. İY / MS MATRIX
    st.markdown("### 🔄 İY / MS Olasılıkları")
    iy_ms_combos = [
        ("1 / 1", (iy_res == 1) & (ms_res == 1)), ("X / 1", (iy_res == 0) & (ms_res == 1)), ("2 / 1", (iy_res == 2) & (ms_res == 1)),
        ("1 / X", (iy_res == 1) & (ms_res == 0)), ("X / X", (iy_res == 0) & (ms_res == 0)), ("2 / X", (iy_res == 2) & (ms_res == 0)),
        ("1 / 2", (iy_res == 1) & (ms_res == 2)), ("X / 2", (iy_res == 0) & (ms_res == 2)), ("2 / 2", (iy_res == 2) & (ms_res == 2))
    ]
    
    i_cols = st.columns(3)
    for idx, (lbl, cond) in enumerate(iy_ms_combos):
        pr = np.sum(cond) / n_simulations
        with i_cols[idx % 3]:
            st.markdown(f"<div class='pro-card' style='padding:8px; text-align:center;'><b>{lbl}</b><br><span style='color:#34d399;'>%{pr*100:.1f}</span></div>", unsafe_allow_html=True)

    # 5. TAKIM GOL PAZARLARI
    st.markdown("### ⚽ Takım Özel Golleri")
    tg1, tg2 = st.columns(2)
    with tg1:
        st.markdown(f"""
        <div class="pro-card">
            <b>🏠 {home_name}</b><br>
            • 1.5 Üst: <b>%{np.sum(sim_home_goals > 1.5)/n_simulations*100:.1f}</b><br>
            • 2.5 Üst: <b>%{np.sum(sim_home_goals > 2.5)/n_simulations*100:.1f}</b>
        </div>
        """, unsafe_allow_html=True)
    with tg2:
        st.markdown(f"""
        <div class="pro-card">
            <b>✈️ {away_name}</b><br>
            • 1.5 Üst: <b>%{np.sum(sim_away_goals > 1.5)/n_simulations*100:.1f}</b><br>
            • 2.5 Üst: <b>%{np.sum(sim_away_goals > 2.5)/n_simulations*100:.1f}</b>
        </div>
        """, unsafe_allow_html=True)
