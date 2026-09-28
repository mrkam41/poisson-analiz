import streamlit as st
import math

# Sayfa Yapılandırması (Mobil Uyumlu)
st.set_page_config(page_title="Poisson Analiz", page_icon="⚽", layout="centered")

st.title("⚽ Futbol Poisson Analiz Motoru")
st.write("Takımların verilerini girerek maç olasılıklarını hesaplayın.")

# EV SAHİBİ BİLGİLERİ
st.subheader("🏠 Ev Sahibi Bilgileri")
col1, col2 = st.columns(2)
with col1:
    ev_adi = st.text_input("Ev Sahibi Adı", value="Beşiktaş")
    ev_mac = st.number_input("Ev Oynanan Maç", min_value=1.0, value=10.0, step=1.0)
with col2:
    ev_att_toplam = st.number_input("Ev Attığı Gol", min_value=0.0, value=18.0, step=1.0)
    ev_def_toplam = st.number_input("Ev Yediği Gol", min_value=0.0, value=10.0, step=1.0)

# DEPLASMAN BİLGİLERİ
st.subheader("✈️ Deplasman Bilgileri")
col3, col4 = st.columns(2)
with col3:
    dep_adi = st.text_input("Deplasman Adı", value="Trabzonspor")
    dep_mac = st.number_input("Dep Oynanan Maç", min_value=1.0, value=10.0, step=1.0)
with col4:
    dep_att_toplam = st.number_input("Dep Attığı Gol", min_value=0.0, value=14.0, step=1.0)
    dep_def_toplam = st.number_input("Dep Yediği Gol", min_value=0.0, value=12.0, step=1.0)

# HESAPLAMA BUTONU
if st.button("📊 ANALİZ ET VE HESAPLA", type="primary", use_container_width=True):
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

    # SONUÇLAR
    st.divider()
    st.subheader(f"📊 ANALİZ: {ev_adi.upper()} vs {dep_adi.upper()}")
    
    st.info(f"🎯 **xG Beklentisi:** {ev_adi}: `{xg_ev:.2f}` | {dep_adi}: `{xg_dep:.2f}`\n\n🎯 **Toplam Maç xG:** `{toplam_xg:.2f}`")
    
    col_m1, col_m0, col_m2 = st.columns(3)
    col_m1.metric("MS 1 (Ev)", f"%{ms1*100:.1f}")
    col_m0.metric("MS 0 (Beraberlik)", f"%{ms0*100:.1f}")
    col_m2.metric("MS 2 (Dep)", f"%{ms2*100:.1f}")

    col_u, col_k = st.columns(2)
    col_u.metric("🔥 2.5 Üst Olasılığı", f"%{ust25*100:.1f}")
    col_k.metric("🤝 KG Var Olasılığı", f"%{kg_var*100:.1f}")

    st.write("### 🎯 En Olası 3 Skor Tahmini")
    for idx, ((h, a), prob) in enumerate(top_scores, 1):
        st.write(f"**{idx}. Olasılık:** `{h} - {a}` (%{prob*100:.1f})")
