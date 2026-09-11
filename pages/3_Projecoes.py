from datetime import date

import plotly.graph_objects as go
import streamlit as st

from finance_control.auth import require_auth
from finance_control.services import projection

st.set_page_config(page_title="Projeções", page_icon="📈", layout="wide")
require_auth()
st.title("Projeção de caixa")
st.caption("A projeção considera os lançamentos previstos cadastrados para cada mês.")

selected_date = st.date_input("A partir de", date.today().replace(day=1))
months = st.slider("Horizonte", 3, 24, 12)
df = projection(selected_date.strftime("%Y-%m"), months)

fig = go.Figure()
fig.add_bar(x=df["month"], y=df["Receitas"], name="Receitas", marker_color="#22c55e")
fig.add_bar(x=df["month"], y=df["Despesas"], name="Despesas", marker_color="#f97316")
fig.add_scatter(x=df["month"], y=df["Saldo acumulado"], name="Saldo acumulado",
                mode="lines+markers", line=dict(color="#2563eb", width=3), yaxis="y2")
fig.update_layout(barmode="group", hovermode="x unified", height=440,
                  yaxis2=dict(overlaying="y", side="right", showgrid=False),
                  margin=dict(l=0, r=0, t=20, b=0))
st.plotly_chart(fig, use_container_width=True)
st.dataframe(df, use_container_width=True, hide_index=True,
             column_config={name: st.column_config.NumberColumn(format="R$ %.2f")
                            for name in ["Receitas", "Despesas", "Saldo acumulado"]})
