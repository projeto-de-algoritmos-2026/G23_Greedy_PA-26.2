"""Laboratório do exchange argument — a prova de otimalidade do EDF, na mão.

A prova diz: toda troca de um par adjacente invertido (d_i > d_j) não aumenta
L_max; repetindo trocas, qualquer ordem vira EDF sem piorar. Ler isso convence
pouco. Aqui a pessoa começa da ordem da pior heurística, troca os pares um a
um e vê o L_max descer — nunca subir — até sobrarem zero inversões, momento em
que a sequência *é* a ordem EDF. A trilha de valores à direita é a monotonia
da prova desenhada.
"""

from html import escape
from typing import List, Sequence

import streamlit as st

from engine import evaluate_order, run_all
from insights import first_inversion, inverted_flags, total_inversions
from models import Job
from theme import job_color_map
from viz.gantt import render_board

_ORDER_KEY = "qd_lab_order"
_TRAIL_KEY = "qd_lab_trail"
_FINGERPRINT_KEY = "qd_lab_fingerprint"

TACTILE_LIMIT = 9  # acima disso, os botões par-a-par não cabem na largura


# ─── estado ───────────────────────────────────────────────────────────────────

def _fingerprint(jobs: Sequence[Job]) -> str:
    return "|".join(f"{job.id}:{job.t}:{job.d}" for job in jobs)


def _worst_heuristic_order(jobs: Sequence[Job]) -> List[str]:
    """Começar da pior heurística dá à prova algo para consertar."""
    results = run_all(list(jobs))
    if not results:
        return [job.id for job in jobs]
    worst = max(results.values(), key=lambda result: result.max_lateness)
    return [scheduled.id for scheduled in worst.jobs_order]


def _ensure_state(jobs: Sequence[Job]) -> None:
    fingerprint = _fingerprint(jobs)
    if st.session_state.get(_FINGERPRINT_KEY) != fingerprint:
        st.session_state[_FINGERPRINT_KEY] = fingerprint
        st.session_state[_ORDER_KEY] = _worst_heuristic_order(jobs)
        st.session_state[_TRAIL_KEY] = [_lmax_of(jobs, st.session_state[_ORDER_KEY])]


def _ordered(jobs: Sequence[Job], order: Sequence[str]) -> List[Job]:
    by_id = {job.id: job for job in jobs}
    return [by_id[job_id] for job_id in order if job_id in by_id]


def _lmax_of(jobs: Sequence[Job], order: Sequence[str]) -> int:
    return evaluate_order(_ordered(jobs, order), "Ordem atual").max_lateness


# ─── ações ────────────────────────────────────────────────────────────────────

def _swap(jobs: List[Job], index: int) -> None:
    order: List[str] = st.session_state[_ORDER_KEY]
    order[index], order[index + 1] = order[index + 1], order[index]
    st.session_state[_TRAIL_KEY].append(_lmax_of(jobs, order))


def _swap_first(jobs: List[Job]) -> None:
    index = first_inversion(_ordered(jobs, st.session_state[_ORDER_KEY]))
    if index is not None:
        _swap(jobs, index)


def _solve(jobs: List[Job]) -> None:
    """Consome inversões até não restar nenhuma, registrando cada L_max.

    É literalmente o passo indutivo da prova rodando em loop — e por isso o
    L_max nunca sobe na trilha que isto produz.
    """
    guard = 0
    while guard < 500:
        order = _ordered(jobs, st.session_state[_ORDER_KEY])
        index = first_inversion(order)
        if index is None:
            return
        _swap(jobs, index)
        guard += 1


def _reset(jobs: List[Job]) -> None:
    st.session_state[_ORDER_KEY] = _worst_heuristic_order(jobs)
    st.session_state[_TRAIL_KEY] = [_lmax_of(jobs, st.session_state[_ORDER_KEY])]


def _worst_case(jobs: List[Job]) -> None:
    """Prazo decrescente: o anti-EDF, com o máximo de inversões adjacentes.

    Serve de ponto de partida quando a ordem da heurística já está quase certa —
    com os presets de duas tarefas a prova terminaria em um clique, cedo demais
    para a ideia assentar.
    """
    order = [job.id for job in sorted(jobs, key=lambda job: job.d, reverse=True)]
    st.session_state[_ORDER_KEY] = order
    st.session_state[_TRAIL_KEY] = [_lmax_of(jobs, order)]


