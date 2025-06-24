import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import PyPDF2
import pandas as pd
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.set_page_config(page_title="Tarifas SAESA (Automático)", layout="wide")
st.title("📊 Dashboard Tarifas SAESA con Scraping")

# Inputs: mes, año, comuna, tarifa
mes = st.selectbox("Mes", ["enero","febrero","marzo","abril","mayo","junio",
                            "julio","agosto","septiembre","octubre","noviembre","diciembre"])
anio = st.number_input("Año", min_value=2020, max_value=datetime.now().year, value=datetime.now().year)

comunas = ["Osorno","Puerto Montt","Valdivia","Ancud","Castro","Quellón",
           "Frutillar","La Unión","Río Bueno","Chonchi","Dalcahue","Purranque","Llanquihue","Calbuco"]
comuna = st.selectbox("Comuna", comunas)

tarifas = ["BT1","BT2","BT3","BT4","AT","MT"]
tipo_tarifa = st.selectbox("Tarifa", tarifas)

def obtener_enlace_pliego():
    url = "https://www.gruposaesa.cl/saesa/tarifas-vigentes"
    res = requests.get(url, verify=False)
    if res.status_code != 200:
        return None
    soup = BeautifulSoup(res.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        txt = (a.text or "").lower()
        if ".pdf" in href.lower() and "regulado" in txt:
            return href
    return None

def descargar_pdf(url):
    res = requests.get(url, verify=False)
    ctype = res.headers.get("Content-Type", "")
    if res.status_code == 200 and "pdf" in ctype.lower():
        fname = "pliego.pdf"
        with open(fname, "wb") as f:
            f.write(res.content)
        return fname
    return None

def extraer_cargos(pdf_path):
    data = []
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for p in reader.pages:
            txt = p.extract_text() or ""
            if comuna.lower() in txt.lower() and tipo_tarifa.upper() in txt.upper():
                for line in txt.split("\n"):
                    if any(x in line for x in ["Cargo", "$", "%", "kWh"]):
                        data.append({"Detalle": line.strip()})
    return data

if st.button("Ejecutar Scraping y Descargar PDF"):
    st.info("🔍 Buscando enlace del pliego tarifario...")
    link = obtener_enlace_pliego()
    if not link:
        st.error("No se encontró el pliego tarifario regulado en el sitio.")
    else:
        st.write("✅ Enlace detectado:", link)
        fname = descargar_pdf(link)
        if not fname:
            st.error("❌ Falló la descarga o el archivo no es un PDF válido.")
        else:
            st.success("📥 PDF descargado correctamente")
            cargos = extraer_cargos(fname)
            os.remove(fname)
            if cargos:
                st.table(pd.DataFrame(cargos))
            else:
                st.warning("⚠️ No se encontraron cargos para los criterios seleccionados.")
