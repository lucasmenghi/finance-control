from __future__ import annotations

from calendar import monthrange
from datetime import date

import pandas as pd

from finance_control.services import ACCOUNTS, CATEGORIES


REQUIRED_COLUMNS = {
    "descricao", "valor", "tipo", "categoria", "conta", "primeira_data", "status"
}
OPTIONAL_COLUMNS = {"recorrencia", "data_final", "observacoes"}
ALLOWED_KINDS = {"Receita", "Despesa"}
ALLOWED_STATUSES = {"Pago", "Previsto", "Atrasado"}


def _as_date(value: object, field: str, row_number: int) -> date:
    if pd.isna(value) or value == "":
        raise ValueError(f"Linha {row_number}: {field} é obrigatório.")
    try:
        return pd.to_datetime(value, dayfirst=True).date()
    except (TypeError, ValueError):
        raise ValueError(f"Linha {row_number}: {field} inválido.") from None


def _add_months(value: date, months: int) -> date:
    total = value.year * 12 + value.month - 1 + months
    year, month_index = divmod(total, 12)
    month = month_index + 1
    return date(year, month, min(value.day, monthrange(year, month)[1]))


def expand_plan(plan: pd.DataFrame) -> list[dict]:
    """Validate a compact import plan and expand monthly recurring entries."""
    normalized = plan.copy()
    normalized.columns = [str(column).strip().lower() for column in normalized.columns]
    missing = REQUIRED_COLUMNS - set(normalized.columns)
    if missing:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))

    rows: list[dict] = []
    for index, source in normalized.iterrows():
        row_number = index + 2
        description = str(source["descricao"]).strip()
        if not description or description.lower() == "nan":
            raise ValueError(f"Linha {row_number}: descrição é obrigatória.")
        try:
            amount = float(source["valor"])
        except (TypeError, ValueError):
            raise ValueError(f"Linha {row_number}: valor inválido.") from None
        if amount <= 0:
            raise ValueError(f"Linha {row_number}: valor deve ser maior que zero.")

        kind = str(source["tipo"]).strip()
        category = str(source["categoria"]).strip()
        account = str(source["conta"]).strip()
        status = str(source["status"]).strip()
        if kind not in ALLOWED_KINDS:
            raise ValueError(f"Linha {row_number}: tipo deve ser Receita ou Despesa.")
        if category not in CATEGORIES:
            raise ValueError(f"Linha {row_number}: categoria desconhecida: {category}.")
        if account not in ACCOUNTS:
            raise ValueError(f"Linha {row_number}: conta desconhecida: {account}.")
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Linha {row_number}: status inválido: {status}.")

        first_date = _as_date(source["primeira_data"], "primeira_data", row_number)
        recurrence = str(source.get("recorrencia", "Única")).strip().lower()
        if recurrence in {"", "nan", "única", "unica"}:
            dates = [first_date]
        elif recurrence == "mensal":
            end_raw = source.get("data_final", None)
            end_date = _as_date(end_raw, "data_final", row_number)
            if end_date < first_date:
                raise ValueError(f"Linha {row_number}: data_final anterior à primeira_data.")
            dates = []
            cursor = first_date
            while cursor <= end_date:
                dates.append(cursor)
                cursor = _add_months(first_date, len(dates))
        else:
            raise ValueError(f"Linha {row_number}: recorrência deve ser Única ou Mensal.")

        notes_raw = source.get("observacoes", "")
        notes = "" if pd.isna(notes_raw) else str(notes_raw).strip()
        rows.extend({
            "description": description,
            "amount": amount,
            "kind": kind,
            "category": category,
            "account": account,
            "occurred_on": item_date.isoformat(),
            "status": status,
            "notes": notes,
        } for item_date in dates)
    return rows


def transaction_signature(row: dict) -> tuple:
    """Fields used to make imports repeatable without duplicating transactions."""
    return tuple(str(row.get(field, "")) for field in (
        "description", "amount", "kind", "category", "account", "occurred_on", "status", "notes"
    ))
