from datetime import date
import io

import pandas as pd
import streamlit as st

from finance_control.importer import expand_plan
from finance_control.services import (
    ACCOUNTS, CATEGORIES, add_transaction, delete_transaction, import_transactions, transactions_for_month,
)
from finance_control.ui import page_header

page_header("Entrada de dados", "Adicione seus Dados", "Importe seu cenário ou registre movimentações individualmente.")

st.subheader("Importar planilha")
st.caption("A importação é vinculada exclusivamente ao usuário conectado e ignora lançamentos idênticos.")

with st.expander("Formato obrigatório do arquivo XLSX", expanded=True):
    st.markdown("O arquivo deve possuir uma aba chamada **Plano**, com os nomes das colunas exatamente como abaixo.")
    st.markdown("""
| Coluna | Obrigatória | Formato e valores aceitos |
|---|---:|---|
| `descricao` | Sim | Texto livre, por exemplo `Aluguel` |
| `valor` | Sim | Número positivo, sem `R$`, por exemplo `2870,00` |
| `tipo` | Sim | `Receita` ou `Despesa` |
| `categoria` | Sim | Moradia, Alimentação, Transporte, Saúde, Educação, Lazer, Assinaturas, Dívidas, Renda ou Outros |
| `conta` | Sim | Nubank, PicPay, Vale-alimentação, Dinheiro ou Outro |
| `primeira_data` | Sim | Data no formato `DD/MM/AAAA` |
| `status` | Sim | `Pago`, `Previsto` ou `Atrasado` |
| `recorrencia` | Não | `Única` ou `Mensal`; se vazia, será considerada única |
| `data_final` | Para mensal | Último mês da recorrência, em `DD/MM/AAAA` |
| `observacoes` | Não | Texto livre |
    """)
    st.info("Cada linha representa um lançamento único ou uma série mensal. A planilha será validada e exibida para revisão antes de salvar.")

uploaded = st.file_uploader("Selecione o XLSX", type=["xlsx"])
if uploaded:
    try:
        plan = pd.read_excel(io.BytesIO(uploaded.getvalue()), sheet_name="Plano")
        rows = expand_plan(plan)
        preview = pd.DataFrame(rows)
        st.success(f"Planilha válida: {len(rows)} lançamentos preparados.")
        st.dataframe(preview, use_container_width=True, hide_index=True,
            column_config={"amount": st.column_config.NumberColumn("Valor", format="R$ %.2f")})
        confirmation = st.checkbox("Revisei a prévia e quero salvar estes lançamentos somente na minha conta.")
        if st.button("Importar dados", type="primary", disabled=not confirmation):
            result = import_transactions(rows)
            st.success(f"Importação concluída: {result['inserted']} adicionados e {result['skipped']} duplicados ignorados.")
    except (ValueError, KeyError) as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error("Não foi possível ler a planilha. Confirme a aba e as colunas do modelo. "
                 f"Detalhe: {type(exc).__name__}.")

st.divider()
st.subheader("Adicionar lançamento manual")
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
    if st.form_submit_button("Adicionar lançamento", type="primary"):
        try:
            add_transaction(description, amount, kind, category, account, occurred_on, status, notes)
            st.success("Lançamento adicionado.")
        except ValueError as exc:
            st.error(str(exc))

st.divider()
st.subheader("Gerenciar lançamentos")
selected_date = st.date_input("Visualizar mês", date.today().replace(day=1), key="month_filter")
month = selected_date.strftime("%Y-%m")
df = transactions_for_month(month)
if df.empty:
    st.info("Nenhum lançamento encontrado.")
else:
    st.dataframe(df[["id", "occurred_on", "description", "kind", "category", "account", "status", "amount"]],
        use_container_width=True, hide_index=True,
        column_config={"amount": st.column_config.NumberColumn("Valor", format="R$ %.2f")})
    ids = {f"#{row.id} — {row.description}": row.id for row in df.itertuples()}
    selected = st.selectbox("Excluir lançamento", [""] + list(ids))
    if selected and st.button("Excluir", type="secondary"):
        delete_transaction(ids[selected]); st.success("Lançamento excluído."); st.rerun()
    st.download_button("Baixar backup CSV", df.to_csv(index=False).encode("utf-8"),
        file_name=f"controle-financeiro-{month}.csv", mime="text/csv")
