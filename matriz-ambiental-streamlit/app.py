"""Matriz de obligaciones y cumplimiento ambiental (Streamlit)."""
import io
from datetime import date, timedelta

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Matriz de obligaciones y cumplimiento ambiental",
    page_icon="🌿",
    layout="wide",
)

COLUMNAS = [
    "Obligación", "Norma o fuente", "Tipo", "Autoridad", "Frecuencia",
    "Responsable", "Fecha límite", "Estado", "Evidencia / observación",
]
TEXTO = ["Obligación", "Norma o fuente", "Autoridad", "Responsable", "Evidencia / observación"]
ESTADOS = ["Cumple", "Parcial", "No cumple", "No aplica"]
TIPOS = ["Legal", "Compromiso del instrumento ambiental", "Voluntaria (ISO 14001)", "Otra"]
FRECUENCIAS = ["Permanente", "Mensual", "Trimestral", "Semestral", "Anual", "Única vez"]
COLORES = {
    "Cumple": "#1f7a4d",
    "Parcial": "#d9a21b",
    "No cumple": "#a8321f",
    "No aplica": "#9aa6a1",
}


def ejemplo() -> pd.DataFrame:
    hoy = date.today()
    d = lambda n: hoy + timedelta(days=n)  # noqa: E731
    filas = [
        ["Contar con instrumento de gestión ambiental aprobado",
         "Ley 27446 (SEIA) y D.S. 019-2009-MINAM", "Legal",
         "Autoridad sectorial / SENACE", "Única vez", "Gerencia", d(60),
         "Cumple", "Resolución de aprobación"],
        ["Segregar y almacenar residuos sólidos según su peligrosidad",
         "D.Leg. 1278 y D.S. 014-2017-MINAM", "Legal", "OEFA / MINAM",
         "Permanente", "Jefe de SSOMA", d(30), "Parcial",
         "Falta señalizar el almacén central"],
        ["Presentar la declaración anual de residuos sólidos no municipales",
         "D.S. 014-2017-MINAM (SIGERSOL)", "Legal", "MINAM", "Anual",
         "Jefe de SSOMA", d(-20), "No cumple", "Declaración pendiente"],
        ["Monitoreo de calidad de aire", "D.S. 003-2017-MINAM (ECA aire)",
         "Compromiso del instrumento ambiental", "OEFA", "Trimestral",
         "Laboratorio acreditado", d(25), "Cumple", "Informe de ensayo del trimestre"],
        ["Monitoreo de ruido ambiental en el límite de propiedad",
         "D.S. 085-2003-PCM", "Legal", "Municipalidad / OEFA", "Semestral",
         "Laboratorio acreditado", d(45), "Parcial", "Un punto sin medir"],
        ["Evaluar el cumplimiento de obligaciones (ISO 14001, 9.1.2)",
         "ISO 14001:2015", "Voluntaria (ISO 14001)", "Auditor interno", "Anual",
         "Coordinador del SGA", d(90), "No cumple", "Sin programa de evaluación"],
        ["Control de vertimientos y cumplimiento del ECA agua",
         "D.S. 004-2017-MINAM", "Legal", "ANA / OEFA", "Mensual",
         "Operaciones", d(10), "No aplica", "No genera vertimientos"],
    ]
    return normalizar(pd.DataFrame(filas, columns=COLUMNAS))


def normalizar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in COLUMNAS:
        if c not in df.columns:
            df[c] = None
    df = df[COLUMNAS]
    df["Fecha límite"] = pd.to_datetime(df["Fecha límite"], errors="coerce")
    df["Estado"] = df["Estado"].where(df["Estado"].isin(ESTADOS), "No cumple")
    df["Tipo"] = df["Tipo"].where(df["Tipo"].isin(TIPOS), "Otra")
    df["Frecuencia"] = df["Frecuencia"].where(df["Frecuencia"].isin(FRECUENCIAS), "Anual")
    for c in TEXTO:
        df[c] = df[c].fillna("").astype(str)
    return df.reset_index(drop=True)


