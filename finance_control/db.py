from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("FINANCE_DB_PATH", "data/finance.db"))
_remote_client: Any | None = None
_remote_user_id: str | None = None


def configure_remote(client: Any, user_id: str) -> None:
    global _remote_client, _remote_user_id
    _remote_client = client
    _remote_user_id = user_id


def remote_enabled() -> bool:
    return _remote_client is not None and _remote_user_id is not None


@contextmanager
def connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    if remote_enabled():
        return
    with connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                kind TEXT NOT NULL CHECK(kind IN ('Receita', 'Despesa')),
                category TEXT NOT NULL,
                account TEXT NOT NULL,
                occurred_on TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pago',
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS budgets (
                month TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                PRIMARY KEY (month, category)
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )


def list_transactions(month: str) -> list[dict]:
    if remote_enabled():
        response = (
            _remote_client.table("transactions").select("*")
            .eq("user_id", _remote_user_id).gte("occurred_on", f"{month}-01")
            .lt("occurred_on", _next_month(month)).order("occurred_on", desc=True)
            .order("created_at", desc=True).execute()
        )
        return response.data or []
    with connection() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT * FROM transactions WHERE substr(occurred_on, 1, 7) = ? "
            "ORDER BY occurred_on DESC, id DESC", (month,)
        ).fetchall()]


def insert_transaction(payload: dict) -> str | int:
    if remote_enabled():
        response = _remote_client.table("transactions").insert(
            {**payload, "user_id": _remote_user_id}
        ).execute()
        return response.data[0]["id"]
    with connection() as conn:
        cursor = conn.execute(
            """INSERT INTO transactions
            (description, amount, kind, category, account, occurred_on, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            tuple(payload[key] for key in (
                "description", "amount", "kind", "category", "account",
                "occurred_on", "status", "notes"
            )),
        )
        return int(cursor.lastrowid)


def remove_transaction(transaction_id: str | int) -> None:
    if remote_enabled():
        (_remote_client.table("transactions").delete().eq("id", str(transaction_id))
         .eq("user_id", _remote_user_id).execute())
        return
    with connection() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))


def list_budgets(month: str) -> list[dict]:
    if remote_enabled():
        response = (_remote_client.table("budgets").select("category,amount")
                    .eq("user_id", _remote_user_id).eq("month", month)
                    .order("category").execute())
        return response.data or []
    with connection() as conn:
        return [dict(row) for row in conn.execute(
            "SELECT category, amount FROM budgets WHERE month = ? ORDER BY category", (month,)
        ).fetchall()]


def save_budget(month: str, category: str, amount: float) -> None:
    if remote_enabled():
        (_remote_client.table("budgets").upsert(
            {"user_id": _remote_user_id, "month": month, "category": category, "amount": amount},
            on_conflict="user_id,month,category",
        ).execute())
        return
    with connection() as conn:
        conn.execute(
            "INSERT INTO budgets(month, category, amount) VALUES (?, ?, ?) "
            "ON CONFLICT(month, category) DO UPDATE SET amount = excluded.amount",
            (month, category, amount),
        )


def get_setting(key: str, default: str = "") -> str:
    if remote_enabled():
        response = (_remote_client.table("settings").select("value")
                    .eq("user_id", _remote_user_id).eq("key", key).limit(1).execute())
        return response.data[0]["value"] if response.data else default
    with connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    if remote_enabled():
        (_remote_client.table("settings").upsert(
            {"user_id": _remote_user_id, "key": key, "value": value},
            on_conflict="user_id,key",
        ).execute())
        return
    with connection() as conn:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value)
        )


def _next_month(month: str) -> str:
    year, current = map(int, month.split("-"))
    return f"{year + 1}-01-01" if current == 12 else f"{year}-{current + 1:02d}-01"

