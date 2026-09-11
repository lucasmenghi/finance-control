from datetime import date

import streamlit as st

from finance_control.db import init_db
from finance_control.services import (
    ACCOUNTS, CATEGORIES, add_transaction, delete_transaction, transactions_for_month,
)

st.set_page_config(page_title="Lançamentos", page_icon="🧾", layout="wide")
init_db()
st.title("Lançamentos")

with st.form("new_transaction", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    description = c1.text_input("Descrição", placeholder="Ex.: Supermercado")
    amount = c2.number_input("Valor", min_value=0.0, step=10.0)
    occurred_on = c3.date_input("Data", date.today())
    c4, c5, c6, c7 = st.columns(4)
    kind = c4.selectbox("Tipo", ["Despesa", "Receita"])
    category = c5.selectbox("Categoria", CATEGORIES)
    account = c6.selectbox("Conta", ACCOUNTS)
    status = c7.selectbox("Status", ["Pago", "Previsto", "Atrasado"])
    notes = st.text_input("Observações", placeholder="Opcional")
    submitted = st.form_submit_button("Adicionar lançamento", type="primary")
    if submitted:
        try:
            add_transaction(description, amount, kind, category, account, occurred_on, status, notes)
            st.success("Lançamento adicionado.")
        except ValueError as exc:
            st.error(str(exc))

selected_date = st.date_input("Visualizar mês", date.today().replace(day=1), key="month_filter")
month = selected_date.strftime("%Y-%m")
df = transactions_for_month(month)

if df.empty:
    st.info("Nenhum lançamento encontrado.")
else:
    st.dataframe(
        df[["id", "occurred_on", "description", "kind", "category", "account", "status", "amount"]],
        use_container_width=True, hide_index=True,
        column_config={"amount": st.column_config.NumberColumn("Valor", format="R$ %.2f")},
    )
    ids = {f"#{row.id} — {row.description}": int(row.id) for row in df.itertuples()}
    selected = st.selectbox("Excluir lançamento", [""] + list(ids))
    if selected and st.button("Excluir", type="secondary"):
        delete_transaction(ids[selected])
        st.success("Lançamento excluído.")
        st.rerun()

