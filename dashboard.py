from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(
    page_title="Análisis de causas de mortalidad",
    layout="wide"
)

def normalizar_nombre(nombre):
    nombre = nombre.strip().lower()
    nombre = nombre.replace("'", "")
    nombre = nombre.replace("/", "_")
    nombre = re.sub(r"\s+", "_", nombre)
    nombre = re.sub(r"[^a-z0-9_áéíóúüñ]", "_", nombre)
    nombre = re.sub(r"_+", "_", nombre)
    nombre = nombre.strip("_")

    return nombre

@st.cache_data
def cargar_datos():

    ruta = Path(__file__).resolve().parent / "Forma_B.csv"

    df = pd.read_csv(ruta)

    columnas_identificadoras_originales = [
        "country",
        "code",
        "year"
    ]

    columnas_causas_originales = [
        columna
        for columna in df.columns
        if columna not in columnas_identificadoras_originales
    ]

    df[columnas_causas_originales] = (
        df[columnas_causas_originales].fillna(0)
    )

    df["code"] = df["code"].fillna("Desconocido")

    df.columns = [
        normalizar_nombre(columna)
        for columna in df.columns
    ]

    diccionario_renombrado = {
        "country": "pais",
        "code": "codigo",
        "year": "año",
        "meningitis": "meningitis",
        "alzheimers_diesease": "enfermedad_alzheimer",
        "parkinsons_disease": "enfermedad_parkinson",
        "nutritional_deficiency": "deficiencias_nutricionales",
        "malaria": "malaria",
        "drowning": "ahogamientos",
        "interpersonal_violence": "violencia_interpersonal",
        "maternal_disorders": "trastornos_maternos",
        "hiv_aids": "vih_sida",
        "drug_use_disorders": "trastornos_uso_drogas",
        "tuberculosis": "tuberculosis",
        "cardiovascular_diseases": "enfermedades_cardiovasculares",
        "lower_respiratory_infections": "infecciones_respiratorias",
        "neonatal_disorders": "trastornos_neonatales",
        "alcohol_use_disorders": "trastornos_uso_alcohol",
        "self_harm": "autolesiones",
        "exposure_to_forces_of_nature": "exposicion_fuerzas_naturaleza",
        "diarrheal_diseases": "enfermedades_diarreicas",
        "environmental_heat_and_cold_exposure": "exposicion_calor_frio_ambiental",
        "neoplasms": "neoplasias",
        "conflict_and_terrorism": "conflictos_y_terrorismo",
        "diabetes_mellitus": "diabetes_mellitus",
        "chronic_kidney_disease": "enfermedad_renal_cronica",
        "poisonings": "envenenamientos",
        "protein_energy_malnutrition": "desnutricion_proteico_energetica",
        "terrorism": "terrorismo",
        "road_injuries": "lesiones_transito",
        "chronic_respiratory_diseases": "enfermedades_respiratorias_cronicas",
        "chronic_liver_diseases": "enfermedades_hepaticas_cronicas",
        "digestive_diseases": "enfermedades_digestivas",
        "fire_heat_hot_substance": "fuego_calor_sustancias_calientes",
        "acute_hepatitis": "hepatitis_aguda"
    }

    df = df.rename(columns=diccionario_renombrado)
    
    df["año"] = pd.to_numeric(
        df["año"],
        errors="raise"
    ).astype(int)

    columnas_identificadoras = [
        "pais",
        "codigo",
        "año"
    ]

    columnas_causas = [
        columna
        for columna in df.columns
        if columna not in columnas_identificadoras
    ]

    for columna in columnas_causas:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="raise"
        )

    df["total_muertes"] = (
        df[columnas_causas].sum(axis=1)
    )

    return df, columnas_causas

df, columnas_causas = cargar_datos()

st.title("Dashboard de causas de mortalidad")

st.write(
    "Análisis interactivo del dataset Forma_B.csv "
    "para el período 1990–2019."
)

st.sidebar.header("Filtros")

año_minimo = int(df["año"].min())
año_maximo = int(df["año"].max())

rango_años = st.sidebar.slider(
    "Selecciona el rango de años",
    min_value=año_minimo,
    max_value=año_maximo,
    value=(año_minimo, año_maximo),
    step=1
)

paises_disponibles = sorted(
    df["pais"].unique()
)

paises_seleccionados = st.sidebar.multiselect(
    "Selecciona países",
    options=paises_disponibles
)

causa_seleccionada = st.sidebar.selectbox(
    "Selecciona una causa de muerte",
    options=columnas_causas,
    format_func=lambda x: x.replace("_", " ").title()
)

filtro = df["año"].between(
    rango_años[0],
    rango_años[1]
)

if paises_seleccionados:
    filtro = (
        filtro
        & df["pais"].isin(paises_seleccionados)
    )

df_filtrado = df.loc[filtro].copy()

if df_filtrado.empty:
    st.warning(
        "No existen registros para la selección realizada."
    )
    st.stop()

total_periodo = df_filtrado["total_muertes"].sum()

promedio_anual = (
    df_filtrado
    .groupby("año")["total_muertes"]
    .sum()
    .mean()
)

totales_causas_filtrado = (
    df_filtrado[columnas_causas]
    .sum()
    .sort_values(ascending=False)
)

causa_principal = (
    totales_causas_filtrado.index[0]
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Muertes en la selección",
    f"{total_periodo:,.0f}"
)

col2.metric(
    "Promedio anual",
    f"{promedio_anual:,.0f}"
)

col3.metric(
    "Causa principal",
    causa_principal.replace("_", " ").title()
)

st.subheader(
    "Evolución del total de muertes"
)

muertes_anuales = (
    df_filtrado
    .groupby("año")["total_muertes"]
    .sum()
)

fig1, ax1 = plt.subplots(figsize=(10, 5))

ax1.plot(
    muertes_anuales.index,
    muertes_anuales.values,
    marker="o"
)

ax1.set_title(
    "Total de muertes por año"
)

ax1.set_xlabel("Año")
ax1.set_ylabel("Muertes")

ax1.grid(alpha=0.3)

st.pyplot(fig1)

st.subheader(
    "Cinco principales causas de muerte"
)

top5_dashboard = (
    totales_causas_filtrado
    .head(5)
    .sort_values()
)

etiquetas_top5 = [
    causa.replace("_", " ").title()
    for causa in top5_dashboard.index
]


fig2, ax2 = plt.subplots(figsize=(10, 5))

ax2.barh(
    etiquetas_top5,
    top5_dashboard.values
)

ax2.set_title(
    "Cinco causas con mayor mortalidad acumulada"
)

ax2.set_xlabel(
    "Muertes acumuladas"
)

ax2.set_ylabel(
    "Causa de muerte"
)

plt.tight_layout()

st.pyplot(fig2)

st.subheader(
    "Evolución de la causa seleccionada"
)

evolucion_causa = (
    df_filtrado
    .groupby("año")[causa_seleccionada]
    .sum()
)

fig3, ax3 = plt.subplots(figsize=(10, 5))

ax3.plot(
    evolucion_causa.index,
    evolucion_causa.values,
    marker="o"
)

ax3.set_title(
    causa_seleccionada.replace("_", " ").title()
)

ax3.set_xlabel("Año")
ax3.set_ylabel("Muertes")

ax3.grid(alpha=0.3)

st.pyplot(fig3)

st.subheader(
    "Países con mayor mortalidad en la selección"
)

ranking_paises = (
    df_filtrado
    .groupby("pais")["total_muertes"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

st.dataframe(
    ranking_paises,
    width="stretch"
)