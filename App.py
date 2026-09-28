import streamlit as st
import math

# Sayfa Yapılandırması ve Mobil Stil
st.set_page_config(
    page_title="Poisson Analiz Motoru", 
    page_icon="⚽", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Özel CSS ile Profesyonel Tasarım Düzenlemeleri
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 22px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ÜST BAŞLIK VE SAĞ ÜST YENİLEME BUTONU
# ---------------------------------------------------------
col_title, col_reload = st.columns([0.85, 0.15])

with col_title:
    st.title("⚽ Poisson Analiz Motoru")

with col_reload:
    # Sağ üst köşedeki yenileme ikonu
    if st.button("🔄", help="Sayfayı Yenile ve Sıfırla"):
        st.rerun()

st.caption("Takımların gol istatistiklerini girerek maç olasılıklarını hesaplayın.")
st.divider()

# ---------------------------------------------------------
# VERİ GİRİŞ ALANLARI (SEKMELİ TASARIM)
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["🏠 EV SAHİBİ", "✈️ DEPLASMAN"])

with tab1:
    ev_adi = st.text_input("Ev Sahibi Takım Adı", value="Beşiktaş", key="ev_name")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        ev_mac = st.number_input("Oynanan Maç", min_value=1.0, value=10.0, step=1.0, key="ev_m")
        ev_att_toplam = st.number_input("Attığı Toplam Gol", min_value=0.0, value=18.0, step=1.0, key="ev_att")
    with col_e2:
        ev_def_toplam = st.number_input("Yediği Toplam Gol", min_value=0.0, value=10.0, step=1.0, key="ev_def")

with tab2:
    dep_adi = st.text_input("Deplasman Takım Adı", value="Trabzonspor", key="dep_name")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        dep_mac = st.number_input("Oynanan Maç ", min_value=1.0, value=10.0, step=1.0, key="dep_m")
        dep_att_toplam = st.number_input("Attığı Toplam Gol ", min_value=0.0, value=14.0, step=1.0, key="dep_att")
    with col_d2:
        dep_def_toplam = st.number_input("Yediği Toplam Gol ", min_value=0.0, value=12.0, step=1.0, key="dep_def")

st.write("")

# ---------------------------------------------------------
# HESAPLAMA VE ANALİZ
# ---------------------------------------------------------
if st.button("📊 MAÇI ANALİZ ET", type="primary", use_container_width=True):
    ev_att = ev_att_toplam / ev_mac
    ev_def = ev_def_toplam / ev_mac
    dep_att = dep_att_toplam / dep_mac
    dep_def = dep_def_toplam / dep_mac

    # Poisson Hesabı
    xg_ev = (ev_att * dep_def) / 1.40
    xg_dep = (dep_att * ev_def) / 1.40
    toplam_xg = xg_ev + xg_dep

    matrix = {}
    for h in range(7):
        for a in range(7):
            p_h = (math.pow(xg_ev, h) * math.exp(-xg_ev)) / math.factorial(h)
            p_a = (math.pow(xg_dep, a) * math.exp(-xg_dep)) / math.factorial(a)
            matrix[(h, a)] = p_h * p_a

    ms1 = sum(p for (h, a), p in matrix.items() if h > a)
    ms0 = sum(p for (h, a), p in matrix.items() if h == a)
    ms2 = sum(p for (h, a), p in matrix.items() if h < a)
    ust25 = sum(p for (h, a), p in matrix.items() if h + a > 2.5)
    kg_var = sum(p for (h, a), p in matrix.items() if h > 0 and a > 0)
    top_scores = sorted(matrix.items(), key=lambda x: x[1], reverse=True)[:3]

    # SONUÇ EKRANI
    st.divider()
    st.subheader(f"📊 {ev_adi.upper()} vs {dep_adi.upper()}")
    
    st.info(f"🎯 **xG Beklentisi:** {ev_adi}: `{xg_ev:.2f}` | {dep_adi}: `{xg_dep:.2f}`\n\n🎯 **Toplam Maç xG:** `{toplam_xg:.2f}`")
    
    st.markdown("##### 📈 Maç Sonucu Olasılıkları")
    c1, c2, c3 = st.columns(3)
    c1.metric("MS 1", f"%{ms1*100:.1f}")
    c2.metric("MS 0", f"%{ms0*100:.1f}")
    c3.metric("MS 2", f"%{ms2*100:.1f}")

    st.markdown("##### 🎯 Gol ve KG Olasılıkları")
    c4, c5 = st.columns(2)
    c4.metric("🔥 2.5 Üst", f"%{ust25*100:.1f}")
    c5.metric("🤝 KG Var", f"%{kg_var*100:.1f}")

    st.markdown("##### 🏆 En Olası 3 Skor Tahmini")
    for idx, ((h, a), prob) in enumerate(top_scores, 1):
        st.success(f"**{idx}. Olasılık:** {h} - {a} &nbsp;&nbsp;(`%{prob*100:.1f}`)")
