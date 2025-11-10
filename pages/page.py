import streamlit as st
import src.config as config

config.init_config()

from src.auth_system.auth_core import init_app_state, validate_login
from src.auth_system.auth_ui import login_view, menu

from src.db_records import load_jugadoras_db, load_competiciones_db

init_app_state()
validate_login()

from src.ui_components import selection_header

# Authentication gate
if not st.session_state["auth"]["is_logged_in"]:
    login_view()
    st.stop()

st.header('Blank Page :red[:material/docs:] ', divider=True)

menu()

# Load reference data
jug_df = load_jugadoras_db()
comp_df = load_competiciones_db()

jugadora, tipo = selection_header(jug_df, comp_df)

if jugadora.empty:
    st.info("Selecciona una jugadora para continuar.")
    st.stop()

st.divider()