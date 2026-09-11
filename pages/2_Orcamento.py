from datetime import date

import plotly.express as px
import streamlit as st

from finance_control.db import init_db
from finance_control.services import CATEGORIES, budget_progress, upsert_budget

st.set_page_config(page_title="Orçamento", page_icon="🎯", layout="wide")
init_db()
st.title("Orçamento por categoria")

selected_date = st.date_input("Mês", date.today().replace(day=1))
month = selected_date.strftime("%Y-%m")

with st.form("budget"):
    c1, c2 = st.columns(2)
    category = c1.selectbox("Categoria", CATEGORIES)
    amount = c2.number_input("Limite do mês", min_value=0.0, step=50.0)
    if st.form_submit_button("Salvar limite", type="primary"):
        upsert_budget(month, category, amount)
        st.success("Limite atualizado.")

progress = budget_progress(month)
if progress.empty:
    st.info("Defina pelo menos um limite para acompanhar seu orçamento.")
else:
    fig = px.bar(progress, x="category", y=["budget", "spent"], barmode="group",
                 labels={"value": "Valor", "category": "Categoria", "variable": "Indicador"},
                 color_discrete_map={"budget": "#94a3b8", "spent": "#2563eb"})
    st.plotly_chart(fig, use_container_width=True)
    table = progress[["category", "budget", "spent", "remaining", "usage"]].copy()
    table.columns = ["Categoria", "Limite", "Gasto", "Disponível", "Uso (%)"]
    st.dataframe(table, use_container_width=True, hide_index=True,
                 column_config={
                     "Limite": st.column_config.NumberColumn(format="R$ %.2f"),
                     "Gasto": st.column_config.NumberColumn(format="R$ %.2f"),
                     "Disponível": st.column_config.NumberColumn(format="R$ %.2f"),
                     "Uso (%)": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%"),
                 })

