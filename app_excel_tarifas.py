import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Tarifas SAESA por Comuna y Tarifa", layout="wide")
st.title("📊 Consulta de Cargos por Comuna y Tarifa (SAESA)")

# Obtener hojas disponibles en el archivo Excel
@st.cache_data
def obtener_hojas():
    xls = pd.ExcelFile("datos_tarifas.xlsx")
    return xls.sheet_names

# Cargar datos desde una hoja específica
@st.cache_data
def cargar_datos(nombre_hoja):
    df_raw = pd.read_excel("datos_tarifas.xlsx", sheet_name=nombre_hoja, header=None)

    # Buscar la fila donde aparece "TARIFA"
    header_index = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("TARIFA", case=False).any(), axis=1)].index[0]
    headers = df_raw.iloc[header_index]
    
    df_clean = df_raw[(header_index + 1):].reset_index(drop=True)
    df_clean.columns = headers

    # Renombrar columnas clave
    df_clean = df_clean.rename(columns={
        headers[1]: "Tarifa",             # Columna B
        headers[2]: "Cargo",              # Columna C
        headers[3]: "Unidad de Medida"    # Columna D
    })

    return df_clean

# Selección de mes/año (hoja del Excel)
hojas = obtener_hojas()
hoja_seleccionada = st.selectbox("Selecciona el mes/año del pliego tarifario", hojas)

# Cargar datos según hoja seleccionada
df = cargar_datos(hoja_seleccionada)

# Listar comunas y tarifas
comunas = list(df.columns[4:])  # A partir de la columna después de "Unidad de Medida"
tarifas = df["Tarifa"].dropna().unique().tolist()

# Selección de comuna y tarifa
comuna = st.selectbox("Selecciona una comuna", comunas)
tarifa = st.selectbox("Selecciona una tarifa", tarifas)

# Filtrar resultados
resultados = df[df["Tarifa"] == tarifa][["Cargo", "Unidad de Medida", comuna]].dropna()

# Mostrar resultados
if not resultados.empty:
    st.success(f"✅ Se encontraron {len(resultados)} cargos para {comuna} con tarifa {tarifa}.")
    st.dataframe(resultados)

    # Descargar como Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        resultados.to_excel(writer, index=False, sheet_name="Resultado")
    output.seek(0)
    st.download_button(
        "📥 Descargar como Excel",
        data=output,
        file_name=f"{hoja_seleccionada}_{comuna}_{tarifa}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("⚠️ No se encontraron cargos para esa combinación.")
