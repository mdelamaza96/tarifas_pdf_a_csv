import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Tarifas SAESA por Comuna y Tarifa", layout="wide")
st.title("📊 Consulta de Cargos por Comuna y Tarifa (SAESA)")

# Cargar archivo Excel local
@st.cache_data
def cargar_datos():
    df_raw = pd.read_excel("datos_tarifas.xlsx", sheet_name="SAESA0625", header=None)
    header_row = df_raw.iloc[1]  # fila con nombres reales de columnas
    df_clean = df_raw.drop([0, 1]).reset_index(drop=True)
    df_clean.columns = header_row
    df_clean = df_clean.rename(columns={df_clean.columns[0]: "Index", df_clean.columns[1]: "Tarifa", df_clean.columns[2]: "Cargo"})
    return df_clean

df = cargar_datos()

# Obtener comunas disponibles desde columnas (desde la 4° en adelante)
comunas = list(df.columns[3:])
tarifas = df["Tarifa"].dropna().unique().tolist()

# Entradas del usuario
comuna = st.selectbox("Selecciona una comuna", comunas)
tarifa = st.selectbox("Selecciona una tarifa", tarifas)

# Filtrar según selección
resultados = df[df["Tarifa"] == tarifa][["Cargo", comuna]].dropna()

# Mostrar resultados
if not resultados.empty:
    st.success(f"✅ Se encontraron {len(resultados)} cargos para {comuna} con tarifa {tarifa}.")
    st.dataframe(resultados)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        resultados.to_excel(writer, index=False, sheet_name="Resultado")
    output.seek(0)
    st.download_button("📥 Descargar como Excel", data=output, file_name=f"tarifas_{comuna}_{tarifa}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.warning("⚠️ No se encontraron cargos para esa combinación.")
