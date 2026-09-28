import streamlit as st
import math

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Pro Poisson Analiz Motoru", 
    page_icon="⚽", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobil Dokunmatik ve Kilitlenme Karşıtı CSS
st.markdown("""
    <style>
    html, body, .stApp {
        overscroll-behavior-y: none !important;
        overflow-x: hidden;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ÜST BAŞLIK VE YENİLEME
# ---------------------------------------------------------
col_title, col_reload = st.columns([0.85, 0.15])

with col_title:
    st.title("⚽ Pro Poisson Analiz Motoru")

with col_reload:
    if st.button("🔄", help="Sayfayı Sıfırla"):
        st.rerun()

st.caption("Gelişmiş Dixon-Coles modeli ve akıllı bahis öneri sistemi.")
st.divider()

# ---------------------------------------------------------
# VERİ GİRİŞ ALANLARI
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🏠 EV SAHİBİ (İÇ SAHA)", "✈️ DEPLASMAN (DIŞ SAHA)", "💰 ORANLAR (İSTEĞE BAĞLI)"])

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
# DIXON-COLES VE POISSON HESAPLAMA MOTORU
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

    matrix = {}
    for h in range(7):
        for a in range(7):
            p_h = (math.pow(xg_ev, h) * math.exp(-xg_ev)) / math.factorial(h)
            p_a = (math.pow(xg_dep, a) * math.exp(-xg_dep)) / math.factorial(a)
            tau = dixon_coles_tau(h, a, xg_ev, xg_dep)
            matrix[(h, a)] = p_h * p_a * tau

    # Normalize Etme
    total_p = sum(matrix.values())
    for k in matrix:
        matrix[k] /= total_p

    ms1 = sum(p for (h, a), p in matrix.items() if h > a)
    ms0 = sum(p for (h, a), p in matrix.items() if h == a)
    ms2 = sum(p for (h, a), p in matrix.items() if h < a)
    
    dc_1x = ms1 + ms0
    dc_x2 = ms0 + ms2
    dc_12 = ms1 + ms2

    ust15 = sum(p for (h, a), p in matrix.items() if h + a > 1.5)
    ust25 = sum(p for (h, a), p in matrix.items() if h + a > 2.5)
    ust35 = sum(p for (h, a), p in matrix.items() if h + a > 3.5)
    alt25 = 1 - ust25

    kg_var = sum(p for (h, a), p in matrix.items() if h > 0 and a > 0)
    top_scores = sorted(matrix.items(), key=lambda x: x[1], reverse=True)[:3]

    fair_ms1 = 1 / ms1 if ms1 > 0 else 0
    fair_ms0 = 1 / ms0 if ms0 > 0 else 0
    fair_ms2 = 1 / ms2 if ms2 > 0 else 0

    val_ms1 = (ms1 * o_ms1) - 1
    val_ms0 = (ms0 * o_ms0) - 1
    val_ms2 = (ms2 * o_ms2) - 1

    # ---------------------------------------------------------
    # SONUÇ EKRANI
    # ---------------------------------------------------------
    st.divider()
    st.subheader(f"📊 {ev_adi.upper()} vs {dep_adi.upper()}")
    
    st.info(f"🎯 **xG Beklentisi:** {ev_adi}: `{xg_ev:.2f}` | {dep_adi}: `{xg_dep:.2f}`\n\n🎯 **Toplam Maç xG:** `{toplam_xg:.2f}`")
    
    st.markdown("##### 📈 Maç Sonucu Olasılıkları ve Adil Oranlar")
    c1, c2, c3 = st.columns(3)
    c1.metric("MS 1", f"%{ms1*100:.1f}", f"Adil: {fair_ms1:.2f}")
    c2.metric("MS 0", f"%{ms0*100:.1f}", f"Adil: {fair_ms0:.2f}")
    c3.metric("MS 2", f"%{ms2*100:.1f}", f"Adil: {fair_ms2:.2f}")

    st.markdown("##### 🎯 Gol ve KG Olasılıkları")
    c4, c5 = st.columns(2)
    c4.metric("🔥 2.5 Üst", f"%{ust25*100:.1f}")
    c5.metric("🤝 KG Var", f"%{kg_var*100:.1f}")

    st.markdown("##### 🏆 En Olası 3 Skor Tahmini")
    for idx, ((h, a), prob) in enumerate(top_scores, 1):
        st.success(f"**{idx}. Olasılık:** {h} - {a} &nbsp;&nbsp;(`%{prob*100:.1f}`)")

    # ---------------------------------------------------------
    # OTOMATİK ÖNERİLEN BAHİSLER PANELİ
    # ---------------------------------------------------------
    st.divider()
    st.markdown("### 💡 MAÇ İÇİN ÖNERİLEN BAHİSLER")

    # Banko Öneri
    banko_tercih = ""
    if ust15 > 0.75:
        banko_tercih = f"1.5 Üst (Olasılık: %{ust15*100:.1f})"
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
    if kg_var > 0.52 and ust25 > 0.52:
        surpriz_tercih = "KG Var & 2.5 Üst Kombinasyonu"
    elif ms1 > 0.45 and kg_var > 0.50:
        surpriz_tercih = f"MS 1 & KG Var ({ev_adi} kazanır ve gol yer)"
    elif ms2 > 0.45 and kg_var > 0.50:
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