def calcular(df: pd.DataFrame) -> dict:
    hoy = pd.Timestamp(date.today())
    conteo = df["Estado"].value_counts().reindex(ESTADOS, fill_value=0)
    aplicables = len(df) - conteo["No aplica"]
    pct = conteo["Cumple"] / aplicables * 100 if aplicables else 0.0
    pond = (conteo["Cumple"] + 0.5 * conteo["Parcial"]) / aplicables * 100 if aplicables else 0.0
    vencida = df["Fecha límite"].notna() & (df["Fecha límite"] < hoy) & df["Estado"].isin(["Parcial", "No cumple"])
    return {"conteo": conteo, "aplicables": int(aplicables), "pct": pct, "pond": pond, "vencida": vencida}


def a_excel(df: pd.DataFrame, k: dict) -> bytes:
    buf = io.BytesIO()
    resumen = pd.DataFrame({
        "Indicador": ["Obligaciones registradas", "Obligaciones aplicables", "Cumple", "Parcial",
                      "No cumple", "No aplica", "Cumplimiento (%)", "Cumplimiento ponderado (%)",
                      "Vencidas sin cumplir"],
        "Valor": [len(df), k["aplicables"], *[int(k["conteo"][e]) for e in ESTADOS],
                  round(k["pct"], 1), round(k["pond"], 1), int(k["vencida"].sum())],
    })
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name="Matriz", index=False)
        resumen.to_excel(w, sheet_name="Resumen", index=False)
        for i, ancho in enumerate([50, 36, 30, 24, 14, 24, 14, 12, 36]):
            w.sheets["Matriz"].column_dimensions[chr(65 + i)].width = ancho
        w.sheets["Resumen"].column_dimensions["A"].width = 30
    return buf.getvalue()


def leer_archivo(archivo) -> pd.DataFrame:
    if archivo.name.lower().endswith(".csv"):
        return pd.read_csv(archivo, encoding="utf-8-sig")
    return pd.read_excel(archivo)


# ---------- Estado de sesión ----------
if "base" not in st.session_state:
    st.session_state.base = ejemplo()
    st.session_state.version = 0


def reemplazar(df: pd.DataFrame) -> None:
    st.session_state.base = normalizar(df)
    st.session_state.version += 1


# ---------- Encabezado ----------
st.title("🌿 Matriz de obligaciones y cumplimiento ambiental")
st.caption(
    "Registra cada obligación legal o voluntaria, su responsable, su plazo y su evidencia. "
    "El cumplimiento se calcula solo sobre las obligaciones aplicables."
)

tab_matriz, tab_ind, tab_info = st.tabs(["Matriz", "Indicadores", "Acerca de"])

with tab_matriz:
    st.write("Edita las celdas directamente. Usa la fila vacía del final para agregar una obligación.")
    editado = st.data_editor(
        st.session_state.base,
        key=f"editor_{st.session_state.version}",
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Obligación": st.column_config.TextColumn(width="large", required=True),
            "Norma o fuente": st.column_config.TextColumn(width="medium"),
            "Tipo": st.column_config.SelectboxColumn(options=TIPOS, width="medium"),
            "Autoridad": st.column_config.TextColumn(width="medium"),
            "Frecuencia": st.column_config.SelectboxColumn(options=FRECUENCIAS),
            "Responsable": st.column_config.TextColumn(width="medium"),
            "Fecha límite": st.column_config.DateColumn(format="DD/MM/YYYY"),
            "Estado": st.column_config.SelectboxColumn(options=ESTADOS, required=True),
            "Evidencia / observación": st.column_config.TextColumn(width="large"),
        },
    )

datos = normalizar(editado)
datos = datos[datos["Obligación"].str.strip() != ""].reset_index(drop=True)
k = calcular(datos)

