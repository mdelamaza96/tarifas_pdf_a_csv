import streamlit as st
import pandas as pd

st.set_page_config(page_title="Extractor Tarifas Saesa - Excel", layout="centered")
st.title("🔌 Extraer Tarifas desde Excel de Saesa")

uploaded_file = st.file_uploader("Sube el archivo Excel de tarifas", type="xlsx")

if uploaded_file:
    comunas = [
        "Ancud", "Castro", "Chonchi", "Curaco De Vélez", "Dalcahue",
        "Puqueldón", "Queilén", "Quemchi", "Quellón", "Quinchao"
    ]
    tarifas = ["BT1", "BT2", "BT3", "AT3", "AT4.3"]

    comuna = st.selectbox("Selecciona la comuna", comunas)
    tarifa = st.selectbox("Selecciona la tarifa", tarifas)

    with st.spinner("Cargando dashboard con la información de tarifas..."):
        xls = pd.ExcelFile(uploaded_file)
        hojas = xls.sheet_names

        hoja_objetivo = None
        for hoja in hojas:
            if tarifa.upper() in hoja.upper():
                hoja_objetivo = hoja
                break

        if hoja_objetivo is None:
            st.warning(f"No se encontró una hoja que contenga la tarifa '{tarifa}'")
        else:
            df = pd.read_excel(xls, sheet_name=hoja_objetivo, dtype=str)
            df.fillna("", inplace=True)

            fila_comunas = df.iloc[8]
            mapa_columnas = {}
            for i, valor in enumerate(fila_comunas):
                if isinstance(valor, str) and "-" in valor:
                    nombre = valor.split("-")[0].strip().lower()
                    mapa_columnas[nombre] = i

            comuna_lower = comuna.lower()
            if comuna_lower not in mapa_columnas:
                st.warning(f"No se encontró la comuna '{comuna}' en la hoja de la tarifa '{tarifa}'")
            else:
                col_neto = mapa_columnas[comuna_lower]
                col_iva = col_neto + 1

                inicio_filas = 12
                fin_filas = 35

                cargos = df.iloc[inicio_filas:fin_filas, [1, 2]]
                valores_neto = df.iloc[inicio_filas:fin_filas, col_neto]
                valores_iva = df.iloc[inicio_filas:fin_filas, col_iva]

                df_tarifas = pd.DataFrame({
                    "Cargo": cargos.iloc[:, 0].values,
                    "Unidad": cargos.iloc[:, 1].values,
                    "Neto_CLP": valores_neto.values,
                    "Con_IVA_CLP": valores_iva.values
                }).dropna(subset=["Cargo"]).reset_index(drop=True)

                st.success(f"✅ Cargos extraídos para {comuna} - {tarifa}")
                st.dataframe(df_tarifas)

                csv = df_tarifas.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Descargar CSV", csv, f"tarifas_{comuna}_{tarifa}.csv", "text/csv")
