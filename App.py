import streamlit as st


def iy_ms_potansiyel_hesapla(
    ev_oran, iy_ms_oran, ev_pace, ev_att, ev_def_yedigi, son_iki_skor, tercih_turu
):
    """Geliştirdiğimiz veri modeline göre maça 2/1 veya 1/2 potansiyel skoru (0-100) atar."""
    puan = 0
    sebepler = []

    if tercih_turu == "2/1 (Ev Sahibi Geri Dönüşü)":
        # 1. Nokta Oran Kontrolü (En çok gelen 19.00 - 22.00 bantı)
        if 18.50 <= iy_ms_oran <= 22.50 or 1.30 <= ev_oran <= 1.60:
            puan += 30
            sebepler.append(
                f"Oran Kriteri Uyumlu (2/1 Oranı: {iy_ms_oran} / MS1: {ev_oran})"
            )
        elif 22.50 < iy_ms_oran <= 25.00:
            puan += 15
            sebepler.append("Oran Kriteri Orta Derece Uyumlu")

        # 2. Oyun Temposu (Pace) ve Hücum Gücü
        if ev_pace >= 65 and ev_att >= 1.8:
            puan += 30
            sebepler.append(
                f"Yüksek Oyun Temposu ({ev_pace}) ve Güçlü Hücum ({ev_att} gol/maç)"
            )

        # 3. Savunma Zafiyeti (Erken gol yeme ihtimali)
        if ev_def_yedigi >= 1.0:
            puan += 15
            sebepler.append(
                f"Ev Sahibi Kalesini Kapatamıyor ({ev_def_yedigi} gol yeme ort.)"
            )

        # 4. Geçmiş 2 Maç Skor Kalıbı
        en_iyi_kaliplar = [
            "2-1 -> 1-0",
            "2-0 -> 2-1",
            "1-1 -> 2-1",
            "1-0 -> 2-0",
            "3-1 -> 2-0",
        ]
        if son_iki_skor in en_iyi_kaliplar:
            puan += 25
            sebepler.append(f"Geçmiş 2 Maç Dizilimi Birebir Eşleşiyor ({son_iki_skor})")

    elif tercih_turu == "1/2 (Deplasman Geri Dönüşü)":
        # 1/2 Oran Kontrolü (En çok gelen 23.00 - 28.00 bantı)
        if 23.00 <= iy_ms_oran <= 28.00:
            puan += 35
            sebepler.append(f"1/2 Nokta Oran Bandı Uyumlu ({iy_ms_oran})")

        if ev_pace >= 70:
            puan += 35
            sebepler.append(f"Çok Yüksek Lig/Maç Temposu ({ev_pace})")

        if ev_def_yedigi >= 1.5:
            puan += 30
            sebepler.append(
                f"Ev Sahibi Savunması Çok Dağınık ({ev_def_yedigi} gol yeme ort.)"
            )

    return puan, sebepler


# --- STREAMLIT ARAYÜZÜ ---
st.title("🎯 İY/MS (2/1 - 1/2) Maç Bulucu & Filtre Modülü")

col1, col2 = st.columns(2)

with col1:
    tercih_turu = st.selectbox(
        "Hedef Tercih Türü",
        ["2/1 (Ev Sahibi Geri Dönüşü)", "1/2 (Deplasman Geri Dönüşü)"],
    )
    ev_takim = st.text_input("Ev Sahibi Takım", "Glentoran")
    dep_takim = st.text_input("Deplasman Takımı", "Dungannon")
    ev_oran = st.number_input("MS 1 Oranı", value=1.40, step=0.05)
    iy_ms_oran = st.number_input("İY/MS Oranı (2/1 veya 1/2)", value=21.10, step=0.50)

with col2:
    ev_pace = st.number_input("Ev Sahibi Tempo (Pace)", value=68.0, step=1.0)
    ev_att = st.number_input("Ev Sahibi Attığı Gol Ort.", value=2.1, step=0.1)
    ev_def = st.number_input("Ev Sahibi Yediği Gol Ort.", value=1.2, step=0.1)
    son_iki_skor = st.selectbox(
        "Ev Sahibi Son 2 Maç Dizilimi",
        [
            "2-1 -> 1-0",
            "2-0 -> 2-1",
            "1-1 -> 2-1",
            "1-0 -> 2-0",
            "3-1 -> 2-0",
            "Diğer / Uymuyor",
        ],
    )

if st.button("Maçın İY/MS Potansiyelini Hesapla"):
    puan, sebepler = iy_ms_potansiyel_hesapla(
        ev_oran,
        iy_ms_oran,
        ev_pace,
        ev_att,
        ev_def,
        son_iki_skor,
        tercih_turu,
    )

    st.markdown("---")
    st.subheader(f"📊 Analiz Sonucu: {ev_takim} vs {dep_takim}")

    # Derecelendirme Çıktısı
    if puan >= 75:
        st.success(
            f"🔥 **GÜÇLÜ İY/MS ADAYI (Uygunluk Skoru: %{puan})**\n\nBu maç kurguladığımız geri dönüş kriterlerine tam oturuyor."
        )
    elif puan >= 50:
        st.warning(
            f"⚠️ **ORTA SEVİYE ADAY (Uygunluk Skoru: %{puan})**\n\nSistemde bazı kriterleri karşılıyor, sürpriz kuponlarda değerlendirilebilir."
        )
    else:
        st.error(
            f"❌ **DÜŞÜK POTANSİYEL (Uygunluk Skoru: %{puan})**\n\nBu maçın 2/1 veya 1/2 bitme ihtimali istatistiksel olarak zayıf."
        )

    st.write("### 🔍 Modelin Tespit Ettiği Kriterler:")
    for sebep in sebepler:
        st.write(f"- ✅ {sebep}")
