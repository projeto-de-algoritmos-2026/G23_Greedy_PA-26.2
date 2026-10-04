"""Painel de controle: de onde vêm as tarefas.

Três fontes — preset (instâncias que provam o ponto), gerador aleatório
(semente fixa, para o resultado ser reproduzível na apresentação) e tabela
manual (editável in loco, em vez do antigo formulário de uma tarefa por vez).
"""

from html import escape
from typing import List

import pandas as pd
import streamlit as st

from engine import generate_jobs, get_presets
from insights import preset_note
from models import Job

_SEED_KEY = "qd_seed"
_TABLE_KEY = "qd_manual_table"

_DEFAULT_TABLE = pd.DataFrame(
    [
        {"tarefa": "J1", "duração t": 1, "prazo d": 2},
        {"tarefa": "J2", "duração t": 10, "prazo d": 10},
        {"tarefa": "J3", "duração t": 3, "prazo d": 18},
    ]
)


def render_sidebar() -> List[Job]:
    _render_brand()

    mode = st.sidebar.radio(
        "fonte das tarefas",
        ["Preset", "Aleatório", "Manual"],
        horizontal=True,
        label_visibility="visible",
    )
    st.sidebar.markdown(
        '<div style="height:1px;background:var(--hairline);margin:0.9rem 0 1.1rem"></div>',
        unsafe_allow_html=True,
    )

    if mode == "Preset":
        return _render_presets()
    if mode == "Aleatório":
        return _render_generator()
    return _render_manual_table()


def _render_brand() -> None:
    st.sidebar.markdown(
        '<div style="font-family:var(--mono);font-size:0.58rem;letter-spacing:0.26em;'
        'text-transform:uppercase;color:var(--amber);margin-bottom:0.3rem">'
        "painel de controle</div>"
        '<div style="font-family:var(--display);font-size:1.35rem;line-height:1.1;'
        'margin-bottom:1.2rem">Instância em análise</div>',
        unsafe_allow_html=True,
    )


# ─── presets ──────────────────────────────────────────────────────────────────

def _render_presets() -> List[Job]:
    presets = get_presets()
    if not presets:
        st.sidebar.warning("Nenhum preset disponível no motor.")
        return []

    choice = st.sidebar.selectbox("instância", list(presets.keys()))
    note = preset_note(choice)
    if note:
        st.sidebar.markdown(
            '<div style="font-family:var(--prose);font-size:0.84rem;line-height:1.55;'
            'color:var(--text-dim);border-left:2px solid var(--hairline);'
            f'padding-left:0.8rem;margin-top:0.9rem">{escape(note)}</div>',
            unsafe_allow_html=True,
        )
    return list(presets[choice])


# ─── gerador ──────────────────────────────────────────────────────────────────

def _roll_seed() -> None:
    """Semente sempre explícita: a instância não muda sozinha a cada clique em
    outro widget, e dá para repetir exatamente o mesmo caso na apresentação."""
    st.session_state[_SEED_KEY] = (st.session_state[_SEED_KEY] * 97 + 31) % 10000


def _render_generator() -> List[Job]:
    n = st.sidebar.slider("quantidade de tarefas (n)", 2, 30, 7)
    t_min, t_max = st.sidebar.slider("faixa de duração (t)", 1, 30, (1, 10))
    d_min, d_max = st.sidebar.slider("faixa de prazo (d)", 1, 60, (5, 30))

    if _SEED_KEY not in st.session_state:
        st.session_state[_SEED_KEY] = 7

    seed = st.sidebar.number_input(
        "semente", min_value=0, max_value=9999, step=1, key=_SEED_KEY
    )
    # on_click (e não mutação inline): callbacks rodam antes do rerun, então a
    # chave do number_input ainda não foi instanciada quando a alteramos.
    st.sidebar.button("sortear outra instância", width="stretch", on_click=_roll_seed)
    st.sidebar.caption(f"instância reproduzível · semente {seed}")
    return generate_jobs(n, (t_min, t_max), (d_min, d_max), int(seed))


# ─── tabela manual ────────────────────────────────────────────────────────────

def _render_manual_table() -> List[Job]:
    st.sidebar.markdown(
        '<div style="font-family:var(--mono);font-size:0.62rem;letter-spacing:0.14em;'
        'text-transform:uppercase;color:var(--text-dim);margin-bottom:0.5rem">'
        "tabela de tarefas</div>",
        unsafe_allow_html=True,
    )

    if _TABLE_KEY not in st.session_state:
        st.session_state[_TABLE_KEY] = _DEFAULT_TABLE.copy()

    edited = st.sidebar.data_editor(
        st.session_state[_TABLE_KEY],
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        column_config={
            "tarefa": st.column_config.TextColumn("tarefa", width="small", required=True),
            "duração t": st.column_config.NumberColumn("t", min_value=1, step=1, width="small"),
            "prazo d": st.column_config.NumberColumn("d", min_value=1, step=1, width="small"),
        },
        key="qd_manual_editor",
    )
    st.sidebar.caption("edite, use + para adicionar e selecione a linha para remover")

    return _table_to_jobs(edited)


def _table_to_jobs(table: pd.DataFrame) -> List[Job]:
    """Linhas incompletas são ignoradas em silêncio: o editor cria a linha vazia
    no instante em que a pessoa clica em '+', e piscar um erro ali seria ruído."""
    jobs: List[Job] = []
    for position, row in enumerate(table.to_dict("records"), start=1):
        duration, deadline = row.get("duração t"), row.get("prazo d")
        if pd.isna(duration) or pd.isna(deadline):
            continue
        raw_id = str(row.get("tarefa") or "").strip()
        jobs.append(Job(
            id=raw_id or f"T{position}",
            t=max(1, int(duration)),
            d=max(1, int(deadline)),
        ))
    return jobs
