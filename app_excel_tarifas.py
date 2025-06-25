import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Tarifas SAESA por Comuna y Tarifa", layout="wide")
st.title("📊 Consulta de Cargos por Comuna y Tarifa (SAESA)")

@st.cache_data
def cargar_datos():
    df_raw = pd.read_excel("datos_tarifas.xlsx", sheet_name="SAESA0625", header=None)

    # Buscar encabezados automáticamente
    header_index = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("TARIFA", case=False).any(), axis=1)].index[0]
    headers = df_raw.iloc[header_index]
    
    df_clean = df_raw[(header_index + 1):].reset_index(drop=True)
    df_clean.columns = headers

    # Renombrar columnas importantes
    df_clean = df_clean.rename(columns={
        headers[1]: "Tarifa",  # Columna B
        headers[2]: "Cargo",   # Columna C
        headers[3]: "Unidad de Medida"  # Columna D
    })

    return df_clean

# Cargar datos
df = cargar_datos()

# Listado de comunas
comunas = list(df.columns[4:])  # desde la columna después de "Unidad de Medida"
tarifas = df["Tarifa"].dropna().unique().tolist()

# Selección de usuario
comuna = st.selectbox("Selecciona una comuna", comunas)
tarifa = st.selectbox("Selecciona una tarifa", tarifas)

# Filtrar resultados
resultados_filtrados = df[df["Tarifa"] == tarifa][["Cargo", "Unidad de Medida", comuna]].dropna()

# Mostrar
if not resultados_filtrados.empty:
    st.success(f"✅ Se encontraron {len(resultados_filtrados)} cargos para {comuna} con tarifa {tarifa}.")
    st.dataframe(resultados_filtrados)

    # Descargar como Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        resultados_filtrados.to_excel(writer, index=False, sheet_name="Resultado")
    output.seek(0)
    st.download_button(
        "📥 Descargar como Excel",
        data=output,
        file_name=f"tarifas_{comuna}_{tarifa}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("⚠️ No se encontraron cargos para esa combinación.")
