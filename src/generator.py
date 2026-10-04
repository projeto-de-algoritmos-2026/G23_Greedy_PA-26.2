"""Gerador de instâncias aleatórias de tarefas para a UI do Integrante B.

Contrato fixado com o Integrante B via engine.py: generate_random_jobs.
"""

import random
from typing import List, Tuple

from models import Job


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
