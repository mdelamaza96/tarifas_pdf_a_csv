import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Tarifas SAESA desde PDF", layout="wide")
st.title("📊 Dashboard Tarifas SAESA (PDF Manual + Descarga Excel)")

# Inputs
mes = st.selectbox("Mes", ["enero","febrero","marzo","abril","mayo","junio",
                            "julio","agosto","septiembre","octubre","noviembre","diciembre"])
anio = st.number_input("Año", min_value=2020, max_value=datetime.now().year, value=datetime.now().year)

tarifas = ["BT1","BT2","BT3","BT4","TRBT","TRAT","AT","MT"]
tipo_tarifa = st.selectbox("Tipo de Tarifa", tarifas)

uploaded_pdf = st.file_uploader("📎 Cargar PDF de tarifas", type="pdf")

def extraer_tablas_tarifa(pdf_file, tarifa):
    tablas_filtradas = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table)
                if df.apply(lambda x: x.astype(str).str.contains(tarifa, case=False).any(), axis=1).any():
                    tablas_filtradas.append(table)
    return tablas_filtradas

def unir_tablas(tablas):
    if not tablas:
        return pd.DataFrame()
    tablas = [t for t in tablas if len(t) > 1]
    try:
        dfs = [pd.DataFrame(t[1:], columns=t[0]) for t in tablas]
        return pd.concat(dfs, ignore_index=True)
    except:
        return pd.DataFrame()

def convertir_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Tarifa")
    output.seek(0)
    return output

if uploaded_pdf and st.button("📤 Procesar PDF"):
    st.info("🔎 Buscando tablas con la tarifa seleccionada...")
    tablas = extraer_tablas_tarifa(uploaded_pdf, tipo_tarifa)
    df_resultado = unir_tablas(tablas)

    if not df_resultado.empty:
        st.success(f"✅ Se encontraron {len(df_resultado)} filas para la tarifa {tipo_tarifa}.")
        st.dataframe(df_resultado)

        excel_file = convertir_excel(df_resultado)
        st.download_button("📥 Descargar Excel", data=excel_file, file_name=f"tarifa_{tipo_tarifa.lower()}_{mes}_{anio}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("⚠️ No se encontraron tablas con esa tarifa.")
