from __future__ import annotations

import os
from typing import Any

import streamlit as st
from supabase import create_client

from finance_control.db import configure_remote, init_db


def _configuration() -> tuple[str, str]:
    try:
        section = st.secrets.get("supabase", {})
        url = section.get("url", "")
        key = section.get("publishable_key", section.get("anon_key", ""))
    except Exception:
        url, key = "", ""
    return url or os.getenv("SUPABASE_URL", ""), key or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")


def require_auth() -> Any | None:
    if os.getenv("FINANCE_LOCAL_MODE") == "1":
        init_db()
        st.sidebar.caption("Modo local: SQLite")
        return None

    url, key = _configuration()
    if not url or not key:
        st.error("O acesso seguro ainda não foi configurado.")
        st.info("Adicione `supabase.url` e `supabase.publishable_key` nos Secrets do Streamlit.")
        st.stop()

    client = create_client(url, key)
    access_token = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")
    user = None
    if access_token and refresh_token:
        try:
            user = client.auth.set_session(access_token, refresh_token).user
        except Exception:
            _clear_session()

    if user is None:
        _login(client)
        st.stop()

    configure_remote(client, str(user.id))
    with st.sidebar:
        st.caption(f"Conectado como {user.email}")
        if st.button("Sair", use_container_width=True):
            try:
                client.auth.sign_out()
            finally:
                _clear_session()
            st.rerun()
    return client


def _login(client: Any) -> None:
    st.title("Controle Financeiro")
    st.caption("Acesso privado")
    with st.form("login"):
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)
    if submitted:
        try:
            response = client.auth.sign_in_with_password({"email": email, "password": password})
            if response.session is None:
                raise ValueError("Sessão não criada")
            st.session_state["access_token"] = response.session.access_token
            st.session_state["refresh_token"] = response.session.refresh_token
            st.rerun()
        except Exception as exc:
            st.error(_friendly_auth_error(exc))


def _clear_session() -> None:
    st.session_state.pop("access_token", None)
    st.session_state.pop("refresh_token", None)


def _friendly_auth_error(exc: Exception) -> str:
    message = str(exc).lower()
    if "email not confirmed" in message:
        return "Seu e-mail existe, mas ainda não foi confirmado no Supabase."
    if "invalid login credentials" in message:
        return "O Supabase recusou as credenciais. Confirme a senha ou redefina o usuário no painel."
    if "email logins are disabled" in message:
        return "O login por e-mail está desativado nas configurações do Supabase."
    if any(term in message for term in ("api key", "jwt", "project", "url")):
        return "A URL ou a chave publicável configurada no Streamlit não corresponde ao projeto."
    if any(term in message for term in ("timeout", "connection", "network")):
        return "Não foi possível conectar ao Supabase. Tente novamente em alguns instantes."
    return f"Falha de autenticação ({type(exc).__name__}). Consulte os logs do aplicativo."
