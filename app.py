import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Tarifas SAESA por Comuna y Tipo de Tarifa", layout="wide")
st.title("📊 Tarifas SAESA (por comuna y tipo de tarifa)")

# Subida de archivo Excel
uploaded_excel = st.file_uploader("📎 Cargar archivo Excel con las tarifas", type=["xlsx"])

if uploaded_excel:
    try:
        df = pd.read_excel(uploaded_excel)
        # Normalización de nombres de columna para evitar errores
        df.columns = [col.strip().lower() for col in df.columns]

        # Verifica que existan las columnas requeridas
        if "comuna" in df.columns and "tipo_tarifa" in df.columns:
            comunas = sorted(df["comuna"].dropna().unique())
            tarifas = sorted(df["tipo_tarifa"].dropna().unique())

            comuna = st.selectbox("Selecciona la comuna", comunas)
            tarifa = st.selectbox("Selecciona el tipo de tarifa", tarifas)

            # Filtra según selección
            filtrado = df[(df["comuna"] == comuna) & (df["tipo_tarifa"] == tarifa)]

            if not filtrado.empty:
                st.success(f"✅ Se encontraron {len(filtrado)} filas para {comuna} y tarifa {tarifa}.")
                st.dataframe(filtrado)

                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    filtrado.to_excel(writer, index=False, sheet_name="Filtrado")
                output.seek(0)
                st.download_button(
                    "📥 Descargar Excel filtrado",
                    data=output,
                    file_name=f"tarifa_{comuna}_{tarifa}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("⚠️ No se encontraron coincidencias para esa comuna y tarifa.")
        else:
            st.error("El archivo debe contener las columnas 'comuna' y 'tipo_tarifa'.")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel con las columnas 'comuna' y 'tipo_tarifa'.")
