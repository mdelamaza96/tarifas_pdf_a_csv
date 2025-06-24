# Requisitos previos:
# pip install streamlit PyPDF2 requests pandas

import streamlit as st
import os
import requests
import pandas as pd
from datetime import datetime
import PyPDF2
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="Tarifas SAESA", layout="wide")
st.title("📊 Dashboard Tarifas SAESA")

# === Inputs del usuario ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    mes = st.selectbox("Selecciona el mes", options=[
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"])

with col2:
    anio = st.number_input("Ingresa el año", min_value=2020, max_value=datetime.now().year, value=datetime.now().year)

comunas_disponibles = [
    "Osorno", "Puerto Montt", "Valdivia", "Ancud", "Castro", "Quellón",
    "Frutillar", "La Unión", "Río Bueno", "Chonchi", "Dalcahue", "Purranque"
]
tarifas_disponibles = ["BT1", "BT2", "BT3", "BT4", "AT", "MT"]

with col3:
    comuna = st.selectbox("Selecciona tu comuna", options=comunas_disponibles)

with col4:
    tipo_tarifa = st.selectbox("Tipo de tarifa", options=tarifas_disponibles)

# Funciones auxiliares
def descargar_pdf(mes: str, anio: int) -> str:
    mes_lower = mes.lower()
    url = f"https://www.saesa.cl/media/1dldnwnn/pliego-tarifario-{mes_lower}-{anio}.pdf"
    local_path = f"pliego_{mes_lower}_{anio}.pdf"
    response = requests.get(url, verify=False)
    
    if response.status_code == 200 and response.headers['Content-Type'] == 'application/pdf':
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return local_path
    else:
        return None

def extraer_cargos(pdf_path: str, comuna: str, tipo_tarifa: str):
    data = []
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text and comuna.lower() in text.lower() and tipo_tarifa.upper() in text.upper():
                lineas = text.split('\n')
                for i, linea in enumerate(lineas):
                    if comuna.lower() in linea.lower() and tipo_tarifa.upper() in linea.upper():
                        for j in range(i, min(i+20, len(lineas))):
                            if any(x in lineas[j] for x in ["Cargo", "$", "%", "kWh"]):
                                data.append({"Descripción": lineas[j]})
    return data

if mes and anio and comuna and tipo_tarifa:
    with st.spinner("Descargando pliego tarifario..."):
        pdf_path = descargar_pdf(mes, anio)

    if pdf_path:
        st.success("Pliego descargado exitosamente")
        with st.spinner("Buscando información en el documento..."):
            resultados = extraer_cargos(pdf_path, comuna, tipo_tarifa)
            if resultados:
                df_resultados = pd.DataFrame(resultados)
                st.subheader(f"Resultados para {comuna.title()} - Tarifa {tipo_tarifa.upper()}")
                st.dataframe(df_resultados, use_container_width=True)
            else:
                st.warning("No se encontraron datos coincidentes con los criterios ingresados.")
        os.remove(pdf_path)
    else:
        st.error("No se pudo descargar el pliego tarifario. Verifica que el mes y año estén disponibles.")
else:
    st.info("Por favor, completa todos los campos para comenzar.")
