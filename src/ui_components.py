import pandas as pd
import streamlit as st
from src.schema import MAP_POSICIONES

def selection_header(
    jug_df: pd.DataFrame,
    comp_df: pd.DataFrame,
    records_df: pd.DataFrame = None,
    modo: str = "registro") -> tuple[pd.DataFrame, dict | None]:
    """
    Muestra los filtros principales (Competición, Posición, Jugadora)
    y retorna el DataFrame de registros filtrado según las selecciones.
    """

    if records_df is None:
        records_df = pd.DataFrame()

    # --- Ajuste: solo tres columnas (posición ahora es la segunda) ---
    col1, col2, col3 = st.columns([3, 2, 3])

    # --- Selección de competición / plantel ---
    with col1:
        competiciones_options = comp_df.to_dict("records")
        competicion = st.selectbox(
            "Plantel",
            options=competiciones_options,
            format_func=lambda x: f'{x["nombre"]} ({x["codigo"]})',
            index=3,
            placeholder="Seleccione una competición",
        )

    # --- Selección de posición ---
    with col2:
        posicion = st.selectbox(
            "Posición",
            options=list(MAP_POSICIONES.values()) if "MAP_POSICIONES" in globals() else [],
            placeholder="Seleccione una posición",
            index=None,
        )

    # --- Selección de jugadora ---
    jugadora_opt = None
    with col3:
        disabled_jugadoras = True if modo == "reporte_grupal" else False
        if not jug_df.empty and competicion:
            codigo_comp = competicion["codigo"]
            jug_df_filtrado = jug_df[jug_df["plantel"] == codigo_comp]

            if posicion:
                jug_df_filtrado = jug_df_filtrado[jug_df_filtrado["posicion"] == posicion]

            if not jug_df_filtrado.empty:
                jugadoras_options = jug_df_filtrado.to_dict("records")
                jugadora_opt = st.selectbox(
                    "Jugadora",
                    options=jugadoras_options,
                    format_func=lambda x: f'{x["nombre"]} {x.get("apellido", "")}'.strip(),
                    index=None,
                    placeholder="Seleccione una Jugadora",
                    disabled=disabled_jugadoras,
                )
            else:
                st.info(":material/info: No hay jugadoras para este plantel.")
        else:
            st.warning(":material/warning: No hay jugadoras cargadas o no se ha seleccionado un plantel.")

    # ==================================================
    # 🧮 FILTRADO DEL DATAFRAME
    # ==================================================
    df_filtrado = records_df.copy()

    if not df_filtrado.empty:
        # --- Filtrar por competición (plantel) ---
        if competicion and "codigo" in competicion:
            df_filtrado = df_filtrado[df_filtrado["plantel"] == competicion["codigo"]]

        # --- Filtrar por posición ---
        if posicion and "posicion" in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado["posicion"] == posicion]

        # --- Filtrar por jugadora seleccionada ---
        if jugadora_opt and "id_jugadora" in jugadora_opt:
            df_filtrado = df_filtrado[df_filtrado["id_jugadora"] == jugadora_opt["id_jugadora"]]

    return df_filtrado, jugadora_opt

def preview_record(record: dict) -> None:
    #st.subheader("Previsualización")
    # Header with key fields
    jug = record.get("id_jugadora", "-")
    fecha = record.get("fecha_sesion", "-")
    turno = record.get("turno", "-")
    tipo = record.get("tipo", "-")
    st.markdown(f"**Jugadora:** {jug}  |  **Fecha:** {fecha}  |  **Turno:** {turno}  |  **Tipo:** {tipo}")
    with st.expander("Ver registro JSON", expanded=True):
        import json

        st.code(json.dumps(record, ensure_ascii=False, indent=2), language="json")
