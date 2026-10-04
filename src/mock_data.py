"""Fallback de motor/presets/gerador usado enquanto scheduler.py, presets.py e
generator.py (Integrante A) não existem. Respeita o mesmo contrato de models.py,
então o app funciona de ponta a ponta hoje e troca para os módulos reais sem
mudar nenhuma linha de app.py/components/viz."""

import random
from typing import Dict, List, Tuple

from models import Job, ScheduledJob, ScheduleResult


def _evaluate_order(jobs: List[Job], algorithm_name: str) -> ScheduleResult:
    current_time = 0
    max_lateness = 0
    scheduled: List[ScheduledJob] = []

    for job in jobs:
        start = current_time
        finish = start + job.t
        lateness = max(0, finish - job.d)
        max_lateness = max(max_lateness, lateness)

        scheduled.append(ScheduledJob(
            id=job.id,
            start=start,
            finish=finish,
            deadline=job.d,
            lateness=lateness,
        ))
        current_time = finish

    return ScheduleResult(
        algorithm_name=algorithm_name,
        jobs_order=scheduled,
        max_lateness=max_lateness,
        total_time=current_time,
    )


def run_edf(jobs: List[Job]) -> ScheduleResult:
    sorted_jobs = sorted(jobs, key=lambda j: j.d)
    return _evaluate_order(sorted_jobs, "EDF (Earliest Deadline First)")


def run_sjf(jobs: List[Job]) -> ScheduleResult:
    sorted_jobs = sorted(jobs, key=lambda j: j.t)
    return _evaluate_order(sorted_jobs, "SJF (Shortest Job First)")


def run_slack(jobs: List[Job]) -> ScheduleResult:
    sorted_jobs = sorted(jobs, key=lambda j: (j.d - j.t))
    return _evaluate_order(sorted_jobs, "Smallest Slack Time")


def run_all_heuristics(jobs: List[Job]) -> Dict[str, ScheduleResult]:
    return {
        "EDF": run_edf(jobs),
        "SJF": run_sjf(jobs),
        "Slack": run_slack(jobs),
    }


MOCK_PRESETS: Dict[str, List[Job]] = {
    "Preset 1 — Quebra do SJF": [
        Job(id="J1", t=1, d=100),
        Job(id="J2", t=10, d=10),
    ],
    "Preset 2 — Quebra do Smallest Slack": [
        Job(id="J1", t=1, d=2),
        Job(id="J2", t=10, d=10),
    ],
    "Preset 3 — Cenário Ideal (todos no prazo)": [
        Job(id="J1", t=2, d=5),
        Job(id="J2", t=3, d=10),
        Job(id="J3", t=4, d=20),
    ],
}


def generate_random_jobs(
    n: int,
    duration_range: Tuple[int, int] = (1, 10),
    deadline_range: Tuple[int, int] = (5, 40),
    seed: int | None = None,
) -> List[Job]:
    rng = random.Random(seed)
    return [
        Job(
            id=f"T{i + 1}",
            t=rng.randint(*duration_range),
            d=rng.randint(*deadline_range),
        )
        for i in range(n)
    ]
