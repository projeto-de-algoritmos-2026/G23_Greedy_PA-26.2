"""Instâncias fixas que demonstram onde SJF e Smallest Slack falham e EDF acerta.

Contrato fixado com o Integrante B via engine.py: dicionário PRESETS.
"""

from typing import Dict, List

from models import Job

PRESETS: Dict[str, List[Job]] = {
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
