from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Job:
    id: str
    t: int  # duração (processing time)
    d: int  # deadline


@dataclass
class ScheduledJob:
    id: str
    start: int
    finish: int
    deadline: int
    lateness: int


@dataclass
class ScheduleResult:
    algorithm_name: str
    jobs_order: List[ScheduledJob]
    max_lateness: int
    total_time: int


ScheduleResults = Dict[str, ScheduleResult]
