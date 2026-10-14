import streamlit as st
from PIL import Image
from google import genai

# Sayfa Ayarları
st.set_page_config(page_title="İY/MS Analiz ve Tahmin Asistanı", layout="wide")

st.title("⚽ İY/MS (İlk Yarı / Maç Sonucu) Yapay Zeka Analizörü")
st.write("Bülten ekran görüntüsünü yükleyin, sistem İY/MS potansiyeli en yüksek maçları çıkarsın.")

# API Key Girişi (Gemini API)
api_key = st.sidebar.text_input("Gemini API Key Giriniz:", type="password")

uploaded_file = st.file_uploader("Bülten Görselini Yükleyin (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file and api_key:
    image = Image.open(uploaded_file)
    st.image(image, caption="Yüklenen Bültenden Kesit", use_column_width=True)
    
    if st.button("📊 Maçları Analiz Et ve İY/MS Önerilerini Getir"):
        with st.spinner("Bültendeki tüm maçlar ve istatistikler analiz ediliyor..."):
            try:
                client = genai.Client(api_key=api_key)
                
                prompt = """
                Sen uzman bir iddaa ve bahis istatistik analizörüsün.
                Sana verilen bülten görselindeki tüm maçları incele.
                
                Özellikle şu İY/MS (İlk Yarı / Maç Sonucu) senaryolarına odaklan:
                1. Ters Gelme / Geri Dönüş Potansiyeli (1/2 veya 2/1)
                2. Beraberlik Kilitlenmesi / İkinci Yarı Çözülme (1/0 veya 2/0)
                3. Erken Dominasyon / Banko (1/1 veya 2/2)
                
                Lütfen çıktıyı şu formatta ver:
                - **Maç Adı ve Saati**
                - **Önerilen İY/MS Tercihi**
                - **Analiz ve Neden Bu Seçim yapıldı? (Takım yapıları, oran uyumu)**
                - **Güven Seviyesi (%):**
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[image, prompt]
                )
                
                st.success("Analiz Tamamlandı!")
                st.markdown("---")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
elif not api_key and uploaded_file:
    st.warning("Lütfen sol menüden Gemini API Key'inizi giriniz.")
