from __future__ import annotations

from datetime import date

import plotly.express as px
import streamlit as st

from finance_control.auth import require_auth
from finance_control.db import get_setting, set_setting
from finance_control.services import CATEGORIES, monthly_summary, transactions_for_month

st.set_page_config(page_title="Finance Control", page_icon="💰", layout="wide")
require_auth()


def brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.title("Finance Control")
st.caption("Seu mês financeiro, sem surpresas.")

today = date.today()
default_month = today.strftime("%Y-%m")
with st.sidebar:
    st.header("Período")
    selected_date = st.date_input("Mês de referência", today.replace(day=1))
    month = selected_date.strftime("%Y-%m")
    st.divider()
    monthly_income = st.number_input(
        "Renda mensal de referência",
        min_value=0.0,
        value=float(get_setting("monthly_income", "0") or 0),
        step=100.0,
    )
    if st.button("Salvar renda", use_container_width=True):
        set_setting("monthly_income", str(monthly_income))
        st.success("Renda atualizada.")

df = transactions_for_month(month)
summary = monthly_summary(df)
reference_income = summary["income"] or monthly_income
commitment = (summary["expense"] / reference_income * 100) if reference_income else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Receitas", brl(summary["income"]))
c2.metric("Despesas", brl(summary["expense"]))
c3.metric("Saldo projetado", brl(summary["balance"]))
c4.metric("Renda comprometida", f"{commitment:.1f}%")

st.subheader("Visão do mês")
left, right = st.columns([1.15, 1])
with left:
    expenses = df[df["kind"] == "Despesa"] if not df.empty else df
    if expenses.empty:
        st.info("Cadastre seus primeiros lançamentos na página **Lançamentos**.")
    else:
        by_category = expenses.groupby("category", as_index=False)["amount"].sum()
        fig = px.bar(by_category.sort_values("amount"), x="amount", y="category",
                     orientation="h", labels={"amount": "Valor", "category": "Categoria"},
                     color="amount", color_continuous_scale=["#38bdf8", "#2563eb"])
        fig.update_layout(coloraxis_showscale=False, margin=dict(l=0, r=10, t=10, b=0), height=360)
        st.plotly_chart(fig, use_container_width=True)

with right:
    if expenses.empty:
        st.info("A distribuição por categoria aparecerá aqui.")
    else:
        by_category = expenses.groupby("category", as_index=False)["amount"].sum()
        fig = px.pie(by_category, values="amount", names="category", hole=.62,
                     color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=360, legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Últimos lançamentos")
if df.empty:
    st.caption("Nenhum lançamento neste mês.")
else:
    display = df[["occurred_on", "description", "category", "account", "status", "amount"]].head(8).copy()
    display.columns = ["Data", "Descrição", "Categoria", "Conta", "Status", "Valor"]
    st.dataframe(display, use_container_width=True, hide_index=True,
                 column_config={"Valor": st.column_config.NumberColumn(format="R$ %.2f")})
