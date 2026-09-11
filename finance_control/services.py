from __future__ import annotations

from datetime import date

import pandas as pd

from finance_control.db import execute, query

CATEGORIES = [
    "Moradia", "Alimentação", "Transporte", "Saúde", "Educação",
    "Lazer", "Assinaturas", "Dívidas", "Renda", "Outros",
]
ACCOUNTS = ["Nubank", "PicPay", "Vale-alimentação", "Dinheiro", "Outro"]


def add_transaction(description: str, amount: float, kind: str, category: str,
                    account: str, occurred_on: date, status: str, notes: str = "") -> int:
    if not description.strip():
        raise ValueError("A descrição é obrigatória.")
    if amount <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    return execute(
        """INSERT INTO transactions
        (description, amount, kind, category, account, occurred_on, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (description.strip(), amount, kind, category, account,
         occurred_on.isoformat(), status, notes.strip()),
    )


def delete_transaction(transaction_id: int) -> None:
    execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))


def transactions_for_month(month: str) -> pd.DataFrame:
    rows = query(
        "SELECT * FROM transactions WHERE substr(occurred_on, 1, 7) = ? "
        "ORDER BY occurred_on DESC, id DESC",
        (month,),
    )
    columns = ["id", "description", "amount", "kind", "category", "account",
               "occurred_on", "status", "notes", "created_at"]
    return pd.DataFrame(rows, columns=columns)


def monthly_summary(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {"income": 0.0, "expense": 0.0, "pending": 0.0, "balance": 0.0}
    paid_or_planned = df[df["status"].isin(["Pago", "Previsto", "Atrasado"])]
    income = paid_or_planned.loc[paid_or_planned["kind"] == "Receita", "amount"].sum()
    expense = paid_or_planned.loc[paid_or_planned["kind"] == "Despesa", "amount"].sum()
    pending = df.loc[(df["kind"] == "Despesa") & (df["status"] != "Pago"), "amount"].sum()
    return {"income": float(income), "expense": float(expense),
            "pending": float(pending), "balance": float(income - expense)}


def upsert_budget(month: str, category: str, amount: float) -> None:
    execute(
        "INSERT INTO budgets(month, category, amount) VALUES (?, ?, ?) "
        "ON CONFLICT(month, category) DO UPDATE SET amount = excluded.amount",
        (month, category, amount),
    )


def budgets_for_month(month: str) -> pd.DataFrame:
    rows = query("SELECT category, amount FROM budgets WHERE month = ? ORDER BY category", (month,))
    return pd.DataFrame(rows, columns=["category", "amount"])


def budget_progress(month: str) -> pd.DataFrame:
    budgets = budgets_for_month(month)
    tx = transactions_for_month(month)
    spent = (
        tx[tx["kind"] == "Despesa"].groupby("category", as_index=False)["amount"].sum()
        if not tx.empty else pd.DataFrame(columns=["category", "amount"])
    )
    spent = spent.rename(columns={"amount": "spent"})
    result = budgets.rename(columns={"amount": "budget"}).merge(spent, on="category", how="outer")
    if result.empty:
        return pd.DataFrame(columns=["category", "budget", "spent", "remaining", "usage"])
    result[["budget", "spent"]] = result[["budget", "spent"]].fillna(0.0)
    result["remaining"] = result["budget"] - result["spent"]
    result["usage"] = result.apply(
        lambda row: row["spent"] / row["budget"] * 100 if row["budget"] else 0.0, axis=1
    )
    return result.sort_values("spent", ascending=False)


def projection(start_month: str, months: int = 12) -> pd.DataFrame:
    start = pd.Period(start_month, freq="M")
    items = []
    running = 0.0
    for offset in range(months):
        period = start + offset
        df = transactions_for_month(str(period))
        summary = monthly_summary(df)
        running += summary["balance"]
        items.append({"month": str(period), "Receitas": summary["income"],
                      "Despesas": summary["expense"], "Saldo acumulado": running})
    return pd.DataFrame(items)

