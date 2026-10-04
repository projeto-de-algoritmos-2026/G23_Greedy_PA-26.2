"""Leituras derivadas de um ScheduleResult — nada de novo algoritmo aqui.

Só interpretação para a interface: quantas tarefas furaram o prazo, por que o
guloso escolheu aquela tarefa naquele passo, quantas inversões faltam para
chegar no EDF. É o material textual que transforma o quadro em explicação.
"""

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from models import Job, ScheduledJob, ScheduleResult


# ─── identidade dos algoritmos ────────────────────────────────────────────────

@dataclass(frozen=True)
class AlgoMeta:
    short: str
    full: str
    criterion: str        # rótulo curto do critério de ordenação
    criterion_label: str  # como o critério aparece na narração
    verdict: str          # uma frase sobre o comportamento esperado


_ALGO_META: Dict[str, AlgoMeta] = {
    "EDF": AlgoMeta(
        short="EDF",
        full="Earliest Deadline First",
        criterion="prazo crescente",
        criterion_label="o menor prazo",
        verdict="Ótimo. Nenhuma ordem alcança L_max menor.",
    ),
    "SJF": AlgoMeta(
        short="SJF",
        full="Shortest Job First",
        criterion="duração crescente",
        criterion_label="a menor duração",
        verdict="Persegue vazão, ignora prazo. Quebra quando a tarefa longa é a urgente.",
    ),
    "SLACK": AlgoMeta(
        short="Slack",
        full="Smallest Slack Time",
        criterion="folga (d − t) crescente",
        criterion_label="a menor folga",
        verdict="Confunde aperto com urgência. Quebra quando folga zero vem de uma tarefa longa.",
    ),
    "ORDEM ATUAL": AlgoMeta(
        short="Ordem atual",
        full="sequência que você está editando",
        criterion="trocas manuais",
        criterion_label="a sua escolha",
        verdict="Ordem arbitrária, avaliada pelo mesmo despachante das heurísticas.",
    ),
}

_FALLBACK_META = AlgoMeta(
    short="?", full="heurística", criterion="—", criterion_label="o critério próprio",
    verdict="Heurística gulosa sob comparação.",
)


def algo_meta(key: str) -> AlgoMeta:
    """Tolerante a variações de rótulo do Integrante A ('Slack', 'SLACK', ...)."""
    probe = key.strip().upper()
    if probe in _ALGO_META:
        return _ALGO_META[probe]
    for name, meta in _ALGO_META.items():
        if name in probe or probe in name:
            return meta
    return AlgoMeta(short=key, full=key, criterion=_FALLBACK_META.criterion,
                    criterion_label=_FALLBACK_META.criterion_label,
                    verdict=_FALLBACK_META.verdict)


def criterion_value(key: str, job: ScheduledJob | Job) -> str:
    """O número que o guloso olhou para escolher esta tarefa."""
    probe = key.strip().upper()
    duration = (job.finish - job.start) if isinstance(job, ScheduledJob) else job.t
    deadline = job.deadline if isinstance(job, ScheduledJob) else job.d
    if "EDF" in probe:
        return f"d = {deadline}"
    if "SJF" in probe or "SHORT" in probe:
        return f"t = {duration}"
    if "SLACK" in probe or "FOLGA" in probe:
        return f"d − t = {deadline - duration}"
    return f"t = {duration}, d = {deadline}"


# ─── estatísticas de um escalonamento ─────────────────────────────────────────

@dataclass(frozen=True)
class Stats:
    late_count: int
    on_time_count: int
    total_lateness: int
    makespan: int
    worst_job: str | None


def stats(result: ScheduleResult) -> Stats:
    late = [job for job in result.jobs_order if job.lateness > 0]
    worst = max(late, key=lambda job: job.lateness).id if late else None
    return Stats(
        late_count=len(late),
        on_time_count=len(result.jobs_order) - len(late),
        total_lateness=sum(job.lateness for job in late),
        makespan=result.total_time,
        worst_job=worst,
    )


def summarize(result: ScheduleResult) -> str:
    """Linha de rodapé do cartão do placar."""
    data = stats(result)
    if data.late_count == 0:
        return f"{data.on_time_count} no prazo · nenhuma atrasada"
    plural = "s" if data.late_count > 1 else ""
    return (
        f"{data.late_count} atrasada{plural} · pior: {data.worst_job} "
        f"· atraso somado {data.total_lateness}"
    )


# ─── inversões: o combustível do exchange argument ───────────────────────────

def inverted_flags(order: Sequence[Job]) -> List[bool]:
    """Para cada par adjacente (i, i+1), diz se é uma inversão: d_i > d_{i+1}.

    Zero inversões adjacentes ⇔ os prazos são não-decrescentes ⇔ a sequência é
    uma ordem EDF. É por isso que contar inversões serve de placar no
    laboratório da prova.
    """
    return [order[i].d > order[i + 1].d for i in range(len(order) - 1)]


def total_inversions(order: Sequence[Job]) -> int:
    """Todos os pares (i < j) com d_i > d_j — a medida que a indução faz decrescer.

    Não confundir com `inverted_flags`, que só olha vizinhos. Trocar um par
    adjacente invertido reduz ESTE contador em exatamente 1, enquanto o número
    de inversões *adjacentes* pode até aumentar depois da troca (é o que faz o
    bubble sort precisar de mais passadas). A prova usa este contador justamente
    porque ele decresce de forma estrita, garantindo terminação.
    """
    return sum(
        1
        for i in range(len(order))
        for j in range(i + 1, len(order))
        if order[i].d > order[j].d
    )


def first_inversion(order: Sequence[Job]) -> int | None:
    for i, inverted in enumerate(inverted_flags(order)):
        if inverted:
            return i
    return None


# ─── notas dos presets ────────────────────────────────────────────────────────

_PRESET_NOTES: List[Tuple[Tuple[str, ...], str]] = [
    (("SJF", "SHORTEST"),
     "A tarefa de 1 unidade tem prazo folgado (d=100); a de 10 unidades vence em "
     "d=10. O SJF despacha a curta primeiro por ser curta — e empurra a urgente "
     "para fora do prazo."),
    (("SLACK", "FOLGA"),
     "J₂ tem folga zero (d−t = 0) e parece a mais apertada, então o Slack a põe na "
     "frente. Mas ela é longa: atrasa J₁, que tinha prazo d=2 e cabia em 1 unidade."),
    (("IDEAL", "TODOS NO PRAZO", "ÓTIMO"),
     "Instância frouxa: há ordem suficiente para todo mundo cumprir o prazo. As três "
     "estratégias empatam em L_max = 0 — comparar heurísticas aqui não revela nada."),
]


def preset_note(name: str) -> str | None:
    probe = name.upper()
    for needles, note in _PRESET_NOTES:
        if any(needle in probe for needle in needles):
            return note
    return None
