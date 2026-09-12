from __future__ import annotations

import streamlit as st


def brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def palette(dark_mode: bool | None = None) -> dict[str, str]:
    dark = st.session_state.get("dark_mode", False) if dark_mode is None else dark_mode
    if dark:
        return {"background": "#0B0F14", "surface": "#151B23", "text": "#F5F7FA",
                "muted": "#A7B0BE", "border": "#344054", "grid": "#263241",
                "blue": "#4EA3E3", "blue_dark": "#8CC8F2", "gray": "#98A2B3"}
    return {"background": "#FFFFFF", "surface": "#FFFFFF", "text": "#111827",
            "muted": "#667085", "border": "#D0D5DD", "grid": "#EAECF0",
            "blue": "#1261A0", "blue_dark": "#0B3658", "gray": "#98A2B3"}


def apply_theme(dark_mode: bool) -> None:
    c = palette(dark_mode)
    sidebar = "#101720" if dark_mode else "#F2F4F7"
    field = "#18212C" if dark_mode else "#E7ECF2"
    field_hover = "#202C39" if dark_mode else "#DDE4EC"
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&display=swap');
        :root {{ --cf-bg:{c['background']}; --cf-surface:{c['surface']}; --cf-text:{c['text']};
          --cf-muted:{c['muted']}; --cf-border:{c['border']}; --cf-blue:{c['blue']}; }}
        html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
          font-family:"Arial Narrow",Arial,sans-serif; color:var(--cf-text); background-color:var(--cf-bg); }}
        [data-testid="stMainBlockContainer"] {{ padding-top:3rem; }}
        h1,h2,h3,[data-testid="stMetricLabel"] {{ font-family:"Montserrat",Arial,sans-serif!important;
          letter-spacing:-.02em; color:var(--cf-text)!important; }}
        h1 {{ font-weight:700!important; }} h2,h3 {{ font-weight:600!important; }}
        p,label,[data-testid="stCaptionContainer"] {{ color:var(--cf-muted); }}
        [data-testid="stMetric"] {{ background:var(--cf-surface); border:1px solid var(--cf-border);
          border-top:4px solid var(--cf-blue); padding:18px 20px; min-height:126px; }}
        [data-testid="stMetricLabel"] {{ color:var(--cf-muted)!important; }}
        [data-testid="stMetricValue"] {{ color:var(--cf-text); font-family:"Arial Narrow",Arial,sans-serif; }}
        [data-testid="stSidebar"] {{ background:{sidebar}; }}
        [data-testid="stSidebar"] * {{ color:var(--cf-text); }}
        [data-testid="stForm"] {{ background:var(--cf-surface); border-color:var(--cf-border); }}
        [data-baseweb="input"], [data-baseweb="base-input"],
        [data-baseweb="select"] > div, [data-baseweb="textarea"] {{
          background-color:{field}!important; border-color:var(--cf-border)!important;
          color:var(--cf-text)!important; }}
        [data-baseweb="input"]:hover, [data-baseweb="select"] > div:hover {{
          background-color:{field_hover}!important; }}
        [data-baseweb="input"] input, [data-baseweb="base-input"] input,
        [data-baseweb="textarea"] textarea, [data-baseweb="select"] span {{
          color:var(--cf-text)!important; -webkit-text-fill-color:var(--cf-text)!important; }}
        [data-baseweb="select"] svg, [data-testid="stNumberInput"] button svg,
        [data-testid="stDateInput"] svg {{ fill:var(--cf-text)!important; color:var(--cf-text)!important; }}
        [data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {{
          background-color:var(--cf-surface)!important; color:var(--cf-text)!important; }}
        [role="option"] {{ color:var(--cf-text)!important; }}
        [role="option"]:hover {{ background-color:{field_hover}!important; }}
        [data-testid="stFileUploaderDropzone"] {{
          background-color:{field}!important; border-color:var(--cf-border)!important; }}
        button[kind="primary"], button[kind="primary"] p,
        [data-testid="stFormSubmitButton"] button, [data-testid="stFormSubmitButton"] button p {{
          color:#FFFFFF!important; -webkit-text-fill-color:#FFFFFF!important; }}
        button[kind="primary"] {{ background-color:var(--cf-blue)!important; border-color:var(--cf-blue)!important; }}
        button[kind="secondary"] {{ background-color:var(--cf-surface)!important;
          border-color:var(--cf-border)!important; color:var(--cf-text)!important; }}
        button[kind="secondary"] p {{ color:var(--cf-text)!important; }}
        input:disabled, button:disabled {{ opacity:.62!important; }}
        .executive-kicker {{ color:var(--cf-blue); font-family:"Montserrat",Arial,sans-serif;
          font-size:.78rem; font-weight:700; letter-spacing:.12em; margin-bottom:.25rem; text-transform:uppercase; }}
        .executive-subtitle {{ color:var(--cf-muted); margin-top:-.5rem; }}
        </style>
    """, unsafe_allow_html=True)


def page_header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(f'<div class="executive-kicker">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p class="executive-subtitle">{subtitle}</p>', unsafe_allow_html=True)
