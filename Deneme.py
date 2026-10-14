import streamlit as st
from PIL import Image
from google import genai

# =========================================================
# 🔑 API KEY'İNİZİ AŞAĞIDAKİ TIKNAKLARIN İÇİNE YAPIŞTIRIN
# =========================================================
RAW_API_KEY = "AQ.Ab8RN6L9SIeHkACTIzOuPAclyERZr8CtbCqg3ICSDP_U9qJ-IQ"

# API Key temizleme (fark etmeden eklenen boşluk/satır başlarını siler)
API_KEY = RAW_API_KEY.strip()

# Sayfa Yapılandırması
st.set_page_config(
    page_title="⚽ İY/MS Analizör & Tahmin Asistanı",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ İY/MS Yapay Zeka Analiz Sistemi")
st.markdown("Bülten ekran görüntüsünü yükleyin; sistem **1/2, 2/1, 1/0, 2/0** ve **1/1 - 2/2** potansiyeli yüksek maçları çıkarsın.")

uploaded_file = st.file_uploader("📸 Bülten Görselini Yükleyin (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Yüklenen İddaa Bülteninden Kesit", use_column_width=True)
    
    if st.button("📊 İY/MS Detaylı Analiz Et", type="primary"):
        # API Key kontrolü
        if not API_KEY or API_KEY == "BURAYA_GEMINI_API_KEY_YAPISTIRIN":
            st.error("⚠️ Lütfen app.py dosyasındaki RAW_API_KEY değişkenine geçerli bir Gemini API Key ekleyin.")
        else:
            with st.spinner("Bültendeki tüm maçlar, oranlar ve takımlar analiz ediliyor..."):
                try:
                    # GenAI Client başlatma
                    client = genai.Client(api_key=API_KEY)
                    
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
                    error_msg = str(e)
                    if "API_KEY_INVALID" in error_msg or "400" in error_msg:
                        st.error("❌ Hata: Girdiğiniz API Key geçersiz veya hatalı. Lütfen Google AI Studio'dan aldığınız key'i kontrol edip tekrar yapıştırın.")
                    else:
                        st.error(f"Bir hata oluştu: {error_msg}")
