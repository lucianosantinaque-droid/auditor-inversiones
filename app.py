import streamlit as st
import yfinance as yf
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Auditor de Inversiones", page_icon="📈", layout="centered")

# --- CONFIGURACIÓN DE IA (Acá va tu llave) ---
# REEMPLAZA EL TEXTO ENTRE COMILLAS POR TU API KEY REAL
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)
modelo_vision = genai.GenerativeModel('gemini-1.5-flash')

def buscar_cedear(ticker):
    """Busca en Yahoo Finance si existe el CEDEAR en la bolsa argentina"""
    ticker_ba = f"{ticker}.BA"
    try:
        activo = yf.Ticker(ticker_ba)
        info = activo.info
        if 'shortName' in info:
            div_yield = info.get('dividendYield', 0)
            if div_yield is None: div_yield = 0
            return True, div_yield * 100
        return False, 0
    except:
        return False, 0

# --- INTERFAZ VISUAL ---
st.title("📊 Auditoría de Inversiones")
st.write("Subí una captura de Finviz o Yahoo Finance y obtené un diagnóstico.")

imagen_subida = st.file_uploader("Cargar captura de pantalla (JPG/PNG)", type=["jpg", "png", "jpeg"])
ticker_input = st.text_input("Ticker de la empresa (Ej: AAPL, AMD, SONY):", max_chars=5)

if imagen_subida is not None and ticker_input:
    imagen = Image.open(imagen_subida)
    st.image(imagen, caption="Captura a analizar", use_column_width=True)
    
    if st.button("🔍 Analizar Empresa"):
        with st.spinner("Procesando datos con Inteligencia Artificial..."):
            
            # Análisis con IA
            prompt = """
            Sos un experto en finanzas. Analizá esta tabla.
            Extraé los KPIs más importantes (P/E, Margen, ROE, Deuda, Crecimiento esperado).
            Danos una lectura profesional sobre la salud de la empresa y si el precio está caro o barato.
            Finalizá con un consejo claro de tres escenarios: Conservador, Moderado o Agresivo sobre si entrar o no.
            """
            respuesta_ia = modelo_vision.generate_content([prompt, imagen])
            
            # Buscar CEDEAR
            ticker = ticker_input.upper()
            existe_cedear, div_porcentaje = buscar_cedear(ticker)
            ganancia_100_usd = 100 * (div_porcentaje / 100)
            
            # Mostrar Resultados
            st.divider()
            st.subheader("📝 Veredicto Profesional")
            st.write(respuesta_ia.text)
            
            st.divider()
            st.subheader("🇦🇷 Disponibilidad Local y Dividendos")
            if existe_cedear:
                st.success(f"✅ ¡Excelente! Existe un CEDEAR para {ticker} (operable en pesos).")
            else:
                st.warning(f"❌ No se detectó un CEDEAR local para {ticker}.")
                
            st.info(f"💸 **Dividendos:** Según el rendimiento anual ({div_porcentaje:.2f}%), por cada 100 USD invertidos, cobrarías aprox **${ganancia_100_usd:.2f} USD brutos al año**.")