# ─── render ───────────────────────────────────────────────────────────────────

def render_exchange_lab(jobs: List[Job]) -> None:
    if len(jobs) < 2:
        st.markdown(
            '<p class="qd-note">O argumento de troca precisa de pelo menos duas '
            "tarefas — não existe par adjacente para inverter.</p>",
            unsafe_allow_html=True,
        )
        return

    _ensure_state(jobs)
    order: List[str] = st.session_state[_ORDER_KEY]
    sequence = _ordered(jobs, order)
    flags = inverted_flags(sequence)
    inversions = sum(flags)
    result = evaluate_order(sequence, "Ordem atual")

    st.markdown(_briefing_html(), unsafe_allow_html=True)
    st.markdown(
        _status_html(
            inversions,
            total_inversions(sequence),
            result.max_lateness,
            st.session_state[_TRAIL_KEY],
        ),
        unsafe_allow_html=True,
    )

    if len(sequence) <= 2:
        # Com duas tarefas só existe um par: a cadeia de trocas que dá sentido à
        # indução nunca aparece. Melhor dizer isso do que deixar a aba parecer
        # trivial por acidente da instância escolhida.
        st.markdown(
            '<p class="qd-note" style="margin:-0.6rem 0 1.4rem;max-width:74ch;'
            'color:var(--text-faint)">Esta instância tem só duas tarefas, então existe '
            "um único par e a prova acaba em uma troca. Para ver a cadeia inteira — "
            "várias trocas, o <span class='qd-math'>L_max</span> descendo em degraus — "
            "troque para o <strong>Preset 3</strong> ou use o gerador aleatório no painel "
            "lateral, e então clique em <strong>pior caso</strong>.</p>",
            unsafe_allow_html=True,
        )

    if len(sequence) <= TACTILE_LIMIT:
        _render_tactile_sequence(jobs, sequence, flags)
    else:
        _render_compact_sequence(jobs, sequence, flags)

    _render_controls(jobs, inversions)

    left, right = st.columns([3, 1], gap="large")
    with left:
        st.markdown(
            '<p class="qd-eyebrow" style="margin-top:1.8rem">cronograma desta ordem</p>',
            unsafe_allow_html=True,
        )
        render_board({"Ordem atual": result}, show_legend=False)
    with right:
        st.markdown(
            '<p class="qd-eyebrow" style="margin-top:1.8rem">L_max a cada troca</p>',
            unsafe_allow_html=True,
        )
        st.markdown(_trail_html(st.session_state[_TRAIL_KEY]), unsafe_allow_html=True)

    if inversions == 0:
        st.markdown(_conclusion_html(jobs, result.max_lateness), unsafe_allow_html=True)


def _briefing_html() -> str:
    """Primeiro o objetivo, depois o mecanismo.

    Sem isto a aba começa falando em "inversões adjacentes" para quem ainda não
    sabe por que deveria se importar com elas.
    """
    return (
        '<p class="qd-note" style="margin:0 0 1.4rem;max-width:74ch">'
        "Não dá para provar que o EDF é ótimo testando todas as ordens — são "
        "<span class='qd-math'>n!</span>. A saída é provar por transformação: "
        "<strong>pegue qualquer ordem, por pior que seja, e mostre que ela vira a ordem "
        "do EDF usando só trocas que nunca pioram o</strong> "
        "<span class='qd-math'>L_max</span>. Se isso vale sempre, nenhuma ordem pode "
        "ser melhor que o EDF. Esta aba é essa demonstração, feita à mão."
        "</p>"
        '<div class="qd-howto">'
        '<div class="qd-howto-item"><span>1</span><p>A fila abaixo começa na ordem de uma '
        "heurística que <em>falhou</em>. Os pares marcados <b>inversão</b> são os vizinhos "
        "em que a tarefa da frente tem prazo <em>maior</em> — alguém menos urgente furando "
        "a fila.</p></div>"
        '<div class="qd-howto-item"><span>2</span><p>Clique no <b>⇄</b> de um par invertido. '
        "Esse é o único movimento permitido pela prova. Acompanhe a trilha do "
        "<span class='qd-math'>L_max</span>: ela pode cair ou ficar igual — "
        "<strong>nunca subir</strong>.</p></div>"
        '<div class="qd-howto-item is-caveat"><span>!</span><p>Uma troca pode <em>expor</em> novos pares '
        "vizinhos invertidos, então <b>pares trocáveis agora</b> às vezes sobe. Isso não "
        "contraria nada: quem a prova faz decrescer é <b>trocas até o EDF</b> — o total de "
        "pares fora de ordem, que cai de exatamente 1 a cada troca e por isso garante que o "
        "processo termina.</p></div>"
        '<div class="qd-howto-item"><span>3</span><p>Quando acabarem as inversões, os prazos '
        "estarão em ordem crescente — e isso <em>é</em> a definição do EDF. Você terá chegado "
        "nele sem nunca piorar nada.</p></div>"
        "</div>"
    )


