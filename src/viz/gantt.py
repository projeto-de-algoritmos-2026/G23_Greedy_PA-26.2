"""Gantt comparativo multi-linha (EDF / SJF / Slack) em Plotly."""

from typing import Dict

import plotly.graph_objects as go
import plotly.express as px

from models import ScheduleResult

LATE_COLOR = "#e03131"


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
                width=0.5,
                hovertemplate=(
                    f"<b>{job.id}</b><br>"
                    f"início: {job.start} | fim: {job.finish}<br>"
                    f"deadline: {job.deadline} | atraso: {job.lateness}"
                    "<extra></extra>"
                ),
            ))

            # marcador pontilhado na posição do deadline
            fig.add_trace(go.Scatter(
                x=[job.deadline],
                y=[algo],
                mode="markers",
                marker=dict(symbol="line-ns-open", size=22, line=dict(color=color, width=2)),
                showlegend=False,
                hoverinfo="skip",
            ))

            if job.lateness > 0:
                fig.add_trace(go.Bar(
                    x=[job.lateness],
                    y=[algo],
                    base=[job.deadline],
                    orientation="h",
                    name=f"{job.id} (atraso)",
                    showlegend=False,
                    marker_color=LATE_COLOR,
                    width=0.5,
                    hovertemplate=f"<b>{job.id}</b> atrasado em {job.lateness}<extra></extra>",
                ))

    fig.update_layout(
        barmode="overlay",
        yaxis=dict(
            categoryorder="array",
            categoryarray=list(reversed(algorithms)),
            title="Algoritmo",
        ),
        xaxis=dict(title="Tempo"),
        legend_title_text="Tarefa",
        margin=dict(l=10, r=10, t=30, b=10),
        height=120 + 90 * len(algorithms),
    )

    return fig
