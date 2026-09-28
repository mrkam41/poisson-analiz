import streamlit as st
import math

# ---------------------------------------------------------
# SAYFA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pro Poisson Analiz & Dashboard", 
    page_icon="⚽", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# PREMIUM MODERN SPOR STİLİ (CSS)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Temel Ayarlar ve Kaydırma Koruması */
    html, body, .stApp {
        overscroll-behavior-y: none !important;
        overflow-x: hidden;
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Kart Yapıları */
    .metric-card {
        background: linear-gradient(135deg, #1e2638 0%, #111827 100%);
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 13px;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: bold;
        color: #38bdf8;
    }
    .metric-sub {
        font-size: 12px;
        color: #4ade80;
        margin-top: 2px;
    }

    /* İlerleme Çubukları Customization */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #3b82f6 , #10b981);
    }
    
    /* Buton Tasarımı */
    .stButton>button {
        border-radius: 10px;
        font-weight: bold;
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.6);
        transform: translateY(-1px);
    }

    /* Tab Stilleri */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        background-color: #1f2937;
        color: #9ca3af;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ÜST BAŞLIK VE YENİLEME
# ---------------------------------------------------------
col_title, col_reload = st.columns([0.85, 0.15])

with col_title:
    st.title("⚽ Pro Poisson Analiz & Dashboard")

with col_reload:
    if st.button("🔄", help="Sayfayı Sıfırla"):
        st.rerun()

st.caption("Dixon-Coles modeli, Skor Matrisi, Kombine Tahminler ve Value Bet Analizi.")
st.divider()

# ---------------------------------------------------------
# VERİ GİRİŞ ALANLARI
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🏠 EV SAHİBİ (İÇ SAHA)", "✈️ DEPLASMAN (DIŞ SAHA)", "💰 ORANLAR (OPTİONAL)"])

with tab1:
    ev_adi = st.text_input("Ev Sahibi Takım", value="Beşiktaş", key="ev_name")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        ev_mac = st.number_input("İç Saha Maç Sayısı", min_value=1.0, value=8.0, step=1.0, key="ev_m")
        ev_att_toplam = st.number_input("İç Sahada Attığı Gol", min_value=0.0, value=16.0, step=1.0, key="ev_att")
    with col_e2:
        ev_def_toplam = st.number_input("İç Sahada Yediği Gol", min_value=0.0, value=6.0, step=1.0, key="ev_def")

with tab2:
    dep_adi = st.text_input("Deplasman Takımı", value="Trabzonspor", key="dep_name")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        dep_mac = st.number_input("Dış Saha Maç Sayısı", min_value=1.0, value=8.0, step=1.0, key="dep_m")
        dep_att_toplam = st.number_input("Dış Sahada Attığı Gol", min_value=0.0, value=11.0, step=1.0, key="dep_att")
    with col_d2:
        dep_def_toplam = st.number_input("Dış Sahada Yediği Gol", min_value=0.0, value=10.0, step=1.0, key="dep_def")

with tab3:
    st.write("Değer (Value) analizi yapmak isterseniz büro oranlarını girebilirsiniz:")
    o_ms1 = st.number_input("MS 1 Oranı", min_value=1.0, value=2.10, step=0.05)
    o_ms0 = st.number_input("MS 0 Oranı", min_value=1.0, value=3.20, step=0.05)
    o_ms2 = st.number_input("MS 2 Oranı", min_value=1.0, value=3.10, step=0.05)

st.write("")

# ---------------------------------------------------------
# HESAPLAMA MOTORU & DIXON-COLES
# ---------------------------------------------------------
def dixon_coles_tau(h, a, xg_ev, xg_dep, rho=-0.13):
    if h == 0 and a == 0:
        return 1.0 - (xg_ev * xg_dep * rho)
    elif h == 0 and a == 1:
        return 1.0 + (xg_ev * rho)
    elif h == 1 and a == 0:
        return 1.0 + (xg_dep * rho)
    elif h == 1 and a == 1:
        return 1.0 - rho
    else:
        return 1.0