with tab_ind:
    if datos.empty:
        st.info("Aún no hay obligaciones. Agrégalas en la pestaña Matriz.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Cumplimiento", f"{k['pct']:.0f}%", help="Cumple ÷ obligaciones aplicables")
        c2.metric("Cumplimiento ponderado", f"{k['pond']:.0f}%", help="Parcial cuenta como 0,5")
        c3.metric("Aplicables", f"{k['aplicables']} de {len(datos)}")
        c4.metric("Vencidas sin cumplir", int(k["vencida"].sum()))

        izq, der = st.columns(2)
        with izq:
            st.subheader("Obligaciones por estado")
            graf = k["conteo"].rename_axis("Estado").reset_index(name="Cantidad")
            st.altair_chart(
                alt.Chart(graf).mark_bar().encode(
                    x=alt.X("Estado:N", sort=ESTADOS, axis=alt.Axis(labelAngle=0), title=None),
                    y=alt.Y("Cantidad:Q", title=None, axis=alt.Axis(tickMinStep=1)),
                    color=alt.Color(
                        "Estado:N",
                        scale=alt.Scale(domain=list(COLORES), range=list(COLORES.values())),
                        legend=None,
                    ),
                    tooltip=["Estado", "Cantidad"],
                ),
                use_container_width=True,
            )
        with der:
            st.subheader("Estado por tipo de obligación")
            cruce = pd.crosstab(datos["Tipo"], datos["Estado"]).reindex(columns=ESTADOS, fill_value=0)
            st.dataframe(cruce, use_container_width=True)

        st.subheader("Pendientes priorizados")
        pend = datos[datos["Estado"].isin(["No cumple", "Parcial"])].copy()
        if pend.empty:
            st.success("No hay obligaciones pendientes.")
        else:
            pend["Días para el plazo"] = (pend["Fecha límite"] - pd.Timestamp(date.today())).dt.days
            pend = pend.sort_values("Días para el plazo", na_position="last")
            st.dataframe(
                pend[["Obligación", "Responsable", "Fecha límite", "Días para el plazo", "Estado"]],
                use_container_width=True, hide_index=True,
                column_config={"Fecha límite": st.column_config.DateColumn(format="DD/MM/YYYY")},
            )
            st.caption("Los días negativos indican que el plazo ya venció.")

with tab_info:
    st.markdown(
        """
**Cómo se calcula**

- *Cumplimiento* = obligaciones en estado Cumple ÷ obligaciones aplicables (todas menos No aplica).
- *Cumplimiento ponderado* cuenta cada obligación Parcial como media obligación cumplida.
- Una obligación está *vencida* si su fecha límite pasó y su estado es Parcial o No cumple.

**Guardado de datos**

Esta aplicación no guarda datos en un servidor. Descarga tu matriz en Excel o CSV desde la
barra lateral y vuelve a cargarla cuando la necesites.

**Aviso**

Las normas del ejemplo son referenciales (Perú). Verifica su vigencia y las obligaciones de tu
instrumento de gestión ambiental antes de usar la matriz en un trabajo o una auditoría.
"""
    )

# ---------- Barra lateral ----------
with st.sidebar:
    st.header("Archivo")
    st.download_button(
        "Descargar Excel", data=a_excel(datos, k),
        file_name="matriz_cumplimiento_ambiental.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    st.download_button(
        "Descargar CSV", data=datos.to_csv(index=False).encode("utf-8-sig"),
        file_name="matriz_cumplimiento_ambiental.csv", mime="text/csv",
        use_container_width=True,
    )
    st.divider()
    subido = st.file_uploader("Cargar una matriz (CSV o Excel)", type=["csv", "xlsx"])
    if subido is not None and st.button("Cargar archivo", use_container_width=True):
        try:
            nuevo = leer_archivo(subido)
            if "Obligación" not in nuevo.columns:
                st.error("El archivo debe tener al menos la columna «Obligación».")
            else:
                reemplazar(nuevo)
                st.rerun()
        except Exception as e:  # noqa: BLE001
            st.error(f"No se pudo leer el archivo: {e}")
    st.divider()
    if st.button("Restaurar ejemplo", use_container_width=True):
        reemplazar(ejemplo())
        st.rerun()
    if st.button("Vaciar matriz", use_container_width=True):
        reemplazar(pd.DataFrame(columns=COLUMNAS))
        st.rerun()
