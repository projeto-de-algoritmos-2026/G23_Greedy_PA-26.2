"""Despacho passo a passo — a escolha gulosa narrada no instante em que ocorre.

O quadro completo mostra o resultado; aqui mostra-se a *decisão*. A cada passo
k, cada estratégia anuncia qual tarefa chamou, qual número olhou para decidir
isso, e o que aconteceu com o prazo. É onde fica evidente que as três olham a
mesma fila e enxergam urgências diferentes.
"""

from html import escape
from typing import Dict

import streamlit as st

from insights import algo_meta, criterion_value
from models import ScheduleResult
from viz.gantt import render_board


def render_stepper(results: Dict[str, ScheduleResult]) -> None:
    if not results:
        return

    total = max(len(result.jobs_order) for result in results.values())

    if total <= 1:
        step = total
        st.markdown(
            '<p class="qd-note">Uma tarefa só: não há decisão gulosa para observar. '
            "Acrescente tarefas para que as estratégias discordem.</p>",
            unsafe_allow_html=True,
        )
    else:
        step = st.slider(
            "despachos revelados",
            min_value=1,
            max_value=total,
            value=total,
            help="Arraste para ver a máquina despachar uma tarefa por vez.",
        )

    render_board(results, reveal=step, show_legend=False)

    st.markdown(
        f'<p class="qd-eyebrow" style="margin-top:2rem">decisão no passo '
        f"{step:02d} de {total:02d}</p>",
        unsafe_allow_html=True,
    )

    columns = st.columns(len(results), gap="medium")
    for column, (algo, result) in zip(columns, results.items()):
        with column:
            st.markdown(_narration_html(algo, result, step), unsafe_allow_html=True)


def _narration_html(algo: str, result: ScheduleResult, step: int) -> str:
    meta = algo_meta(algo)
    order = result.jobs_order

    if step > len(order):
        return (
            '<div class="qd-step">'
            f'<p class="qd-step-head">{escape(meta.short)}</p>'
            '<p class="qd-step-idle">fila vazia — já despachou tudo.</p>'
            "</div>"
        )

    job = order[step - 1]
    remaining = len(order) - step
    partial_lmax = max(dispatched.lateness for dispatched in order[:step])

    if job.lateness > 0:
        klass = "is-late"
        verdict = f'<span class="qd-step-verdict is-late">atraso {job.lateness}</span>'
        outcome = f"estourando o prazo <b>d = {job.deadline}</b>"
    else:
        klass = "is-ok"
        verdict = '<span class="qd-step-verdict is-ok">no prazo</span>'
        outcome = f"dentro do prazo <b>d = {job.deadline}</b>"

    # No último despacho não há escolha: citar o critério ali sugeriria uma
    # decisão que a estratégia não chegou a tomar.
    if remaining == 0 and len(order) > 1:
        choice = f"Resta só <b>{escape(job.id)}</b> — entra por eliminação."
    else:
        choice = (
            f"Chama <b>{escape(job.id)}</b>: tem {escape(meta.criterion_label)} "
            f"(<b>{escape(criterion_value(algo, job))}</b>) entre as que sobraram."
        )

    tail = (
        f" Restam {remaining} na fila."
        if remaining
        else f" Fila encerrada: <b>L_max = {partial_lmax}</b>."
    )

    return (
        f'<div class="qd-step {klass}">'
        f'<p class="qd-step-head">{escape(meta.short)} · L_max parcial {partial_lmax}</p>'
        '<p class="qd-step-body">'
        f"{choice} Roda de <b>{job.start}</b> a <b>{job.finish}</b>, {outcome}.{tail}"
        "</p>"
        f"{verdict}"
        "</div>"
    )