if st.button("📊 DETAYLI MAÇ ANALİZİ YAP", type="primary", use_container_width=True):
    # Temel Ortalama
    ev_att = ev_att_toplam / ev_mac
    ev_def = ev_def_toplam / ev_mac
    dep_att = dep_att_toplam / dep_mac
    dep_def = dep_def_toplam / dep_mac

    # xG Hesaplaması
    xg_ev = (ev_att * dep_def / 1.35)
    xg_dep = (dep_att * ev_def / 1.35)
    toplam_xg = xg_ev + xg_dep

    # Güç Düzeyi Hesaplama (%)
    ev_power = (xg_ev / (xg_ev + xg_dep)) * 100 if (xg_ev + xg_dep) > 0 else 50
    dep_power = 100 - ev_power

    matrix = {}
    for h in range(6):
        for a in range(6):
            p_h = (math.pow(xg_ev, h) * math.exp(-xg_ev)) / math.factorial(h)
            p_a = (math.pow(xg_dep, a) * math.exp(-xg_dep)) / math.factorial(a)
            tau = dixon_coles_tau(h, a, xg_ev, xg_dep)
            matrix[(h, a)] = p_h * p_a * tau

    # Normalize Etme
    total_p = sum(matrix.values())
    for k in matrix:
        matrix[k] /= total_p

    # Maç Sonucu Olasılıkları
    ms1 = sum(p for (h, a), p in matrix.items() if h > a)
    ms0 = sum(p for (h, a), p in matrix.items() if h == a)
    ms2 = sum(p for (h, a), p in matrix.items() if h < a)
    
    dc_1x = ms1 + ms0
    dc_x2 = ms0 + ms2
    dc_12 = ms1 + ms2

    # Gol Olasılıkları
    alt15 = sum(p for (h, a), p in matrix.items() if h + a < 1.5)
    ust15 = 1 - alt15
    
    alt25 = sum(p for (h, a), p in matrix.items() if h + a < 2.5)
    ust25 = 1 - alt25
    
    alt35 = sum(p for (h, a), p in matrix.items() if h + a < 3.5)
    ust35 = 1 - alt35

    kg_var = sum(p for (h, a), p in matrix.items() if h > 0 and a > 0)
    kg_yok = 1 - kg_var

    # Kombine Olasılıklar
    ms1_ust25 = sum(p for (h, a), p in matrix.items() if h > a and (h + a) > 2.5)
    ms1_kgvar = sum(p for (h, a), p in matrix.items() if h > a and a > 0)
    ms2_ust25 = sum(p for (h, a), p in matrix.items() if h < a and (h + a) > 2.5)
    ms2_kgvar = sum(p for (h, a), p in matrix.items() if h < a and h > 0)
    kgvar_ust25 = sum(p for (h, a), p in matrix.items() if h > 0 and a > 0 and (h + a) > 2.5)

    top_scores = sorted(matrix.items(), key=lambda x: x[1], reverse=True)[:3]

    fair_ms1 = 1 / ms1 if ms1 > 0 else 0
    fair_ms0 = 1 / ms0 if ms0 > 0 else 0
    fair_ms2 = 1 / ms2 if ms2 > 0 else 0

    val_ms1 = (ms1 * o_ms1) - 1
    val_ms0 = (ms0 * o_ms0) - 1
    val_ms2 = (ms2 * o_ms2) - 1

    # ---------------------------------------------------------
    # SONUÇ EKRANI VE PANELER
    # ---------------------------------------------------------
    st.divider()
    st.subheader(f"📊 {ev_adi.upper()} vs {dep_adi.upper()}")
    
    # 1. GÜÇ VE XG BARLARI
    st.markdown("##### ⚔️ Hücum ve Güç Düzeyi Kıyaslaması")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.write(f"**{ev_adi} xG:** `{xg_ev:.2f}` (%{ev_power:.1f})")
        st.progress(int(ev_power))
    with col_p2:
        st.write(f"**{dep_adi} xG:** `{xg_dep:.2f}` (%{dep_power:.1f})")
        st.progress(int(dep_power))

    st.write("")

    # 2. MAÇ SONUCU VE ADİL ORAN DOKUMU
    st.markdown("##### 📈 Maç Sonucu Olasılıkları ve Adil Oranlar")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">MS 1 ({ev_adi})</div>
            <div class="metric-value">%{ms1*100:.1f}</div>
            <div class="metric-sub">Adil Oran: {fair_ms1:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(int(ms1*100))

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">MS 0 (BERABERE)</div>
            <div class="metric-value">%{ms0*100:.1f}</div>
            <div class="metric-sub">Adil Oran: {fair_ms0:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(int(ms0*100))

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">MS 2 ({dep_adi})</div>
            <div class="metric-value">%{ms2*100:.1f}</div>
            <div class="metric-sub">Adil Oran: {fair_ms2:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(int(ms2*100))

    st.write("")

    # 3. ALT / ÜST VE KG TAM LİSTE
    st.markdown("##### ⚽ Gol Alt/Üst ve KG Olasılıkları")
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("1.5 Üst", f"%{ust15*100:.1f}")
    g2.metric("2.5 Üst", f"%{ust25*100:.1f}")
    g3.metric("3.5 Üst", f"%{ust35*100:.1f}")
    g4.metric("KG Var", f"%{kg_var*100:.1f}")

    # 4. KOMBİNE TAHMİNLER PANELİ
    st.markdown("##### 🎯 Özel Kombine Tahmin Olasılıkları")
    k1, k2, k3 = st.columns(3)
    k1.write(f"**MS 1 & 2.5 Üst:** `%{ms1_ust25*100:.1f}`")
    k1.write(f"**MS 1 & KG Var:** `%{ms1_kgvar*100:.1f}`")
    
    k2.write(f"**MS 2 & 2.5 Üst:** `%{ms2_ust25*100:.1f}`")
    k2.write(f"**MS 2 & KG Var:** `%{ms2_kgvar*100:.1f}`")

    k3.write(f"**KG Var & 2.5 Üst:** `%{kgvar_ust25*100:.1f}`")
    k3.write(f"**Toplam Gol Beklentisi:** `{toplam_xg:.2f}`")

    st.write("")

    # 5. SKOR MATRİSİ (HEATMAP TABLOSU)
    st.markdown("##### 🧮 Skor Olasılık Matrisi (%)")
    
    # Matris Tablosunu Oluşturma
    header_html = f"<table style='width:100%; text-align:center; border-collapse:collapse; background-color:#111827; border-radius:8px; overflow:hidden;'>"+"<tr style='background-color:#1f2937; color:#a0aec0;'><th>Ev \ Dep</th>"
    for a in range(5):
        header_html += f"<th>{a}</th>"
    header_html += "</tr>"

    rows_html = ""
    for h in range(5):
        rows_html += f"<tr style='border-bottom:1px solid #1f2937;'><td style='background-color:#1f2937; color:#a0aec0; font-weight:bold;'>{h}</td>"
        for a in range(5):
            prob = matrix.get((h, a), 0) * 100
            bg_color = "transparent"
            if prob > 8:
                bg_color = "rgba(16, 185, 129, 0.4)" # Yüksek İhtimal Yeşil
            elif prob > 5:
                bg_color = "rgba(59, 130, 246, 0.3)" # Orta İhtimal Mavi
            
            rows_html += f"<td style='padding:8px; background-color:{bg_color}; font-size:13px;'>%{prob:.1f}</td>"
        rows_html += "</tr>"
    
    full_table = header_html + rows_html + "</table>"
    st.markdown(full_table, unsafe_allow_html=True)

    st.write("")

    # 6. EN OLASI 3 SKOR
    st.markdown("##### 🏆 En Olası 3 Skor Tahmini")
    for idx, ((h, a), prob) in enumerate(top_scores, 1):
        st.success(f"**{idx}. Olasılık:** {h} - {a} &nbsp;&nbsp;(`%{prob*100:.1f}`)")

    # 7. OTOMATİK ÖNERİLEN BAHİSLER PANELİ
    st.divider()
    st.markdown("### 💡 MAÇ İÇİN ÖNERİLEN BAHİSLER")

    # Banko Öneri
    banko_tercih = ""
    if ust15 > 0.75:
        banko_tercih = f"1.5 Üst Gol (Olasılık: %{ust15*100:.1f})"
    elif dc_1x > 0.75:
        banko_tercih = f"Çifte Şans 1X (Olasılık: %{dc_1x*100:.1f})"
    elif dc_x2 > 0.75:
        banko_tercih = f"Çifte Şans X2 (Olasılık: %{dc_x2*100:.1f})"
    else:
        banko_tercih = f"Çifte Şans 12 (Olasılık: %{dc_12*100:.1f})"

    st.write(f"🟢 **Günün Bankosu:** `{banko_tercih}`")

    # İdeal Tercih
    ideal_tercih = ""
    if ms1 > 0.55:
        ideal_tercih = f"Maç Sonucu 1 (Olasılık: %{ms1*100:.1f})"
    elif ms2 > 0.55:
        ideal_tercih = f"Maç Sonucu 2 (Olasılık: %{ms2*100:.1f})"
    elif ust25 > 0.58:
        ideal_tercih = f"2.5 Üst Gol (Olasılık: %{ust25*100:.1f})"
    elif alt25 > 0.58:
        ideal_tercih = f"2.5 Alt Gol (Olasılık: %{alt25*100:.1f})"
    elif kg_var > 0.55:
        ideal_tercih = f"KG Var (Olasılık: %{kg_var*100:.1f})"
    else:
        ideal_tercih = "Taraf bahsi riskli, Karşılıklı Gol veya Alt/Üst seçenekleri değerlendirilmeli."

    st.write(f"🟡 **İdeal / Ana Bahis:** `{ideal_tercih}`")

    # Sürpriz / Yüksek Oran Önerisi
    surpriz_tercih = ""
    if kgvar_ust25 > 0.48:
        surpriz_tercih = f"KG Var & 2.5 Üst Kombinasyonu (Olasılık: %{kgvar_ust25*100:.1f})"
    elif ms1_kgvar > 0.35:
        surpriz_tercih = f"MS 1 & KG Var ({ev_adi} kazanır ve gol yer)"
    elif ms2_kgvar > 0.35:
        surpriz_tercih = f"MS 2 & KG Var ({dep_adi} kazanır ve gol yer)"
    elif ust35 > 0.35:
        surpriz_tercih = f"3.5 Üst Gol (Olasılık: %{ust35*100:.1f})"
    else:
        surpriz_tercih = f"En olası skor olan {top_scores[0][0][0]}-{top_scores[0][0][1]} skor bahsi."

    st.write(f"🔴 **Sürpriz / Yüksek Oran:** `{surpriz_tercih}`")

    # Value Bet Bildirimi
    if val_ms1 > 0.05 or val_ms0 > 0.05 or val_ms2 > 0.05:
        st.markdown("---")
        st.markdown("##### 💎 Değerli (Value) Oran Fırsatı")
        if val_ms1 > 0.05:
            st.warning(f"**MS 1 Oranı Değerli!** Büro Oranı: `{o_ms1}` | Beklenen Değer: `+{val_ms1*100:.1f}%`")
        if val_ms0 > 0.05:
            st.warning(f"**MS 0 Oranı Değerli!** Büro Oranı: `{o_ms0}` | Beklenen Değer: `+{val_ms0*100:.1f}%`")
        if val_ms2 > 0.05:
            st.warning(f"**MS 2 Oranı Değerli!** Büro Oranı: `{o_ms2}` | Beklenen Değer: `+{val_ms2*100:.1f}%`")
