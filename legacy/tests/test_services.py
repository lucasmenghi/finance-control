from pathlib import Path

import pandas as pd

from finance_control.services import income_commitment, monthly_summary


def test_monthly_summary_calculates_balance_and_pending():
    df = pd.DataFrame([
        {"kind": "Receita", "amount": 5000.0, "status": "Pago"},
        {"kind": "Despesa", "amount": 1200.0, "status": "Pago"},
        {"kind": "Despesa", "amount": 300.0, "status": "Previsto"},
    ])
    result = monthly_summary(df)
    assert result == {"income": 5000.0, "expense": 1500.0,
                      "pending": 300.0, "balance": 3500.0}


def test_monthly_summary_empty():
    assert monthly_summary(pd.DataFrame()) == {
        "income": 0.0, "expense": 0.0, "pending": 0.0, "balance": 0.0
    }


def test_income_commitment_prioritizes_configured_reference_income():
    assert income_commitment(4000, 8000, 10000) == 50.0


def test_income_commitment_falls_back_to_recorded_income_when_reference_is_zero():
    assert income_commitment(4000, 0, 10000) == 40.0
