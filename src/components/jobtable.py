"""A instância em números: duração, prazo e folga de cada tarefa.

A folga (d − t) é a coluna que mais ensina: é exatamente o critério do Smallest
Slack, e uma folga negativa deixa óbvio que aquela tarefa já está condenada ao
atraso em qualquer ordem que não a ponha quase no início.
"""

from html import escape
from typing import List

import streamlit as st

from models import Job
from theme import job_color_map


def render_job_table(jobs: List[Job]) -> None:
    if not jobs:
        return

    colors = job_color_map([job.id for job in jobs])
    total = sum(job.t for job in jobs)

    rows = []
    for job in jobs:
        slack = job.d - job.t
        tight = "is-tight" if slack < 0 else ""
        rows.append(
            "<tr>"
            f'<td><span class="qd-cell-id">'
            f'<i style="background:{colors.get(job.id, "#888")}"></i>{escape(job.id)}'
            "</span></td>"
            f"<td>{job.t}</td>"
            f"<td>{job.d}</td>"
            f'<td class="{tight}">{slack}</td>'
            "</tr>"
        )

    st.markdown(
        '<p class="qd-eyebrow">a instância</p>'
        '<table class="qd-table">'
        "<thead><tr><th>tarefa</th><th>duração t</th><th>prazo d</th>"
        "<th>folga d−t</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        f'<p style="font-family:var(--mono);font-size:0.62rem;letter-spacing:0.1em;'
        f'color:var(--text-faint);margin-top:0.9rem;text-transform:uppercase">'
        f"{len(jobs)} tarefas · Σt = {total} · a máquina termina em t={total} "
        "em qualquer ordem</p>",
        unsafe_allow_html=True,
    )
