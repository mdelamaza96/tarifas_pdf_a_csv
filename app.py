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
st.title("📊 Dashboard Tarifas SAESA con Scraping + Backup URL")

# Inputs
mes = st.selectbox("Mes", ["enero","febrero","marzo","abril","mayo","junio",
                            "julio","agosto","septiembre","octubre","noviembre","diciembre"])
anio = st.number_input("Año", min_value=2020, max_value=datetime.now().year, value=datetime.now().year)

comunas = [
    "Osorno", "Puerto Montt", "Ancud", "Castro", "Quellón", "Chonchi", "Dalcahue", "Puqueldón",
    "Quemchi", "Curaco de Vélez", "Queilén", "Frutillar", "Llanquihue", "Calbuco", "Maullín",
    "Hualaihué", "Fresia", "Los Muermos", "Purranque", "Río Negro", "San Pablo",
    "San Juan de la Costa", "La Unión", "Río Bueno", "Paillaco", "Futrono", "Lago Ranco",
    "Valdivia", "Mariquina", "Corral", "Máfil", "Lanco", "Panguipulli", "Los Lagos",
    "Chaitén", "Palena", "Futaleufú", "Cochamó", "Hornopirén"
]
comuna = st.selectbox("Comuna", comunas)

tarifas = ["BT1","BT2","BT3","BT4","AT","MT"]
tipo_tarifa = st.selectbox("Tarifa", tarifas)

BACKUP_URL = "https://www.saesa.cl/adjuntos/Pliego_tarifario_Suministro_Regulado.pdf"

def obtener_enlace_pliego():
    url = "https://www.gruposaesa.cl/saesa/tarifas-vigentes"
    try:
        res = requests.get(url, verify=False, timeout=10)
        if res.status_code != 200:
            return None
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            txt = (a.text or "").lower()
            if href.lower().endswith(".pdf") and "regulado" in txt:
                return href
    except:
        return None
    return None

def descargar_pdf(url):
    try:
        res = requests.get(url, verify=False)
        ctype = res.headers.get("Content-Type", "")
        if res.status_code == 200 and "pdf" in ctype.lower():
            fname = "pliego.pdf"
            with open(fname, "wb") as f:
                f.write(res.content)
            return fname
    except:
        pass
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

if st.button("Ejecutar búsqueda y descarga"):
    st.info("🔍 Buscando pliego tarifario regulado...")
    link = obtener_enlace_pliego()

    if not link:
        st.warning("⚠️ No se encontró el PDF automáticamente. Usando URL de respaldo.")
        link = BACKUP_URL

    st.write("📎 Enlace utilizado:", link)
    fname = descargar_pdf(link)
    if not fname:
        st.error("❌ No se pudo descargar el archivo PDF.")
    else:
        st.success("✅ PDF descargado correctamente")
        cargos = extraer_cargos(fname)
        os.remove(fname)
        if cargos:
            st.dataframe(pd.DataFrame(cargos))
        else:
            st.warning("⚠️ No se encontraron cargos para los criterios seleccionados.")
