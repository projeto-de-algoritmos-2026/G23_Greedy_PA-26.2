"""Gantt comparativo multi-linha (EDF / SJF / Slack) em Plotly."""

from typing import Dict

import plotly.graph_objects as go
import plotly.express as px

from models import ScheduleResult

LATE_COLOR = "#e03131"
FOCUS_MARGIN = 1.15  # folga acima do makespan antes de "cortar" o eixo


def _color_map(results: Dict[str, ScheduleResult]) -> Dict[str, str]:
    job_ids = []
    for result in results.values():
        for job in result.jobs_order:
            if job.id not in job_ids:
                job_ids.append(job.id)

    palette = px.colors.qualitative.Set2
    return {job_id: palette[i % len(palette)] for i, job_id in enumerate(job_ids)}


def build_gantt_figure(results: Dict[str, ScheduleResult]) -> go.Figure:
    algorithms = list(results.keys())
    colors = _color_map(results)
    seen_legend = set()

    all_jobs = [job for result in results.values() for job in result.jobs_order]
    makespan = max((job.finish for job in all_jobs), default=1)
    x_focus = max(makespan * FOCUS_MARGIN, 1)

    fig = go.Figure()

    for algo in algorithms:
        result = results[algo]
        for job in result.jobs_order:
            color = colors[job.id]
            show_legend = job.id not in seen_legend
            seen_legend.add(job.id)

            fig.add_trace(go.Bar(
                x=[job.finish - job.start],
                y=[algo],
                base=[job.start],
                orientation="h",
                name=job.id,
                legendgroup=job.id,
                showlegend=show_legend,
                marker_color=color,
                marker_line_width=0,
                width=0.5,
                hovertemplate=(
                    f"<b>{job.id}</b><br>"
                    f"início: {job.start} | fim: {job.finish}<br>"
                    f"deadline: {job.deadline} | atraso: {job.lateness}"
                    "<extra></extra>"
                ),
            ))

            if job.lateness > 0:
                late_start = max(job.start, job.deadline)
                fig.add_trace(go.Bar(
                    x=[job.finish - late_start],
                    y=[algo],
                    base=[late_start],
                    orientation="h",
                    name=f"{job.id} (atraso)",
                    showlegend=False,
                    marker_color=LATE_COLOR,
                    marker_line_width=0,
                    width=0.5,
                    hovertemplate=f"<b>{job.id}</b> atrasado em {job.lateness}<extra></extra>",
                ))

            if job.deadline <= x_focus:
                # marcador pontilhado na posição real do deadline
                fig.add_trace(go.Scatter(
                    x=[job.deadline],
                    y=[algo],
                    mode="markers",
                    marker=dict(symbol="line-ns-open", size=24, color=color, line=dict(width=2)),
                    showlegend=False,
                    hoverinfo="skip",
                ))
            else:
                # deadline fora da janela visível: anota o valor em vez de esticar o eixo
                fig.add_annotation(
                    x=job.finish,
                    y=algo,
                    text=f"{job.id} prazo→{job.deadline}",
                    showarrow=False,
                    xanchor="left",
                    font=dict(size=10, color=color),
                    xshift=6,
                )

        fig.add_annotation(
            xref="paper",
            x=1.0,
            y=algo,
            text=f"<b>L_max = {result.max_lateness}</b>",
            showarrow=False,
            xanchor="left",
            xshift=10,
            font=dict(size=12, color=LATE_COLOR if result.max_lateness > 0 else "#2f9e44"),
        )

    fig.update_layout(
        barmode="overlay",
        yaxis=dict(
            categoryorder="array",
            categoryarray=list(reversed(algorithms)),
            title="Algoritmo",
        ),
        xaxis=dict(title="Tempo", range=[0, x_focus]),
        legend_title_text="Tarefa",
        margin=dict(l=10, r=90, t=30, b=10),
        height=120 + 90 * len(algorithms),
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig
