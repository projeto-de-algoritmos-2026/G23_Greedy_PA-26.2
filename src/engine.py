"""Ponto único de acesso ao motor de escalonamento.

Tenta usar os módulos reais do Integrante A (scheduler.py, presets.py,
generator.py). Se ainda não existirem, cai para mock_data.py — mesma
assinatura, mesmo contrato de models.py. O resto do app nunca importa
scheduler/presets/generator/mock_data diretamente, só este módulo.
"""

from typing import Dict, List, Tuple

from models import Job, ScheduleResult

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
