import io

import pandas as pd
import streamlit as st

from finance_control.auth import require_auth
from finance_control.importer import expand_plan
from finance_control.services import import_transactions

st.set_page_config(page_title="Importação inicial", page_icon="📥", layout="wide")
require_auth()
st.title("Importação inicial")
st.caption("Os dados importados pertencem somente ao usuário atualmente conectado.")

st.markdown(
    "Envie a planilha `.xlsx` no modelo do Finance Control. Linhas com recorrência **Mensal** "
    "serão expandidas até a data final. Antes de salvar, você verá todos os lançamentos."
)

uploaded = st.file_uploader("Planilha do cenário", type=["xlsx"])
if uploaded:
    try:
        plan = pd.read_excel(io.BytesIO(uploaded.getvalue()), sheet_name="Plano")
        rows = expand_plan(plan)
        preview = pd.DataFrame(rows)
        st.success(f"Planilha válida: {len(rows)} lançamentos preparados.")
        st.dataframe(
            preview,
            use_container_width=True,
            hide_index=True,
            column_config={"amount": st.column_config.NumberColumn("Valor", format="R$ %.2f")},
        )
        confirmation = st.checkbox(
            "Revisei a prévia e quero salvar estes lançamentos somente na minha conta."
        )
        if st.button("Importar cenário", type="primary", disabled=not confirmation):
            result = import_transactions(rows)
            st.success(
                f"Importação concluída: {result['inserted']} adicionados e "
                f"{result['skipped']} duplicados ignorados."
            )
    except (ValueError, KeyError) as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(
            "Não foi possível ler a planilha. Confirme se ela está no modelo e tente novamente. "
            f"Detalhe: {type(exc).__name__}."
        )