def _status_html(
    adjacent: int, total: int, lmax: int, trail: Sequence[int]
) -> str:
    """Placar ao vivo.

    Os dois contadores são diferentes de propósito: `adjacent` é quantos botões
    ⇄ estão ativos agora, `total` é quantas trocas ainda faltam até o EDF. Só o
    segundo decresce sempre — e é nele que a prova se apoia.
    """
    tone = "is-done" if total == 0 else "is-inv"

    if total == 0:
        counters = (
            '<span class="qd-stat"><i>inversões</i><b>0</b> — esta já é a ordem EDF</span>'
        )
    else:
        counters = (
            f'<span class="qd-stat"><i>pares trocáveis agora</i><b>{adjacent}</b></span>'
            f'<span class="qd-stat"><i>trocas até o EDF</i><b>{total}</b></span>'
        )

    last = ""
    if len(trail) >= 2:
        before, after = trail[-2], trail[-1]
        verdict = "caiu" if after < before else "não mudou"
        last = (
            f'<span class="qd-stat"><i>última troca</i>'
            f"L_max {before} → {after} <em>({verdict})</em></span>"
        )

    return (
        f'<div class="qd-statbar {tone}">'
        f'<span class="qd-stat"><i>L_max desta ordem</i>{lmax}</span>'
        f"{counters}{last}"
        "</div>"
    )


def _tile_html(job: Job, color: str) -> str:
    return (
        f'<div class="qd-tile" style="border-bottom:2px solid {color}">'
        f'<div class="qd-tile-id">{escape(job.id)}</div>'
        f'<div class="qd-tile-meta">t {job.t} · d {job.d}</div>'
        "</div>"
    )


def _render_tactile_sequence(
    jobs: List[Job], sequence: List[Job], flags: List[bool]
) -> None:
    """Uma coluna por tarefa, intercalada com o botão de troca do par."""
    colors = job_color_map([job.id for job in jobs])
    widths: List[float] = []
    for i in range(len(sequence)):
        widths.append(1.5)
        if i < len(sequence) - 1:
            widths.append(1.0)

    columns = st.columns(widths, gap="small", vertical_alignment="center")

    for i, job in enumerate(sequence):
        with columns[i * 2]:
            st.markdown(_tile_html(job, colors.get(job.id, "#888")), unsafe_allow_html=True)

        if i < len(sequence) - 1:
            with columns[i * 2 + 1]:
                inverted = flags[i]
                # Mostrar a comparação que define a inversão, não só o rótulo:
                # é a conta "d da frente > d de trás" que a pessoa precisa ver.
                left_d, right_d = sequence[i].d, sequence[i + 1].d
                badge = "inversão" if inverted else "em ordem"
                badge_class = "is-inv" if inverted else "is-fine"
                comparison = f"d {left_d} {'>' if inverted else '≤'} d {right_d}"
                st.markdown(
                    f'<div style="text-align:center;margin-bottom:0.35rem">'
                    f'<span class="qd-inv-badge {badge_class}">{badge}</span>'
                    f'<span class="qd-inv-math">{comparison}</span></div>',
                    unsafe_allow_html=True,
                )
                st.button(
                    "⇄",
                    key=f"qd_swap_{i}",
                    width="stretch",
                    on_click=_swap,
                    args=(jobs, i),
                    help=(
                        f"Trocar {sequence[i].id} com {sequence[i + 1].id}"
                        + (" — este par está invertido" if inverted else "")
                    ),
                )


