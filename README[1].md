# SAESA Tarifario Dashboard

Este proyecto en Streamlit permite descargar automáticamente el pliego tarifario mensual desde la página de SAESA y extraer cargos específicos por comuna y tipo de tarifa.

## Cómo usar

1. Clona este repositorio:
```bash
git clone https://github.com/tuusuario/saesa-tarifario-dashboard.git
cd saesa-tarifario-dashboard
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
streamlit run app.py
```

## Entradas del usuario
- Mes (ej: enero, febrero, etc.)
- Año (ej: 2024)
- Comuna (ej: Osorno)
- Tipo de tarifa (ej: BT1, BT2)

## Salida
- Tabla con los cargos encontrados que coincidan con la búsqueda realizada.
