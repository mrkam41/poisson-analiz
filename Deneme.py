# -*- coding: utf-8 -*-
import os
import sys
import streamlit as st
from PIL import Image
from google import genai

# =========================================================================
# 🔑 AŞAĞIDAKİ ÇİFT TIRNAK İÇİNE KENDİ GEMINI API KEY'İNİZİ YAPIŞTIRIN:
# =========================================================================
MY_API_KEY = "AIzaSy_BURAYA_KENDI_API_KEYINIZI_YAPISTIRIN"

# API Key temizliği ve sistem değişkenine aktarılması
CLEAN_KEY = MY_API_KEY.strip()
os.environ["GEMINI_API_KEY"] = CLEAN_KEY

# Sayfa Yapilandirmasi
st.set_page_config(
    page_title="IY/MS Analizor & Tahmin Asistani",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ IY/MS Yapay Zeka Analiz Sistemi")
st.markdown("Bulten ekran goruntusunu yukleyin; sistem **1/2, 2/1, 1/0, 2/0** ve **1/1 - 2/2** potansiyeli yuksek maclari cikarsin.")

uploaded_file = st.file_uploader("📸 Bulten Gorselini Yukleyin (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Yuklenen Bultenden Kesit", use_column_width=True)
    
    if st.button("📊 IY/MS Detayli Analiz Et", type="primary"):
        # API Key Kontrolü
        if not CLEAN_KEY or "BURAYA_KENDI_API_KEYINIZI_YAPISTIRIN" in CLEAN_KEY:
            st.error("⚠️ Lutfen app.py dosyasinin en ustundeki MY_API_KEY kismina kendi geçerli Gemini API Key'inizi yapistirin!")
        else:
            with st.spinner("Bultendeki tum maclar analiz ediliyor..."):
                try:
                    # Client ortam değişkenindeki GEMINI_API_KEY değerini okur
                    client = genai.Client()
                    
                    prompt = """
                    Sen uzman bir iddaa ve bahis istatistik analizörüsün.
                    Görseldeki tüm maçları incele.
                    
                    Özellikle şu İY/MS (İlk Yarı / Maç Sonucu) senaryolarına odaklan:
                    1. Ters Gelme / Geri Dönüş Potansiyeli (1/2 veya 2/1)
                    2. Beraberlik Kilitlenmesi / İkinci Yarı Çözülme (1/0 veya 2/0)
                    3. Erken Dominasyon / Banko (1/1 veya 2/2)
                    
                    Çıktıyı düzgün Markdown formatında şu başlıklarla ver:
                    - **Maç Adı ve Saati**
                    - **Önerilen İY/MS Tercihi**
                    - **İstatistiksel Neden / Analiz**
                    - **Güven Derecesi (%)**
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[image, prompt]
                    )
                    
                    st.success("Analiz Basariyla Tamamlandi!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Bir hata olustu: {str(e)}")
