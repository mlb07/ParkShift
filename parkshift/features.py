from __future__ import annotations

import math

from parkshift.distance import choose_carry_distance_ft, projectile_height_at_wall_ft
from parkshift.geometry import clamp_spray_angle, is_fair_spray_angle
from parkshift.models import BattedBall, ParkProfile
from parkshift.parks import wall_distance_at_angle, wall_height_at_angle
from parkshift.translator import is_over_wall_home_run, spray_angle_for_ball


FEATURE_COLUMNS = [
    "launch_speed",
    "launch_angle",
    "carry_distance",
    "spray_angle",
    "abs_spray_angle",
    "wall_distance",
    "wall_height",
    "distance_margin",
    "ball_height_at_wall",
    "height_margin",
    "is_pull_side",
    "is_center_third",
    "bb_type_fly_ball",
    "bb_type_line_drive",
    "bb_type_popup",
]


def build_feature_row(ball: BattedBall, park: ParkProfile) -> dict[str, float] | None:
    spray_angle = spray_angle_for_ball(ball)
    carry_distance = choose_carry_distance_ft(
        ball.hit_distance_sc,
        ball.launch_speed,
        ball.launch_angle,
    )
    if (
        spray_angle is None
        or carry_distance is None
        or ball.launch_speed is None
        or ball.launch_angle is None
        or not is_fair_spray_angle(spray_angle, tolerance_deg=4.0)
    ):
        return None

    park_angle = clamp_spray_angle(spray_angle)
    wall_distance = wall_distance_at_angle(park, park_angle)
    wall_height = wall_height_at_angle(park, park_angle)
    ball_height = projectile_height_at_wall_ft(
        ball.launch_speed,
        ball.launch_angle,
        wall_distance,
    )
    if ball_height is None:
        return None

    return {
        "launch_speed": ball.launch_speed,
        "launch_angle": ball.launch_angle,
        "carry_distance": carry_distance,
        "spray_angle": spray_angle,
        "abs_spray_angle": abs(spray_angle),
        "wall_distance": wall_distance,
        "wall_height": wall_height,
        "distance_margin": carry_distance - wall_distance,
        "ball_height_at_wall": ball_height,
        "height_margin": ball_height - wall_height,
        "is_pull_side": float(is_pull_side(ball, spray_angle)),
        "is_center_third": float(abs(spray_angle) <= 15),
        "bb_type_fly_ball": float(ball.bb_type == "fly_ball"),
        "bb_type_line_drive": float(ball.bb_type == "line_drive"),
        "bb_type_popup": float(ball.bb_type == "popup"),
    }


def build_labeled_feature_row(
    ball: BattedBall, source_park: ParkProfile
) -> dict[str, float] | None:
    row = build_feature_row(ball, source_park)
    if row is None:
        return None
    row["label"] = float(is_over_wall_home_run(ball))
    return row


def is_pull_side(ball: BattedBall, spray_angle: float) -> bool:
    if ball.stand == "L":
        return spray_angle > 0
    if ball.stand == "R":
        return spray_angle < 0
    return False


def feature_vector(row: dict[str, float]) -> list[float]:
    return [safe_float(row[column]) for column in FEATURE_COLUMNS]


def safe_float(value: float | int | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, float) and not math.isfinite(value):
        return 0.0
    return float(value)
