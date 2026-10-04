import streamlit as st

from components.metrics import render_metrics
from components.sidebar import render_sidebar
from engine import run_all
from viz.gantt import build_gantt_figure

st.set_page_config(page_title="EDF vs. Heurísticas", layout="wide")

st.title("Escalonador de Tarefas: Minimização do Maior Atraso")
st.caption("EDF (ótimo) vs. SJF e Smallest Slack Time (heurísticas gulosas que falham)")

jobs = render_sidebar()

if not jobs:
    st.info("Selecione um preset, gere tarefas aleatórias ou adicione tarefas manualmente no painel lateral.")
    st.stop()

results = run_all(jobs)

st.subheader("Linha do tempo comparativa")
st.plotly_chart(build_gantt_figure(results), width="stretch")

st.subheader("Atraso máximo (L_max) por algoritmo")
render_metrics(results)
