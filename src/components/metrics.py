"""Placar comparativo: cards com L_max por algoritmo e degradação vs. o ótimo."""

from typing import Dict

import streamlit as st

from models import ScheduleResult


def render_metrics(results: Dict[str, ScheduleResult]) -> None:
    best = min(result.max_lateness for result in results.values())
    cols = st.columns(len(results))

    for col, (name, result) in zip(cols, results.items()):
        delta = result.max_lateness - best
        is_optimal = delta == 0

        with col:
            st.metric(
                label=f"{name} {'🏆 ótimo' if is_optimal else ''}".strip(),
                value=f"L_max = {result.max_lateness}",
                delta=None if is_optimal else f"+{delta} vs. ótimo",
                delta_color="off" if is_optimal else "inverse",
            )
            if not is_optimal and best > 0:
                pct = delta / best * 100
                st.caption(f"{pct:.0f}% piora em relação ao ótimo")
            elif not is_optimal:
                st.caption("ótimo alcançaria atraso zero")
