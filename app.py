import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Tarifas SAESA por Comuna y Tarifa", layout="wide")
st.title("📊 Tarifas SAESA (por comuna y tipo de tarifa)")

# Inputs
comunas = [
    "Ancud", "Calbuco", "Castro", "Chonchi", "Cochamó", "Corral", "Curaco de Vélez",
    "Dalcahue", "Frutillar", "Futaleufú", "Futrono", "Hualaihué", "Lago Ranco", "Lanco",
    "La Unión", "Llanquihue", "Los Lagos", "Los Muermos", "Maullín", "Mariquina",
    "Osorno", "Paillaco", "Palena", "Panguipulli", "Puerto Montt", "Puqueldón", "Purranque",
    "Queilén", "Quemchi", "Quellón", "Río Bueno", "Río Negro", "San Juan de la Costa", "San Pablo",
    "Valdivia"
]
tarifas = ["BT1", "BT2", "BT3", "BT4", "TRBT", "TRAT", "BT5", "BT6", "TRBT2", "TRAT2", "TRBT3", "TRAT3"]

comuna = st.selectbox("Selecciona la comuna", comunas)
tipo_tarifa = st.selectbox("Selecciona el tipo de tarifa", tarifas)

uploaded_pdf = st.file_uploader("📎 Cargar archivo PDF del pliego tarifario", type="pdf")

def extraer_cargos_comuna_tarifa(pdf_file, comuna, tarifa):
    resultados = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and (comuna.lower() in text.lower()) and (tarifa.upper() in text.upper()):
                for line in text.split("\n"):
                    if any(k in line for k in ["Cargo", "$", "%", "kWh"]):
                        resultados.append({"Detalle": line.strip()})
    return pd.DataFrame(resultados)

if uploaded_pdf and st.button("📤 Buscar cargos"):
    st.info(f"🔍 Buscando cargos para {comuna} con tarifa {tipo_tarifa}...")
    df = extraer_cargos_comuna_tarifa(uploaded_pdf, comuna, tipo_tarifa)
    if not df.empty:
        st.success(f"✅ Se encontraron {len(df)} cargos para {comuna} con tarifa {tipo_tarifa}.")
        st.dataframe(df)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Cargos")
        output.seek(0)
        st.download_button("📥 Descargar resultados como Excel", data=output, file_name=f"tarifa_{tipo_tarifa}_{comuna}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("⚠️ No se encontraron coincidencias con los filtros seleccionados.")
