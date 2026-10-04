"""Painel de controle lateral: presets, gerador aleatório e formulário manual."""

from typing import List

import streamlit as st

from engine import generate_jobs, get_presets
from models import Job


def render_sidebar() -> List[Job]:
    st.sidebar.header("Painel de Controle")
    mode = st.sidebar.radio(
        "Fonte das tarefas",
        ["Preset", "Gerador aleatório", "Manual"],
    )

    if mode == "Preset":
        jobs = _render_preset_picker()
    elif mode == "Gerador aleatório":
        jobs = _render_random_generator()
    else:
        jobs = _render_manual_form()

    return jobs


def _render_preset_picker() -> List[Job]:
    presets = get_presets()
    choice = st.sidebar.selectbox("Preset", list(presets.keys()))
    return presets[choice]


def _render_random_generator() -> List[Job]:
    n = st.sidebar.slider("Quantidade de tarefas (N)", 2, 30, 6)
    t_min, t_max = st.sidebar.slider("Faixa de duração (t)", 1, 30, (1, 10))
    d_min, d_max = st.sidebar.slider("Faixa de deadline (d)", 1, 60, (5, 40))
    seed = st.sidebar.number_input("Seed (0 = aleatório)", min_value=0, value=0, step=1)
    return generate_jobs(n, (t_min, t_max), (d_min, d_max), seed or None)


def _render_manual_form() -> List[Job]:
    if "manual_jobs" not in st.session_state:
        st.session_state.manual_jobs = []

    with st.sidebar.form("add_job_form", clear_on_submit=True):
        st.write("Adicionar tarefa")
        job_id = st.text_input("ID", value=f"T{len(st.session_state.manual_jobs) + 1}")
        t = st.number_input("Duração (t)", min_value=1, value=1, step=1)
        d = st.number_input("Deadline (d)", min_value=1, value=10, step=1)
        if st.form_submit_button("Adicionar") and job_id:
            st.session_state.manual_jobs.append(Job(id=job_id, t=int(t), d=int(d)))

    if st.session_state.manual_jobs:
        st.sidebar.caption("Tarefas adicionadas:")
        for job in st.session_state.manual_jobs:
            st.sidebar.write(f"- **{job.id}**: t={job.t}, d={job.d}")
        if st.sidebar.button("Limpar tarefas"):
            st.session_state.manual_jobs = []

    return st.session_state.manual_jobs