def _render_compact_sequence(
    jobs: List[Job], sequence: List[Job], flags: List[bool]
) -> None:
    """Muitas tarefas: a sequência vira leitura, e a troca passa a ser dirigida
    pelos controles (primeira inversão / resolver tudo)."""
    colors = job_color_map([job.id for job in jobs])
    pieces = []
    for i, job in enumerate(sequence):
        pieces.append(_tile_html(job, colors.get(job.id, "#888")))
        if i < len(flags):
            mark = "↯" if flags[i] else "·"
            color = "var(--amber)" if flags[i] else "var(--text-faint)"
            pieces.append(
                f'<div style="display:grid;place-items:center;width:26px;'
                f'font-family:var(--mono);color:{color}">{mark}</div>'
            )
    st.markdown(
        f'<div class="qd-seq" style="gap:4px">{"".join(pieces)}</div>',
        unsafe_allow_html=True,
    )
    st.caption("↯ marca um par invertido")


def _render_controls(jobs: List[Job], inversions: int) -> None:
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    first, second, third, fourth, _ = st.columns([1.15, 1, 1, 1, 1.6], gap="small")
    with first:
        st.button(
            "trocar 1ª inversão",
            width="stretch",
            disabled=inversions == 0,
            on_click=_swap_first,
            args=(jobs,),
            help="Faz uma única troca — a mesma que você faria clicando no ⇄.",
        )
    with second:
        st.button(
            "resolver tudo",
            width="stretch",
            disabled=inversions == 0,
            on_click=_solve,
            args=(jobs,),
            help="Encadeia trocas até zerar as inversões. É o passo indutivo da prova em loop.",
        )
    with third:
        st.button(
            "pior caso",
            width="stretch",
            on_click=_worst_case,
            args=(jobs,),
            help="Começa do anti-EDF (prazo decrescente), a ordem com mais inversões possíveis.",
        )
    with fourth:
        st.button(
            "reiniciar",
            width="stretch",
            on_click=_reset,
            args=(jobs,),
            help="Volta para a ordem da heurística que falhou nesta instância.",
        )


def _trail_html(trail: Sequence[int]) -> str:
    if not trail:
        return ""
    peak = max(trail) or 1
    shown = trail[-16:]
    bars = []
    for i, value in enumerate(shown):
        height = max(value / peak * 100, 3)
        last = " is-last" if i == len(shown) - 1 else ""
        bars.append(
            f'<div class="qd-trail-bar{last}" data-v="{value}" '
            f'style="height:{height:.1f}%"></div>'
        )
    descended = trail[0] - trail[-1]
    note = (
        f"caiu {descended} desde o início"
        if descended > 0
        else "nenhuma troca feita ainda" if len(trail) == 1 else "estável — a troca não piorou"
    )
    return (
        f'<div class="qd-trail">{"".join(bars)}</div>'
        f'<p style="font-family:var(--mono);font-size:0.6rem;letter-spacing:0.08em;'
        f'color:var(--text-faint);margin-top:0.9rem;text-transform:uppercase">'
        f"{escape(note)}</p>"
    )


def _conclusion_html(jobs: List[Job], lmax: int) -> str:
    edf = run_all(list(jobs))
    edf_key = next((key for key in edf if "EDF" in key.upper()), None)
    edf_lmax = edf[edf_key].max_lateness if edf_key else lmax
    matches = edf_lmax == lmax

    verdict = (
        f"O mesmo <span class='qd-math'>L_max = {edf_lmax}</span> que o EDF produz "
        "direto — como tinha de ser."
        if matches
        else f"O EDF chega a <span class='qd-math'>L_max = {edf_lmax}</span>."
    )

    return (
        '<div class="qd-panel" style="margin-top:2rem">'
        '<p class="qd-eyebrow">o que você acabou de fazer</p>'
        '<p class="qd-note" style="margin:0;max-width:74ch">'
        "Partindo da ordem de uma heurística que falhava, você removeu uma inversão "
        "por vez. Nenhuma troca aumentou o atraso máximo, e ao fim das trocas sobrou "
        f"uma sequência sem inversões. {verdict} "
        "<strong>Esse é o argumento inteiro:</strong> se qualquer ordem pode ser levada "
        "até o EDF por trocas que não pioram L_max, então nenhuma ordem tem L_max "
        "menor que o do EDF."
        "</p></div>"
    )
