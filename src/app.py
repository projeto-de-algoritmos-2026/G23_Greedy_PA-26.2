"""Escalonador de Tarefas — Minimização do Maior Atraso.

Interface do Integrante B sobre o motor do Integrante A (via engine.py).
A tela conta uma história em quatro tempos: o quadro mostra o resultado, o
passo a passo mostra a decisão, o laboratório deixa a prova nas mãos de quem
usa, e a teoria fecha o argumento.
"""

import streamlit as st

from components.exchange import render_exchange_lab
from components.jobtable import render_job_table
from components.metrics import render_scoreboard
from components.sidebar import render_sidebar
from components.stepper import render_stepper
from components.theory import render_theory
from engine import run_all
from theme import inject_job_highlight_css, inject_theme
from viz.gantt import board_caption, job_ids, render_board

st.set_page_config(
    page_title="Quadro de Despachos — EDF vs. Heurísticas",
    page_icon="◴",
    layout="wide",
)

inject_theme()

st.markdown(
    '<div class="qd-hero">'
    '<div class="qd-kicker"><span class="qd-dot"></span>'
    "análise e projeto de algoritmos · algoritmos gulosos</div>"
    '<h1 class="qd-title">Uma máquina, muitos prazos, <em>um</em> critério certo.</h1>'
    '<p class="qd-lede">Tarefas numa fila única, sem preempção. Toda ordem termina no '
    "mesmo instante — então a ordem não decide <strong>quando</strong> o trabalho acaba, "
    "decide <strong>quem fura o prazo</strong>. Três estratégias gulosas disputam o menor "
    "atraso máximo <code>L_max</code>, e só uma delas é demonstravelmente ótima.</p>"
    "</div>",
    unsafe_allow_html=True,
)

jobs = render_sidebar()

if not jobs:
    st.markdown(
        '<div class="qd-panel"><p class="qd-eyebrow">sem instância</p>'
        '<p class="qd-note" style="margin:0">Escolha um preset, gere tarefas aleatórias '
        "ou preencha a tabela manual no painel lateral. Os presets são os casos que "
        "expõem a falha de cada heurística — comece por eles.</p></div>",
        unsafe_allow_html=True,
    )
    st.stop()

results = run_all(jobs)
inject_job_highlight_css(job_ids(results))

render_scoreboard(results)

st.markdown("<div style='height:2.6rem'></div>", unsafe_allow_html=True)

quadro_tab, passo_tab, prova_tab, teoria_tab = st.tabs(
    ["O quadro", "Passo a passo", "Laboratório da prova", "Teoria"]
)

with quadro_tab:
    st.markdown(
        '<p class="qd-eyebrow">linha do tempo · as três ordens lado a lado</p>',
        unsafe_allow_html=True,
    )
    render_board(results)
    st.markdown(
        f'<p class="qd-note" style="max-width:72ch">{board_caption(results)} '
        "Passe o mouse numa tarefa: ela acende nas outras linhas, no lugar onde "
        "cada estratégia a colocou.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    table_col, _ = st.columns([1.3, 2])
    with table_col:
        render_job_table(jobs)

with passo_tab:
    st.markdown(
        '<p class="qd-eyebrow">despacho · uma tarefa por vez</p>',
        unsafe_allow_html=True,
    )
    render_stepper(results)

with prova_tab:
    st.markdown(
        '<p class="qd-eyebrow">argumento de troca · a prova na sua mão</p>',
        unsafe_allow_html=True,
    )
    render_exchange_lab(jobs)

with teoria_tab:
    render_theory(results)

st.markdown(
    '<div class="qd-foot">'
    "<span>G23 · minimização do maior atraso</span>"
    "<span>motor: integrante A · interface: integrante B</span>"
    "</div>",
    unsafe_allow_html=True,
)
