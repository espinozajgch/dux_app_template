import streamlit as st
import pandas as pd
import json
import datetime

from src.schema import MAP_POSICIONES
from src.db_connection import get_connection

def get_records_db(as_df: bool = True):
    """
    Carga todos los registros de la tabla 'wellness' desde la base de datos MySQL,
    uniendo los nombres descriptivos de los catálogos de estímulos.

    - as_df=True  → devuelve un DataFrame (por defecto)
    - as_df=False → devuelve lista de diccionarios

    Joins:
    - wellness.id_tipo_estimulo → estimulos_campo.id
    - wellness.id_tipo_readaptacion → estimulos_readaptacion.id

    Añade columnas procesadas:
    - partes_cuerpo_dolor (list Python)
    - fecha_sesion (datetime)
    """

    conn = get_connection()
    if not conn:
        st.error(":material/warning: No se pudo establecer conexión con la base de datos.")
        return pd.DataFrame() if as_df else []

    try:
        query = """
            SELECT 
                w.id,
                w.id_jugadora,
                f.nombre,
                f.apellido,
                f.competicion AS plantel,
                i.posicion,
                w.fecha_sesion,
                w.tipo,
                w.turno,
                w.recuperacion,
                w.fatiga as energia,
                w.sueno,
                w.stress,
                w.dolor,
                w.partes_cuerpo_dolor,
                w.periodizacion_tactica,
                ec.nombre AS tipo_estimulo,
                er.nombre AS tipo_readaptacion,
                w.minutos_sesion,
                w.rpe,
                w.ua,
                w.en_periodo,
                w.observacion,
                w.fecha_hora_registro,
                w.usuario
            FROM wellness AS w
            LEFT JOIN futbolistas f ON w.id_jugadora = f.id
            LEFT JOIN informacion_futbolistas i ON f.id = i.id_futbolista
            LEFT JOIN estimulos_campo AS ec 
                ON w.id_tipo_estimulo = ec.id
            LEFT JOIN estimulos_readaptacion AS er 
                ON w.id_tipo_readaptacion = er.id
            ORDER BY w.fecha_hora_registro DESC;
        """

        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()

        if not rows:
            return pd.DataFrame() if as_df else []

        # --- Crear DataFrame ---
        df = pd.DataFrame(rows)

        # --- Procesar JSON (partes_cuerpo_dolor) ---
        if "partes_cuerpo_dolor" in df.columns:
            df["partes_cuerpo_dolor"] = df["partes_cuerpo_dolor"].apply(
                lambda x: json.loads(x) if isinstance(x, str) and x.strip().startswith("[") else []
            )

        # --- Procesar fechas ---
        if "fecha_sesion" in df.columns:
            df["fecha_sesion"] = (
                pd.to_datetime(df["fecha_sesion"], errors="coerce")
                .apply(lambda x: x.date() if pd.notnull(x) else None)
            )

        if "fecha_hora_registro" in df.columns:
            df["fecha_hora_registro"] = pd.to_datetime(df["fecha_hora_registro"], errors="coerce")

        # --- Ordenar de forma más reciente a más antigua ---
        df = df.sort_values(by="fecha_hora_registro", ascending=False)

        if st.session_state["auth"]["rol"].lower() == "developer":
            df = df[df["usuario"]=="developer"]
        else:
            df = df[df["usuario"]!="developer"]

        # print(df["fecha_sesion"].head())
        # print(df["fecha_sesion"].dtype)
        # print(type(df["fecha_sesion"].iloc[0]))

        # --- Retornar según formato deseado ---
        return df if as_df else df.to_dict(orient="records")

    except Exception as e:
        st.error(f":material/warning: Error al cargar los registros de wellness: {e}")
        return pd.DataFrame() if as_df else []
    finally:
        conn.close()
         
