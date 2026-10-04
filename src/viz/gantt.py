"""O Quadro — linha do tempo comparativa EDF / SJF / Slack.

Desenhado à mão em HTML + CSS em vez de Plotly. O motivo é concreto: o quadro
precisa de revelação animada passo a passo, hachura só no trecho que passou do
prazo, marcador de prazo por tarefa e realce cruzado (passar o mouse numa
tarefa acende a mesma tarefa nas outras linhas). Nada disso sai de um gráfico
de barras pronto.

Geometria: tudo em porcentagem da trilha, com `x_max` ancorado no makespan — um
prazo distante (d=100 num cronograma de 11) viraria anotação em vez de esticar
o eixo e achatar as barras.
"""

from html import escape
from typing import Dict, List, Sequence

import streamlit as st

from insights import algo_meta
from models import ScheduledJob, ScheduleResult
from theme import job_color_map

FOCUS_MARGIN = 1.06   # folga à direita do makespan
STAGGER = 0.055       # atraso de animação entre barras consecutivas (s)
MIN_LABEL_WIDTH = 4.2  # % de trilha abaixo do qual o rótulo não cabe na barra
MAX_DEADLINE_MARKS = 14  # acima disso, só marca prazo das tarefas atrasadas


# ─── geometria ────────────────────────────────────────────────────────────────

def _x_max(results: Dict[str, ScheduleResult]) -> float:
    makespan = max(
        (result.total_time for result in results.values()),
        default=1,
    )
    return max(makespan * FOCUS_MARGIN, 1.0)


def _nice_step(span: float, target_ticks: int = 9) -> int:
    """Passo "redondo" para o eixo do tempo (1, 2, 5, 10, 20, 50, ...)."""
    if span <= target_ticks:
        return 1
    raw = span / target_ticks
    magnitude = 10 ** int(len(str(int(raw))) - 1)
    for multiple in (1, 2, 5, 10):
        step = multiple * magnitude
        if step >= raw:
            return int(step)
    return int(10 * magnitude)


def _job_order(results: Dict[str, ScheduleResult]) -> List[str]:
    """IDs na ordem de primeira aparição — fixa a cor de cada tarefa."""
    seen: List[str] = []
    for result in results.values():
        for job in result.jobs_order:
            if job.id not in seen:
                seen.append(job.id)
    return seen


# ─── peças do quadro ──────────────────────────────────────────────────────────

def _tooltip(job: ScheduledJob, algo: str) -> str:
    duration = job.finish - job.start
    slack = job.deadline - duration
    lines = [
        f"{job.id}  ·  {algo}",
        f"duração   t = {duration}",
        f"prazo     d = {job.deadline}",
        f"folga   d−t = {slack}",
        f"janela    [{job.start} → {job.finish}]",
    ]
    if job.lateness > 0:
        lines.append(f"ATRASO    L = {job.lateness}")
    else:
        lines.append("no prazo")
    # &#10; sobrevive dentro do atributo e o CSS (white-space: pre-line) o lê
    # como quebra de linha. Escapa linha por linha para não escapar o próprio &.
    return "&#10;".join(escape(line, quote=True) for line in lines)


def _bar_html(job: ScheduledJob, algo: str, color: str, x_max: float, index: int) -> str:
    duration = job.finish - job.start
    left = job.start / x_max * 100
    width = max(duration / x_max * 100, 0.45)
    delay = index * STAGGER
    safe_id = escape(job.id, quote=True)

    # A faixa de atraso é filha da barra e vem antes do rótulo, para que o id da
    # tarefa continue legível mesmo quando ela está inteira fora do prazo.
    inner = ""
    if job.lateness > 0:
        late_from = max(job.start, job.deadline)
        offset = (late_from - job.start) / duration * 100
        inner += f'<div class="qd-late-zone" style="left:{offset:.4f}%"></div>'

    if width >= MIN_LABEL_WIDTH:
        inner += f'<span class="qd-bar-id">{escape(job.id)}</span>'

    return (
        f'<div class="qd-bar" data-job="{safe_id}" data-tip="{_tooltip(job, algo)}" '
        f'style="left:{left:.4f}%;width:{width:.4f}%;background:{color};'
        f'animation-delay:{delay:.3f}s">{inner}</div>'
    )


def _deadline_html(job: ScheduledJob, color: str, x_max: float) -> str:
    """Marcador na posição real do prazo. Vazio se o prazo cai fora da janela —
    esses viram nota de rodapé em `_faraway_html`, porque ancorá-los ao fim da
    barra os fazia pousar em cima da tarefa seguinte."""
    if job.deadline > x_max:
        return ""

    safe_id = escape(job.id, quote=True)
    missed = job.lateness > 0
    left = job.deadline / x_max * 100
    klass = "qd-dl is-missed" if missed else "qd-dl"
    style = "" if missed else f"color:{color};"
    return (
        f'<div class="{klass}" data-job="{safe_id}" '
        f'style="left:{left:.4f}%;{style}"></div>'
    )


def _faraway_html(results: Dict[str, ScheduleResult], x_max: float) -> str:
    """Prazos longe demais para caber no eixo sem achatar as barras."""
    distant: Dict[str, int] = {}
    for result in results.values():
        for job in result.jobs_order:
            if job.deadline > x_max:
                distant[job.id] = job.deadline
    if not distant:
        return ""

    listed = " · ".join(
        f"<b>{escape(job_id)}</b> → {deadline}" for job_id, deadline in distant.items()
    )
    plural = "s" if len(distant) > 1 else ""
    return (
        f'<p class="qd-faraway">prazo{plural} fora da janela do eixo: {listed} '
        "— folgado demais para marcar sem achatar o cronograma</p>"
    )


