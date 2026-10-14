# -*- coding: utf-8 -*-
import os
import sys
import streamlit as st
from PIL import Image
from google import genai

# Python sistem varsayilan kodlamasini UTF-8 yap
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# API Key'inizi buraya yapistirin (Ortam degiskeni olarak ayarlanir)
os.environ["GEMINI_API_KEY"] = "BURAYA_GEMINI_API_KEY_YAPISTIRIN"

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
        with st.spinner("Bultendeki tum maclar analiz ediliyor..."):
            try:
                # Client otomatik olarak GEMINI_API_KEY ortam degiskenini okur
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
