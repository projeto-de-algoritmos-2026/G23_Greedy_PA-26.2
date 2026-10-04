"""Fundamentação: o enunciado, o teorema, a prova por troca de inversões e o
diagnóstico de cada heurística.

Esta aba é deliberadamente tipográfica — teorema em serifa itálica de display,
passos numerados como um artigo. A fundamentação teórica é entrega do
Integrante A; aqui ela é apresentada, não produzida.
"""

from html import escape
from typing import Dict, List, Tuple

import streamlit as st

from insights import algo_meta
from models import ScheduleResult

_PROOF_STEPS: List[Tuple[str, bool]] = [
    ("Chame de <strong>inversão</strong> um par de tarefas vizinhas no cronograma em que "
     "<span class='qd-math'>i</span> roda imediatamente antes de <span class='qd-math'>j</span>, "
     "mas <span class='qd-math'>d_i > d_j</span> — a de prazo mais folgado passou na frente.", False),

    ("O cronograma do EDF não tem ociosidade e, por construção, <strong>não contém "
     "inversão alguma</strong>: ele ordena por prazo crescente.", False),

    ("Se um cronograma tem alguma inversão, então tem pelo menos um <strong>par adjacente "
     "invertido</strong>. (Se nenhum par vizinho estivesse invertido, os prazos seriam "
     "não-decrescentes ao longo de todo o cronograma — sem inversão nenhuma.)", False),

    ("Troque esse par adjacente e acompanhe as consequências. Nenhuma outra tarefa muda de "
     "lugar nem de tempo: a soma das durações das duas é a mesma, então o bloco que elas "
     "ocupam começa e termina nos mesmos instantes. <strong>Só os atrasos dessas duas podem "
     "mudar.</strong>", False),

    ("<span class='qd-math'>j</span>, que agora roda primeiro, termina <em>mais cedo</em> do "
     "que terminava antes. Seu atraso não aumenta.", False),

    ("<span class='qd-math'>i</span>, que agora roda em segundo, termina exatamente no "
     "instante em que <span class='qd-math'>j</span> terminava antes da troca. Como "
     "<span class='qd-math'>d_i > d_j</span>, o atraso de <span class='qd-math'>i</span> "
     "depois da troca é <strong>no máximo</strong> o atraso que <span class='qd-math'>j</span> "
     "tinha antes dela.", False),

    ("Logo o máximo entre os dois atrasos não cresce, e como nenhuma outra tarefa foi tocada, "
     "<span class='qd-math'>L_max</span> do cronograma inteiro <strong>não aumenta</strong>.", False),

    ("Cada troca dessas reduz em <strong>exatamente 1</strong> o total de pares fora de ordem — "
     "contando todos os pares, não só os vizinhos — e esse total é finito. Logo o processo "
     "termina. Repetindo-o, qualquer cronograma ótimo vira o cronograma do EDF sem nunca piorar "
     "<span class='qd-math'>L_max</span>. Portanto <strong>o EDF é ótimo</strong>.", True),
]


def render_theory(results: Dict[str, ScheduleResult]) -> None:
    _render_problem()
    _render_theorem()
    _render_proof()
    _render_failures(results)
    _render_complexity()


def _render_problem() -> None:
    st.markdown(
        '<p class="qd-eyebrow">o problema</p>'
        '<p class="qd-note" style="max-width:70ch;margin-top:0">'
        "Uma única máquina, <strong>sem preempção</strong>, começando em "
        "<span class='qd-math'>s = 0</span> e sem ociosidade entre tarefas. Cada tarefa "
        "<span class='qd-math'>i</span> tem duração <span class='qd-math'>t_i</span> e prazo "
        "<span class='qd-math'>d_i</span>. Escolhida uma ordem, tudo o mais é consequência: "
        "<span class='qd-math'>f_i = s_i + t_i</span>, o atraso é "
        "<span class='qd-math'>L_i = max(0, f_i − d_i)</span> e o que se quer minimizar é "
        "<span class='qd-math'>L_max = max_i L_i</span>.</p>"
        '<p class="qd-note" style="max-width:70ch">'
        "Note o que <em>não</em> está em jogo: como não há ociosidade, toda ordem termina no "
        "mesmo instante <span class='qd-math'>Σ t_i</span>. O makespan é invariante. A única "
        "coisa que a ordem decide é <strong>quem paga o atraso</strong>.</p>",
        unsafe_allow_html=True,
    )


def _render_theorem() -> None:
    st.markdown(
        '<div class="qd-theorem" style="margin-top:2.4rem">'
        '<p class="qd-theorem-label">teorema</p>'
        '<p class="qd-theorem-body">Ordenar as tarefas por prazo crescente produz um '
        "cronograma de atraso máximo mínimo.</p>"
        "</div>",
        unsafe_allow_html=True,
    )


def _render_proof() -> None:
    items = "".join(
        f'<div class="qd-proof-item{" is-qed" if is_qed else ""}"><p>{body}</p></div>'
        for body, is_qed in _PROOF_STEPS
    )
    st.markdown(
        '<p class="qd-eyebrow">prova — argumento de troca de inversões</p>'
        f'<div class="qd-proof">{items}</div>',
        unsafe_allow_html=True,
    )


def _render_failures(results: Dict[str, ScheduleResult]) -> None:
    st.markdown(
        '<p class="qd-eyebrow" style="margin-top:2.8rem">por que as gulosas erram</p>',
        unsafe_allow_html=True,
    )
    columns = st.columns(len(results) or 1, gap="medium")
    for column, algo in zip(columns, results):
        meta = algo_meta(algo)
        with column:
            st.markdown(
                '<div class="qd-fail-card">'
                f"<h4>{escape(meta.short)}</h4>"
                f'<p><em style="color:var(--text-faint)">ordena por {escape(meta.criterion)}.</em><br><br>'
                f"{escape(meta.verdict)}</p>"
                "</div>",
                unsafe_allow_html=True,
            )


def _render_complexity() -> None:
    st.markdown(
        '<p class="qd-eyebrow" style="margin-top:2.8rem">custo</p>'
        '<p class="qd-note" style="max-width:70ch;margin-top:0">'
        "As três estratégias têm o mesmo custo: uma ordenação, "
        "<span class='qd-math'>O(n log n)</span>, seguida de uma varredura linear que "
        "acumula <span class='qd-math'>f_i</span> e <span class='qd-math'>L_i</span>, "
        "<span class='qd-math'>O(n)</span>. Elas não diferem em desempenho — diferem em "
        "<strong>qual chave</strong> passam para a ordenação. É o critério, e só ele, que "
        "separa o ótimo do subótimo.</p>",
        unsafe_allow_html=True,
    )