def get_records_plus_players_db(plantel: str = None) -> pd.DataFrame:
    """
    Devuelve todas las lesiones junto con los datos de las jugadoras.
    Si no hay registros, devuelve un DataFrame vacío.

    Combina:
    - lesiones
    - futbolistas (nombre, apellido, competicion)
    - informacion_futbolistas (posicion, altura, peso)
    """

    conn = get_connection()
    if not conn:
        st.error(":material/warning: No se pudo conectar a la base de datos.")
        return pd.DataFrame()

    try:
        query = """
        SELECT 
            l.id AS id_registro,
            l.id_lesion,
            l.id_jugadora,
            f.nombre,
            f.apellido,
            f.competicion AS plantel,
            i.posicion,
            l.fecha_lesion,
            l.estado_lesion,
            l.diagnostico,
            l.dias_baja_estimado,
            l.impacto_dias_baja_estimado,
            l.mecanismo_id,
            m.nombre AS mecanismo,
            t.nombre AS tipo_lesion,
            te.nombre AS tipo_especifico,
            l.lugar_id,
            lu.nombre AS lugar,
            l.segmento_id,
            s.nombre AS segmento,
            l.zona_cuerpo_id,
            z.nombre AS zona_cuerpo,
            l.zona_especifica_id,
            za.nombre AS zona_especifica,
            l.lateralidad,
            l.es_recidiva,
            l.tipo_recidiva,
            l.tipo_tratamiento,
            l.personal_reporta,
            l.fecha_alta_diagnostico,
            l.fecha_alta_medica,
            l.fecha_alta_deportiva,
            l.descripcion,
            l.evolucion,
            l.fecha_hora_registro,
            l.usuario
        FROM lesiones l
        LEFT JOIN futbolistas f ON l.id_jugadora = f.id
        LEFT JOIN informacion_futbolistas i ON l.id_jugadora = i.id_futbolista
        LEFT JOIN lugares lu ON l.lugar_id = lu.id
        LEFT JOIN mecanismos m ON l.mecanismo_id = m.id
        LEFT JOIN tipo_lesion t ON l.tipo_lesion_id = t.id
        LEFT JOIN tipo_especifico_lesion te ON l.tipo_especifico_id = te.id
        LEFT JOIN segmentos_corporales s ON l.segmento_id = s.id
        LEFT JOIN zonas_segmento z ON l.zona_cuerpo_id = z.id
        LEFT JOIN zonas_anatomicas za ON l.zona_especifica_id = za.id
        ORDER BY l.fecha_hora_registro DESC;
        """

        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        cursor.close()

        if not rows:
            st.info(":material/info: No existen registros de lesiones en la base de datos.")
            st.stop()

        # Crear columna nombre_jugadora
        df["nombre_jugadora"] = (
            df["nombre"].fillna("") + " " + df["apellido"].fillna("")
        ).str.strip()

        # Reordenar columnas
        columnas = df.columns.tolist()
        if "id_jugadora" in columnas and "nombre_jugadora" in columnas:
            idx = columnas.index("id_jugadora") + 1
            columnas.insert(idx, columnas.pop(columnas.index("nombre_jugadora")))
        if "posicion" in columnas and "plantel" in columnas:
            idx = columnas.index("posicion") + 1
            columnas.insert(idx, columnas.pop(columnas.index("plantel")))

        df = df[columnas]
        df["posicion"] = df["posicion"].map(MAP_POSICIONES).fillna(df["posicion"])
        #df["sesiones"] = df["evolucion"].apply(contar_sesiones)
        
        # Filtrar por plantel si se indica
        if plantel:
            df = df[df["plantel"] == plantel]

        if st.session_state["auth"]["rol"].lower() == "developer":
            df = df[df["usuario"]=="developer"]
        else:
            df = df[df["usuario"]!="developer"]
        
        return df

    except Exception as e:
        st.error(f":material/warning: Error al cargar registros y jugadoras: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

@st.cache_data(ttl=3600)  # cachea por 1 hora (ajústalo según tu frecuencia de actualización)
def load_jugadoras_db() -> pd.DataFrame | None:
    """
    Carga jugadoras desde la base de datos (futbolistas + informacion_futbolistas).
    
    Devuelve:
        tuple: (DataFrame o None, mensaje de error o None)
    """
    conn = get_connection()
    if not conn:
        return None, ":material/warning: No se pudo conectar a la base de datos."

    try:
        query = """
        SELECT 
            f.id AS id_jugadora,
            f.nombre,
            f.apellido,
            f.competicion AS plantel,
            f.fecha_nacimiento,
            f.sexo,
            i.posicion,
            i.dorsal,
            i.nacionalidad,
            i.altura,
            i.peso,
            i.foto_url
        FROM futbolistas f
        LEFT JOIN informacion_futbolistas i 
            ON f.id = i.id_futbolista
        ORDER BY f.nombre ASC;
        """

        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        cursor.close()

        # Limpiar y preparar los datos
        df["nombre"] = df["nombre"].astype(str).str.strip().str.title()
        df["apellido"] = df["apellido"].astype(str).str.strip().str.title()

        # Crear columna nombre completo
        df["nombre_jugadora"] = (df["nombre"] + " " + df["apellido"]).str.strip()

        # Reordenar columnas
        orden = [
            "id_jugadora", "nombre_jugadora", "nombre", "apellido", "posicion", "plantel",
            "dorsal", "nacionalidad", "altura", "peso", "fecha_nacimiento",
            "sexo", "foto_url"
        ]
        df = df[[col for col in orden if col in df.columns]]
        df["posicion"] = df["posicion"].map(MAP_POSICIONES).fillna(df["posicion"])

        #st.dataframe(df)

        return df

    except Exception as e:
            st.error(f":material/warning: Error al cargar jugadoras: {e}")
            st.stop()
    finally:
        conn.close()

@st.cache_data(ttl=3600)  # cachea por 1 hora
def load_competiciones_db() -> tuple[pd.DataFrame | None, str | None]:
    """
    Carga competiciones desde la base de datos (tabla 'plantel').

    Devuelve:
        tuple: (DataFrame o None, mensaje de error o None)
    """
    conn = get_connection()
    if not conn:
        return None, ":material/warning: No se pudo conectar a la base de datos."

    try:
        query = """
        SELECT 
            id,
            nombre,
            codigo
        FROM plantel
        ORDER BY nombre ASC;
        """

        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        cursor.close()

        if df.empty:
            st.error(":material/warning: No se encontraron registros en la tabla 'plantel'.")
            st.stop()

        # Limpieza básica
        df["nombre"] = df["nombre"].astype(str).str.strip().str.title()
        df["codigo"] = df["codigo"].astype(str).str.strip().str.upper()

        # Reordenar columnas (por consistencia)
        orden = ["id", "nombre", "codigo"]
        df = df[[col for col in orden if col in df.columns]]

        return df

    except Exception as e:
        st.error(f":material/warning: Error al cargar competiciones: {e}")
        st.stop()
    finally:
        conn.close()

def delete_wellness(ids: list[int]) -> tuple[bool, str]:
    """
    Elimina múltiples wellness desde la base de datos.

    Parámetros:
        ids (list[int]): lista de IDs de wellness a eliminar.

    Retorna:
        (bool, str): (éxito, mensaje)
    """
    if not ids:
        return False, "No se proporcionaron IDs de wellness."

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Construir la query dinámica con placeholders
        query = f"DELETE FROM wellness WHERE id IN ({','.join(['%s'] * len(ids))})"
        cursor.execute(query, tuple(ids))
        conn.commit()

        cursor.close()
        conn.close()

        return True, f"✅ Se eliminaron {cursor.rowcount} registro(s) correctamente."

    except Exception as e:
        st.error(f":material/warning: Error al eliminar los registros: {e}")
        return False, f":material/warning: Error al eliminar los registros: {e}"
