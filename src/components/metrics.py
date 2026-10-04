"""Placar: L_max por estratégia, com o ótimo coroado e a degradação medida.

O número que importa no trabalho é um só — L_max. Então ele é o maior elemento
da tela, em serifa de display, e tudo o mais (quantas atrasaram, quanto piorou
em relação ao ótimo) orbita em volta dele em monoespaçada pequena.
"""

from html import escape
from typing import Dict

import streamlit as st

from insights import algo_meta, summarize
from models import ScheduleResult


def _card_html(
    algo: str,
    result: ScheduleResult,
    best: int,
    worst: int,
    index: int,
) -> str:
    meta = algo_meta(algo)
    delta = result.max_lateness - best
    is_best = delta == 0

    if is_best:
        klass, value_class = "qd-score is-best", ""
        delta_html = (
            '<div class="qd-score-delta is-ok">menor atraso máximo da comparação</div>'
        )
    else:
        klass, value_class = "qd-score is-worse", ""
        if best > 0:
            pct = delta / best * 100
            detail = f"+{delta} sobre o ótimo · {pct:.0f}% pior"
        else:
            detail = f"+{delta} sobre o ótimo · o ótimo zera o atraso"
        delta_html = f'<div class="qd-score-delta">{escape(detail)}</div>'

    fill = 0 if worst <= 0 else result.max_lateness / worst * 100

    return (
        f'<div class="{klass}{value_class}" style="animation-delay:{index * 0.08:.2f}s">'
        f'<p class="qd-score-name">{escape(meta.short)}</p>'
        f'<p class="qd-score-full">{escape(meta.full)}</p>'
        f'<div class="qd-score-value">{result.max_lateness}'
        f'<span class="qd-unit">L max</span></div>'
        f"{delta_html}"
        f'<div class="qd-score-bar"><span style="width:{fill:.2f}%;'
        f'animation-delay:{index * 0.08 + 0.1:.2f}s"></span></div>'
        f'<div class="qd-score-foot">{escape(summarize(result))}</div>'
        "</div>"
    )


def render_scoreboard(results: Dict[str, ScheduleResult]) -> None:
    if not results:
        return

    values = [result.max_lateness for result in results.values()]
    best, worst = min(values), max(values)

    columns = st.columns(len(results), gap="medium")
    for index, (column, (algo, result)) in enumerate(zip(columns, results.items())):
        with column:
            st.markdown(
                _card_html(algo, result, best, worst, index),
                unsafe_allow_html=True,
            )

    st.markdown(_verdict_html(results, best, worst), unsafe_allow_html=True)


def _verdict_html(results: Dict[str, ScheduleResult], best: int, worst: int) -> str:
    """A leitura do placar em uma frase — o que o aluno deveria concluir."""
    winners = [algo_meta(a).short for a, r in results.items() if r.max_lateness == best]

    if best == worst:
        body = (
            f"As três estratégias empatam em <span class='qd-math'>L_max = {best}</span>. "
            "Esta instância é frouxa demais para separá-las — troque de preset para ver "
            "o guloso errar."
        )
    elif len(winners) == 1:
        losers = [
            f"{algo_meta(a).short} ({r.max_lateness})"
            for a, r in results.items()
            if r.max_lateness != best
        ]
        body = (
            f"<strong>{escape(winners[0])}</strong> fecha em "
            f"<span class='qd-math'>L_max = {best}</span> e nenhuma ordem faz melhor; "
            f"{escape(' e '.join(losers))} pagam a diferença por escolher o critério errado."
        )
    else:
        body = (
            f"{escape(' e '.join(winners))} empatam no ótimo "
            f"(<span class='qd-math'>L_max = {best}</span>); a pior chega a "
            f"<span class='qd-math'>{worst}</span>."
        )

    return f'<p class="qd-note" style="margin-top:1.3rem">{body}</p>'
