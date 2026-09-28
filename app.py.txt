import streamlit as st
import math

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pro Football Analytics & Predictive Engine", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ADVANCED CUSTOM STYLING (DARK ULTRA-PRO THEME)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f17 !important;
        color: #e2e8f0 !important;
    }

    .stApp {
        background-color: #0b0f17 !important;
    }

    /* Hide Header / Footer clutter */
    header[data-testid="stHeader"] { background: rgba(11, 15, 23, 0.8) !important; backdrop-filter: blur(8px); }
    footer { visibility: hidden; }

    /* Custom Cards & Panels */
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
        border-color: #3b82f6;
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

    /* Metric Display */
    .metric-value-huge {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #60a5fa, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label-sub {
        font-size: 12px;
        color: #94a3b8;
        font-weight: 500;
        margin-top: 2px;
    }

    /* Heatmap Table Styling */
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
        transition: all 0.2s;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 14px 20px !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1d4ed8 0%, #1e40af 100%) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.6) !important;
        transform: translateY(-2px);
    }

    /* Inputs Customization */
    div[data-baseweb="input"] {
        background-color: #1a2332 !important;
        border-color: #334155 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #3b82f6 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Custom Divider */
    hr {
        border-color: #1e293b !important;
        margin: 25px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR - CONFIGURATION & PARAMETERS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Analiz Parametreleri")
    
    st.markdown("#### 🏆 Lig Ortalamaları")
    league_home_xg = st.number_input("Lig İç Saha Gol Ort.", min_value=0.5, max_value=3.5, value=1.50, step=0.05, help="Ligteki tüm ev sahiplerinin maç başı ortalama golü.")
    league_away_xg = st.number_input("Lig Dış Saha Gol Ort.", min_value=0.5, max_value=3.5, value=1.20, step=0.05, help="Ligteki tüm deplasman takımlarının maç başı ortalama golü.")
    
    st.markdown("---")
    st.markdown("#### 🧮 Model Ayarları")
    use_dixon_coles = st.checkbox("Dixon-Coles Düzeltmesi (0-0, 1-0, 0-1, 1-1)", value=True)
    rho = st.slider("Dixon-Coles Korelasyonu (Rho)", -0.30, 0.0, -0.13, 0.01) if use_dixon_coles else 0.0

    st.markdown("---")
    st.caption("🔥 Pro Poisson Engine v3.5 | Professional Betting Analytics")

# ---------------------------------------------------------
# MAIN HEADER
# ---------------------------------------------------------
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 10px;">
    <div>
        <h1 style="margin:0; font-size: 28px; font-weight: 800; color: #ffffff;">⚽ Professional Football Analytics Engine</h1>
        <p style="margin:4px 0 0 0; color: #94a3b8; font-size: 14px;">Gelişmiş xG & Poisson Modeli ile Maç ve Oran Analiz Platformu</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# INPUT FORM (DIRECT ENTRY SYSTEM)
# ---------------------------------------------------------
st.markdown("<div class="pro-card">", unsafe_allow_html=True)
st.markdown("<span class="stat-badge badge-primary">Girdi Ekranı</span> <h3 style="margin: 8px 0 15px 0;">Takım ve Metrik Bilgileri (Doğrudan Ortalamalar)</h3>", unsafe_allow_html=True)

col_h, col_a = st.columns(2)

with col_h:
    st.markdown("#### 🏠 Ev Sahibi Takım")
    home_name = st.text_input("Ev Sahibi Adı", value="Beşiktaş", key="h_name")
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        home_att = st.number_input(f"{home_name} Attığı Gol (Maç Başı)", min_value=0.0, max_value=5.0, value=2.00, step=0.05, help="Ev sahibinin iç sahadaki maç başı ortalama gol sayısı.")
    with col_h2:
        home_def = st.number_input(f"{home_name} Yediği Gol (Maç Başı)", min_value=0.0, max_value=5.0, value=0.75, step=0.05, help="Ev sahibinin iç sahadaki maç başı ortalama yediği gol.")

with col_a:
    st.markdown("#### ✈️ Deplasman Takımı")
    away_name = st.text_input("Deplasman Adı", value="Trabzonspor", key="a_name")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        away_att = st.number_input(f"{away_name} Attığı Gol (Maç Başı)", min_value=0.0, max_value=5.0, value=1.38, step=0.05, help="Deplasmanın dış sahadaki maç başı ortalama gol sayısı.")
    with col_a2:
        away_def = st.number_input(f"{away_name} Yediği Gol (Maç Başı)", min_value=0.0, max_value=5.0, value=1.25, step=0.05, help="Deplasmanın dış sahadaki maç başı ortalama yediği gol.")

st.markdown("<hr style="margin: 15px 0 !important;">", unsafe_allow_html=True)
st.markdown("#### 💰 Büro Oranları (Value Bet Analizi İçin - İsteğe Bağlı)")

col_o1, col_o2, col_o3 = st.columns(3)
with col_o1:
    odds_ms1 = st.number_input("MS 1 Oranı", min_value=1.0, value=2.10, step=0.05)
with col_o2:
    odds_ms0 = st.number_input("MS 0 Oranı", min_value=1.0, value=3.25, step=0.05)
with col_o3:
    odds_ms2 = st.number_input("MS 2 Oranı", min_value=1.0, value=3.10, step=0.05)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# POISSON & DIXON-COLES ENGINE
# ---------------------------------------------------------
def dixon_coles_tau(h, a, xg_h, xg_a, rho_val):
    if not use_dixon_coles:
        return 1.0
    if h == 0 and a == 0:
        return 1.0 - (xg_h * xg_a * rho_val)
    elif h == 0 and a == 1:
        return 1.0 + (xg_h * rho_val)
    elif h == 1 and a == 0:
        return 1.0 + (xg_a * rho_val)
    elif h == 1 and a == 1:
        return 1.0 - rho_val
    else:
        return 1.0

if st.button("🔥 MAÇI DETAYLI ANALİZ ET VE MODELİ ÇALIŞTIR", use_container_width=True):
    
    # xG Hesaplama (İç/Dış Saha Güç Endeksi)
    home_attack_power = home_att / league_home_xg if league_home_xg > 0 else 1.0
    home_defense_power = home_def / league_away_xg if league_away_xg > 0 else 1.0
    
    away_attack_power = away_att / league_away_xg if league_away_xg > 0 else 1.0
    away_defense_power = away_def / league_home_xg if league_home_xg > 0 else 1.0

    xg_home = home_attack_power * away_defense_power * league_home_xg
    xg_away = away_attack_power * home_defense_power * league_away_xg
    total_xg = xg_home + xg_away

    # Matris ve Olasılık Hesabı (6x6)
    matrix = {}
    for h in range(7):
        for a in range(7):
            p_h = (math.pow(xg_home, h) * math.exp(-xg_home)) / math.factorial(h)
            p_a = (math.pow(xg_away, a) * math.exp(-xg_away)) / math.factorial(a)
            tau = dixon_coles_tau(h, a, xg_home, xg_away, rho)
            matrix[(h, a)] = p_h * p_a * tau

    # Normalize Etme
    total_p = sum(matrix.values())
    for k in matrix:
        matrix[k] /= total_p

    # Maç Sonucu
    p_ms1 = sum(p for (h, a), p in matrix.items() if h > a)
    p_ms0 = sum(p for (h, a), p in matrix.items() if h == a)
    p_ms2 = sum(p for (h, a), p in matrix.items() if h < a)

    # Çifte Şans
    p_1x = p_ms1 + p_ms0
    p_x2 = p_ms0 + p_ms2
    p_12 = p_ms1 + p_ms2

    # Gol Limitleri
    p_alt15 = sum(p for (h, a), p in matrix.items() if h + a < 1.5)
    p_ust15 = 1.0 - p_alt15
    
    p_alt25 = sum(p for (h, a), p in matrix.items() if h + a < 2.5)
    p_ust25 = 1.0 - p_alt25
    
    p_alt35 = sum(p for (h, a), p in matrix.items() if h + a < 3.5)
    p_ust35 = 1.0 - p_alt35

    # Karşılıklı Gol
    p_kgvar = sum(p for (h, a), p in matrix.items() if h > 0 and a > 0)
    p_kgyok = 1.0 - p_kgvar

    # Kombineler
    p_ms1_ust25 = sum(p for (h, a), p in matrix.items() if h > a and (h + a) > 2.5)
    p_ms1_kgvar = sum(p for (h, a), p in matrix.items() if h > a and a > 0)
    p_ms2_ust25 = sum(p for (h, a), p in matrix.items() if h < a and (h + a) > 2.5)
    p_ms2_kgvar = sum(p for (h, a), p in matrix.items() if h < a and h > 0)
    p_kgvar_ust25 = sum(p for (h, a), p in matrix.items() if h > 0 and a > 0 and (h + a) > 2.5)

    # Adil Oranlar
    fair_ms1 = 1.0 / p_ms1 if p_ms1 > 0 else 0
    fair_ms0 = 1.0 / p_ms0 if p_ms0 > 0 else 0
    fair_ms2 = 1.0 / p_ms2 if p_ms2 > 0 else 0

    # Value Beklentisi
    val_ms1 = (p_ms1 * odds_ms1) - 1.0
    val_ms0 = (p_ms0 * odds_ms0) - 1.0
    val_ms2 = (p_ms2 * odds_ms2) - 1.0

    # Top 4 En Olası Skorlar
    top_scores = sorted(matrix.items(), key=lambda x: x[1], reverse=True)[:4]

    # ---------------------------------------------------------
    # DISPLAY DASHBOARD
    # ---------------------------------------------------------
    st.markdown("---")
    
    # HEADER DASHBOARD
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius:16px; padding:25px; border:1px solid #334155; text-align:center; margin-bottom:25px;">
        <span class="stat-badge badge-primary">MAÇ DOKÜMANI VE MODEL SONUCU</span>
        <h2 style="font-size:30px; font-weight:800; margin: 10px 0 5px 0; color:#ffffff;">{home_name.upper()} vs {away_name.upper()}</h2>
        <p style="color:#94a3b8; font-size:15px; margin:0;">
            Model Beklenen Goller (xG): <b style="color:#38bdf8;">{home_name}: {xg_home:.2f}</b> | <b style="color:#f43f5e;">{away_name}: {xg_away:.2f}</b> &nbsp;•&nbsp; Toplam xG: <b style="color:#34d399;">{total_xg:.2f}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # SECTION 1: MS & ADİL ORANLAR
    st.markdown("### 🏆 1. Maç Sonucu Olasılıkları ve Adil Oranlar")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
        <div class="pro-card" style="border-top: 4px solid #3b82f6;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="stat-badge badge-primary">MS 1</span>
                <span style="font-size:12px; color:#94a3b8;">{home_name}</span>
            </div>
            <div class="metric-value-huge" style="margin-top:10px;">%{p_ms1*100:.1f}</div>
            <div class="metric-label-sub">Adil Oran: <b style="color:#38bdf8;">{fair_ms1:.2f}</b> | Büro: <b>{odds_ms1:.2f}</b></div>
            <div style="margin-top:10px; font-size:12px; color:{'#34d399' if val_ms1 > 0.03 else '#94a3b8'};">
                Value (Değer): <b>%{val_ms1*100:+.1f}</b> {'🔥 (DEĞERLİ)' if val_ms1 > 0.03 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="pro-card" style="border-top: 4px solid #f59e0b;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="stat-badge badge-warning">MS 0</span>
                <span style="font-size:12px; color:#94a3b8;">BERABERLİK</span>
            </div>
            <div class="metric-value-huge" style="margin-top:10px; color:#f59e0b;">%{p_ms0*100:.1f}</div>
            <div class="metric-label-sub">Adil Oran: <b style="color:#fbbf24;">{fair_ms0:.2f}</b> | Büro: <b>{odds_ms0:.2f}</b></div>
            <div style="margin-top:10px; font-size:12px; color:{'#34d399' if val_ms0 > 0.03 else '#94a3b8'};">
                Value (Değer): <b>%{val_ms0*100:+.1f}</b> {'🔥 (DEĞERLİ)' if val_ms0 > 0.03 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="pro-card" style="border-top: 4px solid #f43f5e;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="stat-badge" style="background:rgba(244,63,94,0.15); color:#f43f5e; border:1px solid rgba(244,63,94,0.3);">MS 2</span>
                <span style="font-size:12px; color:#94a3b8;">{away_name}</span>
            </div>
            <div class="metric-value-huge" style="margin-top:10px; color:#f43f5e;">%{p_ms2*100:.1f}</div>
            <div class="metric-label-sub">Adil Oran: <b style="color:#fda4af;">{fair_ms2:.2f}</b> | Büro: <b>{odds_ms2:.2f}</b></div>
            <div style="margin-top:10px; font-size:12px; color:{'#34d399' if val_ms2 > 0.03 else '#94a3b8'};">
                Value (Değer): <b>%{val_ms2*100:+.1f}</b> {'🔥 (DEĞERLİ)' if val_ms2 > 0.03 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # SECTION 2: GOL ANALİZLERİ & KOMBİNELER
    st.markdown("### ⚽ 2. Gol Limitleri ve Kombine Tahminler")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("""
        <div class="pro-card">
            <h4 style="margin:0 0 15px 0; color:#38bdf8;">📊 Gol Alt / Üst Matrisi</h4>
            <table style="width:100%; font-size:14px;">
                <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px 0;">1.5 Alt / Üst</td><td style="text-align:right;"><b>%{p_alt15*100:.1f}</b> / <b style="color:#34d399;">%{p_ust15*100:.1f}</b></td></tr>
                <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px 0;">2.5 Alt / Üst</td><td style="text-align:right;"><b>%{p_alt25*100:.1f}</b> / <b style="color:#34d399;">%{p_ust25*100:.1f}</b></td></tr>
                <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px 0;">3.5 Alt / Üst</td><td style="text-align:right;"><b>%{p_alt35*100:.1f}</b> / <b style="color:#34d399;">%{p_ust35*100:.1f}</b></td></tr>
                <tr><td style="padding:8px 0;">KG Var / Yok</td><td style="text-align:right;"><b style="color:#34d399;">%{p_kgvar*100:.1f}</b> / <b>%{p_kgyok*100:.1f}</b></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_g2:
        st.markdown(f"""
        <div class="pro-card">
            <h4 style="margin:0 0 15px 0; color:#fbbf24;">🎯 Özel Kombinasyon İhtimalleri</h4>
            <table style="width:100%; font-size:14px;">
                <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px 0;">MS 1 & 2.5 Üst</td><td style="text-align:right;"><b style="color:#60a5fa;">%{p_ms1_ust25*100:.1f}</b></td></tr>
                <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px 0;">MS 1 & KG Var</td><td style="text-align:right;"><b style="color:#60a5fa;">%{p_ms1_kgvar*100:.1f}</b></td></tr>
                <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px 0;">MS 2 & 2.5 Üst</td><td style="text-align:right;"><b style="color:#f43f5e;">%{p_ms2_ust25*100:.1f}</b></td></tr>
                <tr style="border-bottom:1px solid #1e293b;"><td style="padding:8px 0;">MS 2 & KG Var</td><td style="text-align:right;"><b style="color:#f43f5e;">%{p_ms2_kgvar*100:.1f}</b></td></tr>
                <tr><td style="padding:8px 0;">KG Var & 2.5 Üst</td><td style="text-align:right;"><b style="color:#34d399;">%{p_kgvar_ust25*100:.1f}</b></td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # SECTION 3: SKOR MATRİSİ (HEATMAP)
    st.markdown("### 🧮 3. Profesyonel Skor Olasılık Isı Haritası (%)")
    
    heatmap_html = f"""
    <div class="pro-card">
        <p style="color:#94a3b8; font-size:13px; margin-bottom:12px;">Yeşil ve Mavi renkli hücreler en yüksek istatistiki olasılığa sahip skorları gösterir.</p>
        <table class="heatmap-table">
            <tr>
                <th style="background:#0f172a;">{home_name[:4].upper()} \ {away_name[:4].upper()}</th>
                <th>0 Gol</th><th>1 Gol</th><th>2 Gol</th><th>3 Gol</th><th>4 Gol</th><th>5 Gol</th>
            </tr>
    """
    
    for h in range(6):
        heatmap_html += f"<tr><td style='background:#1e293b; color:#ffffff; font-weight:700;'>{h} Gol</td>"
        for a in range(6):
            prob = matrix.get((h, a), 0) * 100
            
            # Dynamic Dark Heatmap Styling
            if prob > 8.0:
                bg = "rgba(16, 185, 129, 0.45)" # High - Bright Emerald
                color = "#ffffff"
                border = "1px solid #10b981"
            elif prob > 5.0:
                bg = "rgba(59, 130, 246, 0.35)" # Medium - Blue
                color = "#ffffff"
                border = "1px solid #3b82f6"
            elif prob > 2.5:
                bg = "rgba(30, 41, 59, 0.8)"
                color = "#cbd5e1"
                border = "1px solid #334155"
            else:
                bg = "rgba(15, 23, 42, 0.5)"
                color = "#64748b"
                border = "1px solid #1e293b"

            heatmap_html += f"<td style='background:{bg}; color:{color}; border:{border};'>%{prob:.1f}</td>"
        heatmap_html += "</tr>"

    heatmap_html += "</table></div>"
    st.markdown(heatmap_html, unsafe_allow_html=True)

    # SECTION 4: TAHMİNLER & ÖNERİLER
    st.markdown("### 💡 4. Model Tarafından Önerilen Kararlar")
    
    sc1, sc2 = st.columns([0.4, 0.6])
    
    with sc1:
        st.markdown("<div class="pro-card">", unsafe_allow_html=True)
        st.markdown("#### 🎯 En Olası 4 Skor Tahmini", unsafe_allow_html=True)
        for idx, ((h, a), prob) in enumerate(top_scores, 1):
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; background:#1a2332; padding:10px 14px; border-radius:8px; margin-bottom:8px; border:1px solid #334155;">
                <span style="font-weight:700; color:#38bdf8;">#{idx} Skor: {h} - {a}</span>
                <span class="stat-badge badge-success">%{prob*100:.1f} Olasılık</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with sc2:
        # Smart Decision Logic
        if p_ust15 > 0.78:
            banko = f"1.5 Gol Üst (Olasılık: %{p_ust15*100:.1f})"
        elif p_1x > 0.76:
            banko = f"Çifte Şans 1X (Olasılık: %{p_1x*100:.1f})"
        elif p_x2 > 0.76:
            banko = f"Çifte Şans X2 (Olasılık: %{p_x2*100:.1f})"
        else:
            banko = f"Çifte Şans 12 (Olasılık: %{p_12*100:.1f})"

        if p_ms1 > 0.52:
            ideal = f"Maç Sonucu 1 (Olasılık: %{p_ms1*100:.1f})"
        elif p_ms2 > 0.52:
            ideal = f"Maç Sonucu 2 (Olasılık: %{p_ms2*100:.1f})"
        elif p_ust25 > 0.56:
            ideal = f"2.5 Gol Üst (Olasılık: %{p_ust25*100:.1f})"
        elif p_alt25 > 0.56:
            ideal = f"2.5 Gol Alt (Olasılık: %{p_alt25*100:.1f})"
        else:
            ideal = f"Karşılıklı Gol VAR (Olasılık: %{p_kgvar*100:.1f})"

        if p_kgvar_ust25 > 0.45:
            surpriz = f"KG Var & 2.5 Üst (Olasılık: %{p_kgvar_ust25*100:.1f})"
        elif p_ms1_kgvar > 0.32:
            surpriz = f"{home_name} Kazanır & KG Var"
        elif p_ms2_kgvar > 0.32:
            surpriz = f"{away_name} Kazanır & KG Var"
        else:
            surpriz = f"3.5 Gol Üst (Olasılık: %{p_ust35*100:.1f})"

        st.markdown(f"""
        <div class="pro-card">
            <h4 style="margin:0 0 15px 0; color:#34d399;">🛡️ Algoritmik Strateji Kartı</h4>
            <div style="margin-bottom:12px;">
                <span class="stat-badge badge-success">BANKO TERCİH</span>
                <p style="margin:5px 0 0 0; font-size:15px; font-weight:600; color:#ffffff;">{banko}</p>
            </div>
            <div style="margin-bottom:12px;">
                <span class="stat-badge badge-primary">İDEAL ANA BAHİS</span>
                <p style="margin:5px 0 0 0; font-size:15px; font-weight:600; color:#ffffff;">{ideal}</p>
            </div>
            <div>
                <span class="stat-badge badge-warning">SÜRPRİZ / YÜKSEK ORAN</span>
                <p style="margin:5px 0 0 0; font-size:15px; font-weight:600; color:#ffffff;">{surpriz}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
