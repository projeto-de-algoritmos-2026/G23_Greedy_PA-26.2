"""Ponto único de acesso ao motor de escalonamento.

Tenta usar os módulos reais do Integrante A (scheduler.py, presets.py,
generator.py). Se ainda não existirem, cai para mock_data.py — mesma
assinatura, mesmo contrato de models.py. O resto do app nunca importa
scheduler/presets/generator/mock_data diretamente, só este módulo.

Assinaturas públicas estáveis (os componentes dependem delas):
get_presets(), generate_jobs(...), run_all(jobs), evaluate_order(jobs, name).
"""

from typing import Callable, Dict, List, Sequence, Tuple

from models import Job, ScheduledJob, ScheduleResult

try:
    from scheduler import run_all_heuristics as _run_all_heuristics
except ImportError:
    from mock_data import run_all_heuristics as _run_all_heuristics

try:
    from presets import PRESETS as _PRESETS
except ImportError:
    from mock_data import MOCK_PRESETS as _PRESETS

try:
    from generator import generate_random_jobs as _generate_random_jobs
except ImportError:
    from mock_data import generate_random_jobs as _generate_random_jobs


def _local_evaluate_order(jobs: Sequence[Job], algorithm_name: str) -> ScheduleResult:
    """Despacho sequencial de uma ordem já decidida — sem reordenar nada.

    Só entra em ação se o motor do Integrante A não expuser um despachante
    reutilizável. É a mesma recorrência do enunciado (s=0, sem preempção, sem
    ociosidade), não uma segunda heurística.
    """
    current_time = 0
    max_lateness = 0
    scheduled: List[ScheduledJob] = []

    for job in jobs:
        start = current_time
        finish = start + job.t
        lateness = max(0, finish - job.d)
        max_lateness = max(max_lateness, lateness)
        scheduled.append(ScheduledJob(
            id=job.id, start=start, finish=finish, deadline=job.d, lateness=lateness,
        ))
        current_time = finish

    return ScheduleResult(
        algorithm_name=algorithm_name,
        jobs_order=scheduled,
        max_lateness=max_lateness,
        total_time=current_time,
    )


def _resolve_dispatcher() -> Callable[[Sequence[Job], str], ScheduleResult]:
    """Prefere o despachante do Integrante A, para que a conta de L_max do
    laboratório da prova seja literalmente a mesma do motor avaliado."""
    try:
        from scheduler import _evaluate_order as dispatcher  # type: ignore[attr-defined]
        return dispatcher
    except (ImportError, AttributeError):
        return _local_evaluate_order


_evaluate = _resolve_dispatcher()


def get_presets() -> Dict[str, List[Job]]:
    return _PRESETS


def generate_jobs(
    n: int,
    duration_range: Tuple[int, int] = (1, 10),
    deadline_range: Tuple[int, int] = (5, 40),
    seed: int | None = None,
) -> List[Job]:
    return _generate_random_jobs(n, duration_range, deadline_range, seed)


def run_all(jobs: List[Job]) -> Dict[str, ScheduleResult]:
    return _run_all_heuristics(jobs)


def evaluate_order(jobs: Sequence[Job], algorithm_name: str = "Ordem manual") -> ScheduleResult:
    """Avalia uma ordem arbitrária escolhida pelo usuário.

    Usado pelo laboratório do exchange argument: lá a ordem não vem de
    heurística nenhuma, vem das trocas que a pessoa fez à mão.
    """
    return _evaluate(list(jobs), algorithm_name)
