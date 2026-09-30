from datetime import date

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from finance_control.db import get_setting, set_setting
from finance_control.services import income_commitment, monthly_summary, projection, transactions_for_month
from finance_control.ui import brl, compact_brl, page_header, palette

colors = palette()
page_header("Visão executiva", "Controle Financeiro", "Acompanhamento mensal de receitas, despesas e caixa.")

today = date.today()
month_names = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


def shift_month(base: date, offset: int) -> date:
    total = base.year * 12 + base.month - 1 + offset
    year, month_index = divmod(total, 12)
    return date(year, month_index + 1, 1)


current_month = today.replace(day=1)
available_months = [shift_month(current_month, offset) for offset in range(-24, 61)]
with st.sidebar:
    st.header("Período")
    selected_date = st.selectbox(
        "Mês de referência",
        available_months,
        index=24,
        format_func=lambda value: f"{month_names[value.month - 1]}/{value.year}",
    )
    month = selected_date.strftime("%Y-%m")
    st.divider()
    monthly_income = st.number_input("Renda mensal de referência", min_value=0.0,
        value=float(get_setting("monthly_income", "0") or 0), step=100.0)
    if st.button("Salvar renda", use_container_width=True):
        set_setting("monthly_income", str(monthly_income))
        st.success("Renda atualizada.")
    with st.expander("Atualizar caixa e investimentos"):
        cash_balance = st.number_input("Caixa disponível", min_value=0.0,
            value=float(get_setting("cash_balance", "0") or 0), step=100.0)
        investment_balance = st.number_input("Investimentos", min_value=0.0,
            value=float(get_setting("investment_balance", "0") or 0), step=100.0)
        if st.button("Salvar saldos", use_container_width=True):
            set_setting("cash_balance", str(cash_balance))
            set_setting("investment_balance", str(investment_balance))
            st.success("Saldos atualizados.")

df = transactions_for_month(month)
summary = monthly_summary(df)
commitment = income_commitment(summary["expense"], monthly_income, summary["income"])
c1, c2, c3, c4 = st.columns(4)
c1.metric("Receitas", brl(summary["income"])); c2.metric("Despesas", brl(summary["expense"]))
c3.metric("Saldo projetado", brl(summary["balance"])); c4.metric("Renda comprometida", f"{commitment:.1f}%")

cash_balance = float(get_setting("cash_balance", "0") or 0)
investment_balance = float(get_setting("investment_balance", "0") or 0)
st.caption("POSIÇÃO FINANCEIRA ATUAL")
p1, p2, p3 = st.columns(3)
p1.metric("Caixa disponível", brl(cash_balance))
p2.metric("Investimentos", brl(investment_balance))
p3.metric("Total disponível", brl(cash_balance + investment_balance))

st.subheader("Projeção de caixa")
projection_left, projection_right = st.columns([3, 1])
with projection_right:
    months = st.slider("Horizonte da projeção", 3, 24, 6)
    st.caption("Considera os lançamentos previstos cadastrados em cada mês.")
projection_df = projection(month, months)
with projection_left:
    fig = go.Figure()
    fig.add_bar(x=projection_df["month"], y=projection_df["Receitas"], name="Receitas",
        marker_color=colors["gray"], text=[compact_brl(v) for v in projection_df["Receitas"]], textposition="outside")
    fig.add_bar(x=projection_df["month"], y=projection_df["Despesas"], name="Despesas",
        marker_color=colors["blue"], text=[compact_brl(v) for v in projection_df["Despesas"]], textposition="outside")
    fig.add_scatter(x=projection_df["month"], y=projection_df["Saldo acumulado"], name="Saldo acumulado",
        mode="lines+markers+text", text=[compact_brl(v) for v in projection_df["Saldo acumulado"]],
        textposition="top center", line=dict(color=colors["blue_dark"], width=3), yaxis="y2")
    fig.update_layout(barmode="group", hovermode="x unified", height=390,
        paper_bgcolor=colors["background"], plot_bgcolor=colors["background"],
        font=dict(family="Arial Narrow, Arial", color=colors["text"]),
        yaxis=dict(gridcolor=colors["grid"], zeroline=False),
        yaxis2=dict(overlaying="y", side="right", showgrid=False),
        uniformtext_minsize=9, uniformtext_mode="hide",
        legend=dict(orientation="h", y=1.18), margin=dict(l=0, r=0, t=70, b=0))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Composição da receita")
income = df[df["kind"] == "Receita"].copy() if not df.empty else df
if income.empty:
    st.info("Nenhuma receita cadastrada neste mês.")
else:
    income["income_type"] = income["income_type"].fillna("Outros").replace("Não se aplica", "Outros")
    by_income = income.groupby("income_type", as_index=False)["amount"].sum().sort_values("amount")
    by_income["label"] = by_income["amount"].map(brl)
    income_fig = px.bar(by_income, x="amount", y="income_type", orientation="h", text="label",
        labels={"amount": "Receitas", "income_type": ""})
    income_fig.update_traces(marker_color=colors["gray"], textposition="outside", cliponaxis=False,
        textfont=dict(family="Arial Narrow, Arial", size=14, color=colors["text"]))
    income_fig.update_layout(margin=dict(l=0, r=90, t=16, b=0), height=max(260, len(by_income) * 48),
        plot_bgcolor=colors["background"], paper_bgcolor=colors["background"],
        font=dict(family="Arial Narrow, Arial", color=colors["text"]),
        xaxis=dict(showgrid=True, gridcolor=colors["grid"], zeroline=False, tickprefix="R$ "), yaxis=dict(showgrid=False))
    st.plotly_chart(income_fig, use_container_width=True)

st.subheader("Visão do mês")
expenses = df[df["kind"] == "Despesa"] if not df.empty else df
if expenses.empty:
    st.info("Adicione seus primeiros registros na página **Adicione seus Dados**.")
else:
    by_category = expenses.groupby("category", as_index=False)["amount"].sum().sort_values("amount")
    by_category["label"] = by_category["amount"].map(brl)
    fig = px.bar(by_category, x="amount", y="category", orientation="h", text="label",
                 labels={"amount": "Despesas", "category": ""})
    fig.update_traces(marker_color=colors["blue"], textposition="outside",
        textfont=dict(family="Arial Narrow, Arial", size=14, color=colors["text"]),
        hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>", cliponaxis=False)
    fig.update_layout(margin=dict(l=0, r=90, t=16, b=0), height=max(360, len(by_category) * 48),
        plot_bgcolor=colors["background"], paper_bgcolor=colors["background"],
        font=dict(family="Arial Narrow, Arial", color=colors["text"]),
        xaxis=dict(showgrid=True, gridcolor=colors["grid"], zeroline=False, tickprefix="R$ "), yaxis=dict(showgrid=False))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Últimos lançamentos")
if df.empty:
    st.caption("Nenhum lançamento neste mês.")
else:
    display = df[["occurred_on", "description", "category", "account", "status", "amount"]].head(8).copy()
    display.columns = ["Data", "Descrição", "Categoria", "Conta", "Status", "Valor"]
    st.dataframe(display, use_container_width=True, hide_index=True,
        column_config={"Valor": st.column_config.NumberColumn(format="R$ %.2f")})
