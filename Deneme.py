import streamlit as st
import numpy as np
from scipy.stats import poisson

# Mobil uyumlu sayfa ayarı
st.set_page_config(page_title="İddaa Analiz Programı", page_icon="⚽", layout="centered")

st.title("⚽ İddaa Yüzdesel Analiz Programı")
st.write("Takımların son maçlardaki gol ortalamalarını girerek ihtimalleri hesaplayın.")

st.markdown("---")

# Kullanıcı Giriş Alanları
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Ev Sahibi")
    home_scored = st.number_input("Attığı Gol Ortalaması", min_value=0.0, value=1.8, step=0.1)
    home_conceded = st.number_input("Yediği Gol Ortalaması", min_value=0.0, value=1.0, step=0.1)

with col2:
    st.subheader("✈️ Deplasman")
    away_scored = st.number_input("Attığı Gol Ortalaması", min_value=0.0, value=1.2, step=0.1)
    away_conceded = st.number_input("Yediği Gol Ortalaması", min_value=0.0, value=1.5, step=0.1)

# Genel Lig Ortalamaları (Standart kabul edilen değerler)
league_home_avg = 1.5
league_away_avg = 1.2

if st.button("📊 ANALİZ ET VE HESAPLA", use_container_width=True):
    # Beklenen Gol (xG) Hesaplama
    exp_home = (home_scored / league_home_avg) * (away_conceded / league_away_avg) * league_home_avg
    exp_away = (away_scored / league_away_avg) * (home_conceded / league_home_avg) * league_away_avg

    # Poisson Olasılık Matrisi (0-8 gol arası)
    max_goals = 9
    home_probs = [poisson.pmf(i, exp_home) for i in range(max_goals)]
    away_probs = [poisson.pmf(j, exp_away) for j in range(max_goals)]

    ms1, ms0, ms2 = 0.0, 0.0, 0.0
    over_25 = 0.0
    kg_var = 0.0

    for i in range(max_goals):
        for j in range(max_goals):
            p = home_probs[i] * away_probs[j]
            
            # MS 1 - 0 - 2
            if i > j:
                ms1 += p
            elif i == j:
                ms0 += p
            else:
                ms2 += p
            
            # 2.5 Üst
            if (i + j) > 2.5:
                over_25 += p
            
            # Karşılıklı Gol Var
            if i > 0 and j > 0:
                kg_var += p

    # İY 0.5 Üst (Toplam maç golünün tahminen %45'i ilk yarı atılır)
    exp_iy_total = (exp_home + exp_away) * 0.45
    iy_05_over = (1 - poisson.pmf(0, exp_iy_total)) * 100

    # Yüzdelere Çevirme
    ms1_pct = ms1 * 100
    ms0_pct = ms0 * 100
    ms2_pct = ms2 * 100
    over_25_pct = over_25 * 100
    kg_var_pct = kg_var * 100

    # Sonuçları Gösterme
    st.markdown("### 🎯 Maç Sonucu (MS) İhtimalleri")
    c1, c2, c3 = st.columns(3)
    c1.metric("MS 1", f"%{ms1_pct:.1f}")
    c2.metric("MS 0 (X)", f"%{ms0_pct:.1f}")
    c3.metric("MS 2", f"%{ms2_pct:.1f}")

    st.markdown("### ⚽ Gol İhtimalleri")
    c4, c5, c6 = st.columns(3)
    c4.metric("İY 0.5 Üst", f"%{iy_05_over:.1f}")
    c5.metric("2.5 Gol Üstü", f"%{over_25_pct:.1f}")
    c6.metric("KG Var", f"%{kg_var_pct:.1f}")

    st.info(f"💡 **Beklenen Gol Sayısı:** Ev Sahibi: **{exp_home:.2f}** | Deplasman: **{exp_away:.2f}**")
