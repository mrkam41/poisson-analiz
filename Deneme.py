import streamlit as st
import numpy as np
from scipy.stats import poisson

# Mobil uyumlu sayfa ayarları
st.set_page_config(page_title="Gelişmiş İddaa Analiz", page_icon="⚽", layout="centered")

st.title("⚽ Gelişmiş İddaa Analiz Programı")
st.write("Takımların son 5 maç skorlarını aralarında virgül olacak şekilde girin. Gerisini program hesaplar!")

# Skor Ayrıştırma Fonksiyonu
def parse_scores(score_str):
    scores = score_str.replace(" ", "").split(",")
    scored_list, conceded_list = [], []
    for s in scores:
        if "-" in s:
            parts = s.split("-")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                scored_list.append(int(parts[0]))
                conceded_list.append(int(parts[1]))
    return scored_list, conceded_list

# Kullanıcı Giriş Alanları
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Ev Sahibi")
    home_input = st.text_input("Son 5 Maç Skoru", "2-1, 1-0, 3-1, 0-0, 2-2")

with col2:
    st.subheader("✈️ Deplasman")
    away_input = st.text_input("Son 5 Maç Skoru", "0-1, 1-1, 2-0, 1-2, 0-0")

if st.button("🚀 DETAYLI ANALİZ ET", use_container_width=True):
    home_scored, home_conceded = parse_scores(home_input)
    away_scored, away_conceded = parse_scores(away_input)

    if not home_scored or not away_scored:
        st.error("⚠️ Lütfen skorları '2-1, 1-0, 3-0' formatında doğru girdiğinizden emin olun.")
    else:
        # Otomatik Ortak Hesaplama
        avg_home_scored = np.mean(home_scored)
        avg_home_conceded = np.mean(home_conceded)
        avg_away_scored = np.mean(away_scored)
        avg_away_conceded = np.mean(away_conceded)

        # Beklenen Gol (xG) Hesaplama
        league_avg = 1.35
        exp_home = max(0.2, (avg_home_scored / league_avg) * (avg_away_conceded / league_avg) * league_avg)
        exp_away = max(0.2, (avg_away_scored / league_avg) * (avg_home_conceded / league_avg) * league_avg)

        # Poisson Matrisi
        max_g = 8
        home_p = [poisson.pmf(i, exp_home) for i in range(max_g)]
        away_p = [poisson.pmf(j, exp_away) for j in range(max_g)]

        ms1, ms0, ms2 = 0.0, 0.0, 0.0
        o15, o25, o35 = 0.0, 0.0, 0.0
        kg_var = 0.0
        exact_scores = []

        for i in range(max_g):
            for j in range(max_g):
                p = home_p[i] * away_p[j]
                
                # Taraf İhtimalleri
                if i > j: ms1 += p
                elif i == j: ms0 += p
                else: ms2 += p

                # Gol Üstü İhtimalleri
                tot = i + j
                if tot > 1.5: o15 += p
                if tot > 2.5: o25 += p
                if tot > 3.5: o35 += p

                # KG Var
                if i > 0 and j > 0: kg_var += p

                exact_scores.append((f"{i}-{j}", p * 100))

        exact_scores.sort(key=lambda x: x[1], reverse=True)

        # İlk Yarı Tahminleri
        exp_ht = (exp_home + exp_away) * 0.44
        iy_05 = (1 - poisson.pmf(0, exp_ht)) * 100
        iy_15 = (1 - poisson.pmf(0, exp_ht) - poisson.pmf(1, exp_ht)) * 100

        # Çifte Şans
        dc_1x = (ms1 + ms0) * 100
        dc_x2 = (ms0 + ms2) * 100
        dc_12 = (ms1 + ms2) * 100

        ms1_pct, ms0_pct, ms2_pct = ms1 * 100, ms0 * 100, ms2 * 100

        # Banko Öneri Seçici
        candidates = [
            ("1.5 Gol Üstü", o15 * 100),
            ("2.5 Gol Üstü", o25 * 100),
            ("İlk Yarı 0.5 Üstü", iy_05),
            ("Karşılıklı Gol Var", kg_var * 100),
            ("Çifte Şans 1X", dc_1x),
            ("Çifte Şans X2", dc_x2),
            ("Maç Sonucu 1", ms1_pct),
            ("Maç Sonucu 2", ms2_pct),
        ]
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_rec = candidates[0]

        # BANNER TAVSİYE
        st.success(f"💡 **Sistem Önerisi:** {top_rec[0]} (Güven Oranı: **%{top_rec[1]:.1f}**)")

        # SONUÇ EKRANI
        st.markdown("### 🎯 Maç Sonucu & Çifte Şans")
        c1, c2, c3 = st.columns(3)
        c1.metric("MS 1", f"%{ms1_pct:.1f}")
        c2.metric("MS 0 (X)", f"%{ms0_pct:.1f}")
        c3.metric("MS 2", f"%{ms2_pct:.1f}")

        c4, c5, c6 = st.columns(3)
        c4.metric("1X Çifte Şans", f"%{dc_1x:.1f}")
        c5.metric("1-2 Çifte Şans", f"%{dc_12:.1f}")
        c6.metric("X2 Çifte Şans", f"%{dc_x2:.1f}")

        st.markdown("### ⚽ Gol & KG İhtimalleri")
        g1, g2, g3 = st.columns(3)
        g1.metric("İY 0.5 Üst", f"%{iy_05:.1f}")
        g2.metric("1.5 Gol Üstü", f"%{o15*100:.1f}")
        g3.metric("2.5 Gol Üstü", f"%{o25*100:.1f}")

        g4, g5, g6 = st.columns(3)
        g4.metric("İY 1.5 Üst", f"%{iy_15:.1f}")
        g5.metric("3.5 Gol Üstü", f"%{o35*100:.1f}")
        g6.metric("KG Var", f"%{kg_var*100:.1f}")

        st.markdown("### 📊 En Olası 3 Skor Tahmini")
        s1, s2, s3 = st.columns(3)
        s1.metric(f"1. Skor ({exact_scores[0][0]})", f"%{exact_scores[0][1]:.1f}")
        s2.metric(f"2. Skor ({exact_scores[1][0]})", f"%{exact_scores[1][1]:.1f}")
        s3.metric(f"3. Skor ({exact_scores[2][0]})", f"%{exact_scores[2][1]:.1f}")
