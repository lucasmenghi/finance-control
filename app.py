from __future__ import annotations

from datetime import date

import plotly.express as px
import streamlit as st

from finance_control.auth import require_auth
from finance_control.db import get_setting, set_setting
from finance_control.services import (
    CATEGORIES, income_commitment, monthly_summary, transactions_for_month,
)

st.set_page_config(page_title="Controle Financeiro", page_icon="💰", layout="wide")
require_auth()


def brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap');

    :root {
        --executive-black: #111827;
        --executive-gray: #667085;
        --executive-light: #F2F4F7;
        --executive-blue: #1261A0;
        --executive-blue-dark: #0B3658;
    }
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: "Arial Narrow", Arial, sans-serif;
        color: var(--executive-black);
    }
    h1, h2, h3, [data-testid="stMetricLabel"] {
        font-family: "Montserrat", Arial, sans-serif !important;
        letter-spacing: -0.02em;
    }
    h1 { font-weight: 700 !important; color: var(--executive-black); }
    h2, h3 { font-weight: 600 !important; }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #D0D5DD;
        border-top: 4px solid var(--executive-blue);
        padding: 18px 20px;
        min-height: 126px;
    }
    [data-testid="stMetricLabel"] { color: var(--executive-gray); }
    [data-testid="stMetricValue"] {
        color: var(--executive-black);
        font-family: "Arial Narrow", Arial, sans-serif;
    }
    [data-testid="stSidebar"] { background: var(--executive-light); }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: var(--executive-blue-dark); }
    .executive-kicker {
        color: var(--executive-blue);
        font-family: "Montserrat", Arial, sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
    }
    .executive-subtitle { color: var(--executive-gray); margin-top: -0.5rem; }
    </style>
    <div class="executive-kicker">Visão executiva</div>
    """,
    unsafe_allow_html=True,
)
st.title("Controle Financeiro")
st.markdown('<p class="executive-subtitle">Acompanhamento mensal de receitas, despesas e caixa.</p>', unsafe_allow_html=True)

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
commitment = income_commitment(summary["expense"], monthly_income, summary["income"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Receitas", brl(summary["income"]))
c2.metric("Despesas", brl(summary["expense"]))
c3.metric("Saldo projetado", brl(summary["balance"]))
c4.metric("Renda comprometida", f"{commitment:.1f}%")

st.subheader("Visão do mês")
expenses = df[df["kind"] == "Despesa"] if not df.empty else df
if expenses.empty:
    st.info("Cadastre seus primeiros lançamentos na página **Lançamentos**.")
else:
    by_category = expenses.groupby("category", as_index=False)["amount"].sum()
    by_category = by_category.sort_values("amount")
    by_category["label"] = by_category["amount"].map(brl)
    fig = px.bar(
        by_category,
        x="amount",
        y="category",
        orientation="h",
        text="label",
        labels={"amount": "Despesas", "category": ""},
    )
    fig.update_traces(
        marker_color="#1261A0",
        textposition="outside",
        textfont=dict(family="Arial Narrow, Arial", size=14, color="#111827"),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
        cliponaxis=False,
    )
    fig.update_layout(
        margin=dict(l=0, r=90, t=16, b=0),
        height=max(360, len(by_category) * 48),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Arial Narrow, Arial", color="#344054"),
        xaxis=dict(showgrid=True, gridcolor="#EAECF0", zeroline=False, tickprefix="R$ "),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Últimos lançamentos")
if df.empty:
    st.caption("Nenhum lançamento neste mês.")
else:
    display = df[["occurred_on", "description", "category", "account", "status", "amount"]].head(8).copy()
    display.columns = ["Data", "Descrição", "Categoria", "Conta", "Status", "Valor"]
    st.dataframe(display, use_container_width=True, hide_index=True,
                 column_config={"Valor": st.column_config.NumberColumn(format="R$ %.2f")})
