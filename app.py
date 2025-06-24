import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Tarifas SAESA por Tipo de Tarifa", layout="wide")
st.title("📊 Tarifas SAESA (por tipo de tarifa)")

# Inputs
tarifas = ["BT1", "BT2", "BT3", "BT4", "BT5", "BT6", "TRBT", "TRAT", "TRBT2", "TRAT2", "TRBT3", "TRAT3"]
tipo_tarifa = st.selectbox("Selecciona el tipo de tarifa", tarifas)
uploaded_pdf = st.file_uploader("📎 Cargar archivo PDF del pliego tarifario", type="pdf")

# Comunas extraídas del encabezado del pliego (ajustar si es necesario)
comunas_aplicables = [
    "Ancud", "Calbuco", "Castro", "Chonchi", "Cochamó", "Corral", "Curaco de Vélez",
    "Dalcahue", "Frutillar", "Futaleufú", "Futrono", "Hualaihué", "Lago Ranco", "Lanco",
    "La Unión", "Llanquihue", "Los Lagos", "Los Muermos", "Maullín", "Mariquina",
    "Osorno", "Paillaco", "Palena", "Panguipulli", "Puerto Montt", "Puqueldón", "Purranque",
    "Queilén", "Quemchi", "Quellón", "Río Bueno", "Río Negro", "San Juan de la Costa", "San Pablo",
    "Valdivia"
]

def extraer_por_tarifa(pdf_file, tarifa):
    resultados = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and tarifa.upper() in text.upper():
                for line in text.split("\n"):
                    if any(palabra in line for palabra in ["Cargo", "$", "%", "kWh"]):
                        resultados.append({"Detalle": line.strip()})
    return pd.DataFrame(resultados)

if uploaded_pdf and st.button("📤 Buscar cargos por tarifa"):
    st.info(f"🔍 Buscando cargos para tarifa {tipo_tarifa}...")
    df = extraer_por_tarifa(uploaded_pdf, tipo_tarifa)
    if not df.empty:
        st.success(f"✅ Se encontraron {len(df)} filas para tarifa {tipo_tarifa}.")
        st.dataframe(df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Tarifa")
        output.seek(0)
        st.download_button("📥 Descargar Excel", data=output, file_name=f"tarifa_{tipo_tarifa}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.markdown("---")
        st.markdown("ℹ️ **Comunas a las que aplica esta tarifa según el pliego:**")
        st.write(", ".join(comunas_aplicables))
    else:
        st.warning("⚠️ No se encontraron coincidencias con esa tarifa.")
