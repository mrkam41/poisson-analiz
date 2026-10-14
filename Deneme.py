import os
import streamlit as st
from PIL import Image
from google import genai

# API Key'i ortam değişkenine atıyoruz
os.environ["GEMINI_API_KEY"] = "AIzaSy_KENDI_API_KEYINIZI_YAPIŞTIRIN"

# Sayfa Yapılandırması
st.set_page_config(
    page_title="⚽ İY/MS Analizör & Tahmin Asistanı",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ İY/MS Yapay Zeka Analiz Sistemi")

uploaded_file = st.file_uploader("📸 Bülten Görselini Yükleyin (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Yüklenen İddaa Bülteninden Kesit", use_column_width=True)
    
    if st.button("📊 İY/MS Detaylı Analiz Et", type="primary"):
        with st.spinner("Bültendeki tüm maçlar, oranlar ve takımlar analiz ediliyor..."):
            try:
                # İstemci otomatik olarak GEMINI_API_KEY ortam değişkenini okur
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
                
                st.success("Analiz Başarıyla Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")
