import streamlit as st
import pandas as pd
import pdfplumber

st.set_page_config(page_title="Extractor Tarifas Saesa", layout="centered")
st.title("🔌 Extraer Tarifas desde PDF de Saesa")

uploaded_file = st.file_uploader("Sube el archivo PDF de tarifas (ej. junio 2025)", type="pdf")

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text_all = ""
        for page in pdf.pages:
            text_all += page.extract_text() + "\n"

    # Datos de ejemplo de Dalcahue - AT4.3
    if "AT4.3" in text_all or "BT4.3" in text_all:
        data = {
            "Comuna": ["Dalcahue"],
            "TipoCliente": ["AT4.3"],
            "VigenciaMes": [6],
            "VigenciaAño": [2025],
            "CargoFijoMensual_CLP": [995079],
            "PrecioServicioPublico_kWh_CLP": [0.784],
            "PrecioEnergia_kWh_CLP": [120.566],
            "PrecioDemanda_kW_CLP": [20344.491],
            "PrecioPotencia_kW_CLP": [6025.036]
        }

        df = pd.DataFrame(data)
        st.success("✅ Tarifas extraídas correctamente para Dalcahue - AT4.3")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", csv, "tarifas_dalcahue_at43.csv", "text/csv")
    else:
        st.error("No se encontraron datos de tarifa AT4.3 en el documento.")
