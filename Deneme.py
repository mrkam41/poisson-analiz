import streamlit as st
from PIL import Image
from google import genai

# Sayfa Yapılandırması
st.set_page_config(
    page_title="⚽ İY/MS Analizör & Tahmin Asistanı",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ İY/MS Yapay Zeka Analiz Sistemi")
st.markdown("Bülten ekran görüntüsünü yükleyin; sistem **1/2, 2/1, 1/0, 2/0** ve **1/1 - 2/2** potansiyeli yüksek maçları çıkarsın.")

# Yan Menü: API Key Kontrolü (Streamlit Secrets veya Kullanıcı Girişi)
st.sidebar.header("🔑 Bağlantı Ayarları")

# Önce Streamlit Secrets kontrol edilir, yoksa kullanıcıdan istenir
api_key = None
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.sidebar.success("API Anahtarı Tanımlı (Secrets) ✅")
else:
    api_key = st.sidebar.text_input("Gemini API Key Giriniz:", type="password")
    st.sidebar.info("[Buradan ücretsiz API key alabilirsiniz](https://aistudio.google.com/)")

uploaded_file = st.file_uploader("📸 Bülten Görselini Yükleyin (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Yüklenen İddaa Bültenden Kesit", use_column_width=True)
    
    if st.button("📊 İY/MS Detaylı Analiz Et", type="primary"):
        if not api_key:
            st.error("Lütfen devam etmek için Gemini API Key girin.")
        else:
            with st.spinner("Bültendeki tüm maçlar, oranlar ve takımlar analiz ediliyor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
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
