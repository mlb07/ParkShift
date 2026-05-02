from __future__ import annotations

import json
from importlib import resources

from parkshift.identity import HomeParkIdentity, calculate_home_park_identity
from parkshift.schedule import game_context_by_pk


DEMO_NAMES = ("judge-2024",)


def load_demo_identity(name: str = "judge-2024") -> HomeParkIdentity:
    if name != "judge-2024":
        raise ValueError(f"Unknown demo: {name}. Available demos: {', '.join(DEMO_NAMES)}")
    examples = resources.files("parkshift.examples")
    details = json.loads(examples.joinpath("judge_2024_details.json").read_text())
    schedule = json.loads(examples.joinpath("judge_2024_schedule.json").read_text())
    return calculate_home_park_identity(
        details,
        game_context_by_pk(schedule),
    )
