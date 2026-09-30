from pathlib import Path

from finance_control.auth import _friendly_auth_error


def test_rls_covers_every_table_and_operation():
    sql = Path("supabase/migrations/001_initial_schema.sql").read_text(encoding="utf-8")
    for table in ("transactions", "budgets", "settings"):
        assert f"alter table public.{table} enable row level security" in sql
        for operation in ("select", "insert", "update", "delete"):
            assert f'create policy "{table}_{operation}_own"' in sql
    assert "revoke all" in sql
    assert "from anon, authenticated" in sql
    assert "service_role" not in sql


def test_private_files_are_gitignored():
    ignored = Path(".gitignore").read_text(encoding="utf-8")
    assert ".streamlit/secrets.toml" in ignored
    assert "data/" in ignored


def test_auth_errors_are_safe_and_actionable():
    error = ValueError("Invalid login credentials")
    message = _friendly_auth_error(error)
    assert "Supabase recusou" in message
    assert "Invalid login credentials" not in message
