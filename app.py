import streamlit as st
import pandas as pd

from src.auth_system.auth_core import init_app_state, validate_login
from src.auth_system.auth_ui import login_view, menu
from src.ui_app import grafico
from src.db_records import get_records_db
from numpy.random import default_rng as rng
import src.config as config
config.init_config()

# ============================================================
# 🔐 AUTENTICACIÓN
# ============================================================
init_app_state()
validate_login()

if not st.session_state["auth"]["is_logged_in"]:
    login_view()
    st.stop()

st.header("Resumen", divider="red")
menu()

#st.session_state.clear()

# ============================================================
# 📦 CARGA DE DATOS
# ============================================================
df = get_records_db()
if df.empty:
    st.warning("No hay registros disponibles.")
    st.stop()

# ============================================================
# 🧭 INTERFAZ PRINCIPAL
# ============================================================

import streamlit as st

col1, col2, col3 = st.columns(3, border=True)
col1.metric("Temperature", "70 °F", "1.2 °F")
col2.metric("Wind", "9 mph", "-8%")
col3.metric("Humidity", "86%", "4%")

# ============================================================
# 📊 REGISTROS DEL PERIODO
# ============================================================

#st.divider()
st.markdown(f"**Registros**")
tabs = st.tabs([
        ":material/physical_therapy: Indicadores Claves",
        ":material/description: Registros detallados",
        #"Riesgo de lesión"
    ])

with tabs[0]: 
    df = pd.DataFrame(rng(0).standard_normal((50, 20)), columns=("col %d" % i for i in range(20)))
    st.dataframe(df)
with tabs[1]: 
    df = pd.DataFrame(rng(0).standard_normal((10, 20)), columns=("col %d" % i for i in range(20)))
    st.dataframe(df.style.highlight_max(axis=0))

grafico()