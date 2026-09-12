from datetime import date

import pandas as pd
import pytest

from finance_control.importer import expand_plan, read_plan_file


def base_row(**updates):
    row = {
        "descricao": "Aluguel", "valor": 2870, "tipo": "Despesa",
        "categoria": "Moradia", "conta": "Nubank", "primeira_data": "05/09/2026",
        "status": "Previsto", "recorrencia": "Única", "data_final": None,
        "observacoes": "",
    }
    row.update(updates)
    return row


def test_expand_monthly_plan_preserves_day_and_limits_end_date():
    plan = pd.DataFrame([base_row(
        primeira_data=date(2026, 9, 30), recorrencia="Mensal", data_final=date(2026, 11, 30)
    )])
    rows = expand_plan(plan)
    assert [row["occurred_on"] for row in rows] == [
        "2026-09-30", "2026-10-30", "2026-11-30"
    ]


def test_expand_plan_rejects_unknown_account():
    with pytest.raises(ValueError, match="conta desconhecida"):
        expand_plan(pd.DataFrame([base_row(conta="Banco inexistente")]))


def test_read_csv_detects_semicolon_and_brazilian_amount():
    content = (
        "descricao;valor;tipo;categoria;conta;primeira_data;status\n"
        "Aluguel;2.870,00;Despesa;Moradia;Nubank;05/09/2026;Previsto\n"
    ).encode("utf-8")
    rows = expand_plan(read_plan_file("plano.csv", content))
    assert rows[0]["amount"] == 2870.0
