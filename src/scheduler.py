"""Motor algorítmico: EDF (ótimo), SJF e Smallest Slack Time (heurísticas que falham).

Contrato fixado com o Integrante B via models.py / engine.py:
run_edf, run_sjf, run_slack, run_all_heuristics.
"""

from typing import Dict, List

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
