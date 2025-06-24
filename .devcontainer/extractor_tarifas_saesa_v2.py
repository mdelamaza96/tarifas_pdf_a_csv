
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Extractor Tarifas Saesa - Excel", layout="centered")
st.title("🔌 Extraer Tarifas desde Excel de Saesa")

uploaded_file = st.file_uploader("Sube el archivo Excel de tarifas", type="xlsx")

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")
        st.stop()

    comunas = [
        "Ancud", "Castro", "Chonchi", "Curaco De Vélez", "Dalcahue",
        "Puqueldón", "Queilén", "Quemchi", "Quellón", "Quinchao"
    ]
    tarifas = ["BT1", "BT2", "BT3", "AT3", "AT4.3"]

    comuna = st.selectbox("Selecciona la comuna", comunas)
    tarifa = st.selectbox("Selecciona la tarifa", tarifas)

    with st.spinner("Cargando dashboard con la información de tarifas..."):
        hojas = xls.sheet_names
        st.write("📄 Hojas encontradas en el archivo:", hojas)  # Mostrar para depuración

        hoja_objetivo = None
        tarifa_clean = tarifa.replace(".", "").replace(" ", "").lower()
        for hoja in hojas:
            hoja_clean = hoja.replace(".", "").replace(" ", "").lower()
            if tarifa_clean in hoja_clean:
                hoja_objetivo = hoja
                break

        if hoja_objetivo is None:
            st.warning(f"No se encontró una hoja que contenga la tarifa '{tarifa}'")
        else:
            df = pd.read_excel(xls, sheet_name=hoja_objetivo, dtype=str)
            df.fillna("", inplace=True)

            if len(df) < 36:
                st.error("La hoja seleccionada no tiene suficientes filas para extraer los datos.")
                st.stop()

            fila_comunas = df.iloc[8]
            mapa_columnas = {
                valor.split("-")[0].strip().lower(): i
                for i, valor in enumerate(fila_comunas)
                if isinstance(valor, str) and "-" in valor
            }

            comuna_lower = comuna.lower()
            if comuna_lower not in mapa_columnas:
                st.warning(f"❌ No se encontró la comuna '{comuna}' en la hoja '{hoja_objetivo}'. Verifica si está correctamente escrita.")
                st.stop()
            else:
                col_neto = mapa_columnas[comuna_lower]
                col_iva = col_neto + 1

                inicio_filas = 12
                fin_filas = 35

                if df.shape[1] <= col_iva:
                    st.error("La hoja no tiene suficientes columnas para leer los valores de tarifa.")
                    st.stop()

                cargos = df.iloc[inicio_filas:fin_filas, [1, 2]]
                valores_neto = df.iloc[inicio_filas:fin_filas, col_neto]
                valores_iva = df.iloc[inicio_filas:fin_filas, col_iva]

                df_tarifas = pd.DataFrame({
                    "Cargo": cargos.iloc[:, 0].values,
                    "Unidad": cargos.iloc[:, 1].values,
                    "Neto_CLP": valores_neto.values,
                    "Con_IVA_CLP": valores_iva.values
                }).dropna(subset=["Cargo"]).reset_index(drop=True)

                df_tarifas["Neto_CLP"] = pd.to_numeric(df_tarifas["Neto_CLP"], errors='coerce')
                df_tarifas["Con_IVA_CLP"] = pd.to_numeric(df_tarifas["Con_IVA_CLP"], errors='coerce')

                st.success(f"✅ Cargos extraídos para {comuna} - {tarifa}")
                st.dataframe(df_tarifas.style.format({
                    "Neto_CLP": "${:,.0f}",
                    "Con_IVA_CLP": "${:,.0f}"
                }))

                csv = df_tarifas.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Descargar CSV", csv, f"tarifas_{comuna}_{tarifa}.csv", "text/csv")

                # Botón de descarga de Excel
                from io import BytesIO
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_tarifas.to_excel(writer, index=False, sheet_name="Tarifas")
                buffer.seek(0)
                st.download_button("📥 Descargar Excel", buffer, f"tarifas_{comuna}_{tarifa}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
