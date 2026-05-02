from __future__ import annotations

import math

from parkshift.models import BallParkResult


DISTANCE_MIDPOINT_FT = 4.0
DISTANCE_SCALE_FT = 4.0
HEIGHT_MIDPOINT_FT = 1.0
HEIGHT_SCALE_FT = 3.0


def home_run_probability(result: BallParkResult) -> float:
    """Estimate HR probability from wall-clearance margins.

    This is a calibration layer over the deterministic geometry engine. It
    treats public Statcast distance and hit coordinates as noisy near the wall,
    so a ball clearing by inches is not equivalent to a ball clearing by 40 ft.
    """
    if (
        result.carry_distance_ft is None
        or result.wall_distance_ft is None
        or result.ball_height_at_wall_ft is None
        or result.wall_height_ft is None
    ):
        return 0.0

    distance_margin = result.carry_distance_ft - result.wall_distance_ft
    height_margin = result.ball_height_at_wall_ft - result.wall_height_ft
    distance_score = sigmoid((distance_margin - DISTANCE_MIDPOINT_FT) / DISTANCE_SCALE_FT)
    height_score = sigmoid((height_margin - HEIGHT_MIDPOINT_FT) / HEIGHT_SCALE_FT)
    return max(0.0, min(1.0, distance_score * height_score))


def sigmoid(value: float) -> float:
    if value >= 50:
        return 1.0
    if value <= -50:
        return 0.0
    return 1.0 / (1.0 + math.exp(-value))