def _row_html(
    algo: str,
    result: ScheduleResult,
    colors: Dict[str, str],
    x_max: float,
    tick_gap: float,
    reveal: int | None,
) -> str:
    meta = algo_meta(algo)
    jobs = result.jobs_order if reveal is None else result.jobs_order[:reveal]

    pieces = [
        _bar_html(job, meta.short, colors.get(job.id, "#888"), x_max, i)
        for i, job in enumerate(jobs)
    ]

    # Com muitas tarefas, marcar todo prazo vira ruído: sobram os que importam.
    show_all_deadlines = len(result.jobs_order) <= MAX_DEADLINE_MARKS
    for job in jobs:
        if show_all_deadlines or job.lateness > 0:
            pieces.append(_deadline_html(job, colors.get(job.id, "#888"), x_max))

    # No modo passo a passo, o L_max exibido é o parcial — o que a estratégia já
    # acumulou até aqui, não o veredito final que o aluno ainda não viu.
    lateness = max((job.lateness for job in jobs), default=0)
    chip_class = "is-ok" if lateness == 0 else "is-late"
    chip = f'<span class="qd-row-lmax {chip_class}">L_max = {lateness}</span>'

    if reveal is not None and jobs:
        now = jobs[-1].finish
        pieces.append(
            f'<div class="qd-cursor" data-t="t={now}" '
            f'style="left:{now / x_max * 100:.4f}%"></div>'
        )

    return (
        '<div class="qd-row">'
        '<div class="qd-row-label">'
        f'<span class="qd-algo">{escape(meta.short)}</span>'
        f'<span class="qd-algo-sub">{escape(meta.criterion)}</span>'
        f"{chip}"
        "</div>"
        f'<div class="qd-track" style="--tickgap:{tick_gap:.4f}%">{"".join(pieces)}</div>'
        "</div>"
    )


def _axis_html(x_max: float, step: int) -> str:
    ticks = []
    value = 0
    while value <= x_max:
        left = value / x_max * 100
        # O último tique colidiria com o rótulo "tempo" na borda direita.
        if left <= 92:
            ticks.append(
                f'<div class="qd-axis-tick" style="left:{left:.4f}%">{value}</div>'
            )
        value += step
    ticks.append('<div class="qd-axis-title">tempo</div>')
    # Alinha o eixo com as trilhas (que começam depois do rótulo de 148px).
    return (
        '<div class="qd-row" style="padding:0">'
        '<div></div>'
        f'<div class="qd-axis">{"".join(ticks)}</div>'
        "</div>"
    )


def legend_html(job_ids: Sequence[str], colors: Dict[str, str]) -> str:
    items = [
        '<span class="qd-legend-item"><i class="qd-swatch is-hatch"></i>trecho em atraso</span>',
        '<span class="qd-legend-item"><i class="qd-swatch is-dl"></i>prazo (d)</span>',
    ]
    for job_id in job_ids:
        items.append(
            '<span class="qd-legend-item">'
            f'<i class="qd-swatch" style="background:{colors.get(job_id, "#888")}"></i>'
            f"{escape(job_id)}</span>"
        )
    return f'<div class="qd-legend">{"".join(items)}</div>'


# ─── API pública ──────────────────────────────────────────────────────────────

def build_board_html(
    results: Dict[str, ScheduleResult],
    reveal: int | None = None,
    with_axis: bool = True,
) -> str:
    """O quadro inteiro como HTML. `reveal=k` mostra só os k primeiros despachos."""
    if not results:
        return ""

    x_max = _x_max(results)
    step = _nice_step(x_max)
    tick_gap = step / x_max * 100
    colors = job_color_map(_job_order(results))

    rows = [
        _row_html(algo, result, colors, x_max, tick_gap, reveal)
        for algo, result in results.items()
    ]
    if with_axis:
        rows.append(_axis_html(x_max, step))

    return (
        f'<div class="qd-board">{"".join(rows)}</div>'
        f"{_faraway_html(results, x_max)}"
    )


def render_board(
    results: Dict[str, ScheduleResult],
    reveal: int | None = None,
    show_legend: bool = True,
) -> None:
    html = build_board_html(results, reveal=reveal)
    if show_legend:
        colors = job_color_map(_job_order(results))
        html += legend_html(_job_order(results), colors)
    st.markdown(html, unsafe_allow_html=True)


def job_ids(results: Dict[str, ScheduleResult]) -> List[str]:
    return _job_order(results)


def board_caption(results: Dict[str, ScheduleResult]) -> str:
    """Uma frase factual sobre o que o quadro está mostrando agora."""
    makespan = max((result.total_time for result in results.values()), default=0)
    values = [result.max_lateness for result in results.values()]
    best, worst = min(values), max(values)

    opening = (
        f"As três linhas terminam no mesmo instante <span class='qd-math'>t = {makespan}</span> "
        "— nenhuma estratégia é mais rápida que as outras. "
    )

    if worst == 0:
        return opening + "E aqui ninguém fura o prazo: a instância é frouxa o bastante."
    if best == worst:
        return opening + (
            f"E todas fecham no mesmo <span class='qd-math'>L_max = {best}</span>: "
            "esta instância não separa as estratégias."
        )
    return opening + (
        f"O que muda é quem paga a conta — o atraso máximo vai de "
        f"<span class='qd-math'>{best}</span> a <span class='qd-math'>{worst}</span> "
        "conforme o critério de ordenação."
    )
