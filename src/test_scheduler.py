"""Testes do motor algorítmico (Integrante A).

Rodar com: pytest src/test_scheduler.py -v
(ou: python -m pytest src/test_scheduler.py -v, a partir da raiz do projeto)
"""

from generator import generate_random_jobs
from models import Job
from presets import PRESETS
from scheduler import run_all_heuristics, run_edf, run_slack, run_sjf


def test_edf_orders_by_deadline():
    jobs = [Job(id="A", t=1, d=5), Job(id="B", t=1, d=2), Job(id="C", t=1, d=9)]
    result = run_edf(jobs)
    assert [j.id for j in result.jobs_order] == ["B", "A", "C"]


def test_sjf_orders_by_duration():
    jobs = [Job(id="A", t=5, d=1), Job(id="B", t=1, d=1), Job(id="C", t=3, d=1)]
    result = run_sjf(jobs)
    assert [j.id for j in result.jobs_order] == ["B", "C", "A"]


def test_slack_orders_by_deadline_minus_duration():
    jobs = [Job(id="A", t=1, d=10), Job(id="B", t=5, d=5), Job(id="C", t=2, d=4)]
    result = run_slack(jobs)
    # folgas: A=9, B=0, C=2
    assert [j.id for j in result.jobs_order] == ["B", "C", "A"]


def test_lateness_and_finish_times_are_consistent():
    jobs = [Job(id="A", t=3, d=2), Job(id="B", t=2, d=10)]
    result = run_edf(jobs)
    first, second = result.jobs_order
    assert first.start == 0
    assert first.finish == first.start + 3 if first.id == "A" else True
    for sched_job, original in zip(result.jobs_order, sorted(jobs, key=lambda j: j.d)):
        assert sched_job.finish == sched_job.start + original.t
        assert sched_job.lateness == max(0, sched_job.finish - sched_job.deadline)
    assert result.max_lateness == max(j.lateness for j in result.jobs_order)
    assert result.total_time == result.jobs_order[-1].finish


def test_preset_1_breaks_sjf():
    jobs = PRESETS["Preset 1 — Quebra do SJF"]
    edf = run_edf(jobs)
    sjf = run_sjf(jobs)
    assert edf.max_lateness == 0
    assert sjf.max_lateness == 1
    assert edf.max_lateness < sjf.max_lateness


def test_preset_2_breaks_slack():
    jobs = PRESETS["Preset 2 — Quebra do Smallest Slack"]
    edf = run_edf(jobs)
    slack = run_slack(jobs)
    assert edf.max_lateness == 1
    assert slack.max_lateness == 9
    assert edf.max_lateness < slack.max_lateness


def test_preset_3_everyone_meets_deadline():
    jobs = PRESETS["Preset 3 — Cenário Ideal (todos no prazo)"]
    for result in run_all_heuristics(jobs).values():
        assert result.max_lateness == 0


def test_run_all_heuristics_keys():
    jobs = PRESETS["Preset 1 — Quebra do SJF"]
    results = run_all_heuristics(jobs)
    assert set(results.keys()) == {"EDF", "SJF", "Slack"}


def test_edf_is_never_worse_than_other_heuristics_on_random_instances():
    for seed in range(20):
        jobs = generate_random_jobs(n=8, duration_range=(1, 10), deadline_range=(5, 40), seed=seed)
        results = run_all_heuristics(jobs)
        edf_lateness = results["EDF"].max_lateness
        for name, result in results.items():
            assert edf_lateness <= result.max_lateness, (
                f"EDF perdeu para {name} na seed {seed}: "
                f"EDF={edf_lateness} {name}={result.max_lateness}"
            )


def test_generator_respects_ranges_and_seed_is_reproducible():
    jobs_a = generate_random_jobs(n=15, duration_range=(2, 6), deadline_range=(10, 20), seed=42)
    jobs_b = generate_random_jobs(n=15, duration_range=(2, 6), deadline_range=(10, 20), seed=42)
    assert jobs_a == jobs_b
    for job in jobs_a:
        assert 2 <= job.t <= 6
        assert 10 <= job.d <= 20
