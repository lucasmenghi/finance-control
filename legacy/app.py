import streamlit as st

from finance_control.auth import require_auth
from finance_control.ui import apply_theme

st.set_page_config(page_title="Controle Financeiro", page_icon="💰", layout="wide")
require_auth()

with st.sidebar:
    st.divider()
    dark_mode = st.toggle("Tema escuro", value=st.session_state.get("dark_mode", False))
    st.session_state["dark_mode"] = dark_mode

apply_theme(dark_mode)

navigation = st.navigation([
    st.Page("pages/0_Visao_Geral.py", title="Visão Geral", icon="📊", default=True),
    st.Page("pages/1_Adicione_seus_Dados.py", title="Adicione seus Dados", icon="➕"),
])
navigation.run()
