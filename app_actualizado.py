import streamlit as st
import pandas as pd
import pdfplumber
import re

st.set_page_config(page_title="Extractor Tarifas Saesa", layout="centered")
st.title("🔌 Extraer Tarifas desde PDF de Saesa")

uploaded_file = st.file_uploader("Sube el archivo PDF de tarifas (ej. junio 2025)", type="pdf")

if uploaded_file:
    comunas = ["Ancud", "Castro", "Chonchi", "Curaco de Vélez", "Dalcahue", "Puqueldón", "Queilén", "Quemchi", "Quellón", "Quinchao"]
    tarifas = ["BT1", "BT2", "BT3", "AT3", "AT4.3"]

    comuna_seleccionada = st.selectbox("Selecciona la comuna", comunas)
    tarifa_seleccionada = st.selectbox("Selecciona la tarifa", tarifas)

    with pdfplumber.open(uploaded_file) as pdf:
        tablas = []
        for page in pdf.pages:
            try:
                tables = page.extract_tables()
                tablas.extend(tables)
            except:
                continue

    datos = []

    for tabla in tablas:
        for fila in tabla:
            fila_limpia = [str(item).strip() if item else "" for item in fila]
            fila_texto = " ".join(fila_limpia).lower()
            if comuna_seleccionada.lower() in fila_texto and tarifa_seleccionada.lower() in fila_texto:
                datos.append(fila_limpia)

    if datos:
        # Suponiendo que los campos están en posiciones conocidas dentro de la fila
        try:
            fila = datos[0]  # Tomamos la primera coincidencia

            def extraer_valor(valor):
                valor = re.sub(r'[^0-9,\.]', '', valor)
                valor = valor.replace(',', '.')
                try:
                    return float(valor)
                except:
                    return None

            df = pd.DataFrame({
                "Comuna": [comuna_seleccionada],
                "TipoCliente": [tarifa_seleccionada],
                "VigenciaMes": [6],
                "VigenciaAño": [2025],
                "CargoFijoMensual_CLP": [extraer_valor(fila[1]) if len(fila) > 1 else None],
                "PrecioServicioPublico_kWh_CLP": [extraer_valor(fila[2]) if len(fila) > 2 else None],
                "PrecioEnergia_kWh_CLP": [extraer_valor(fila[3]) if len(fila) > 3 else None],
                "PrecioDemanda_kW_CLP": [extraer_valor(fila[4]) if len(fila) > 4 else None],
                "PrecioPotencia_kW_CLP": [extraer_valor(fila[5]) if len(fila) > 5 else None]
            })

            st.success(f"✅ Valores extraídos para {comuna_seleccionada} - {tarifa_seleccionada}")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Descargar CSV", csv, f"tarifas_{comuna_seleccionada}_{tarifa_seleccionada}.csv", "text/csv")

        except Exception as e:
            st.error("No se pudo interpretar correctamente la fila encontrada.")
            st.text(str(e))
    else:
        st.warning("No se encontraron coincidencias exactas para la comuna y tarifa seleccionadas. Revisa el PDF o intenta con otra combinación.")
