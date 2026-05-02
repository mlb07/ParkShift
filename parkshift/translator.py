from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from parkshift.distance import choose_carry_distance_ft, projectile_height_at_wall_ft
from parkshift.geometry import (
    clamp_spray_angle,
    is_fair_spray_angle,
    spray_angle_from_description,
    spray_angle_from_hc,
)
from parkshift.models import BallParkResult, BattedBall, ParkProfile
from parkshift.mlb import TEAM_HOME_PARK_ID
from parkshift.parks import load_parks, wall_distance_at_angle, wall_height_at_angle
from parkshift.probability import home_run_probability
from parkshift.statcast import actual_home_runs

DEFAULT_DISTANCE_TOLERANCE_FT = 0.0
DEFAULT_FOUL_LINE_TOLERANCE_DEG = 4.0


@dataclass(frozen=True)
class TranslationSummary:
    actual_home_runs: int
    batted_balls_checked: int
    rows_skipped: int
    park_home_runs: dict[str, int]
    park_expected_home_runs: dict[str, float] | None = None


def translate_ball_to_park(
    ball: BattedBall,
    park: ParkProfile,
    source_park: ParkProfile | None = None,
    distance_tolerance_ft: float = DEFAULT_DISTANCE_TOLERANCE_FT,
    foul_line_tolerance_deg: float = DEFAULT_FOUL_LINE_TOLERANCE_DEG,
    respect_source_outcome: bool = True,
) -> BallParkResult:
    spray_angle = spray_angle_for_ball(ball)
    carry_distance = effective_carry_distance_ft(
        ball,
        spray_angle,
        source_park,
    )
    if (
        respect_source_outcome
        and source_park is not None
        and source_park.mlb_id == park.mlb_id
        and ball.events is not None
    ):
        return BallParkResult(
            row_id=ball.row_id,
            park_name=park.name,
            is_home_run=is_over_wall_home_run(ball),
            spray_angle_deg=spray_angle,
            carry_distance_ft=carry_distance,
            wall_distance_ft=None,
            wall_height_ft=None,
            ball_height_at_wall_ft=None,
        )

    if (
        not is_fair_spray_angle(spray_angle, tolerance_deg=foul_line_tolerance_deg)
        or carry_distance is None
    ):
        return BallParkResult(
            row_id=ball.row_id,
            park_name=park.name,
            is_home_run=False,
            spray_angle_deg=spray_angle,
            carry_distance_ft=carry_distance,
            wall_distance_ft=None,
            wall_height_ft=None,
            ball_height_at_wall_ft=None,
        )

    park_angle = clamp_spray_angle(spray_angle)
    wall_distance = wall_distance_at_angle(park, park_angle)
    wall_height = wall_height_at_angle(park, park_angle)
    ball_height = projectile_height_at_wall_ft(
        ball.launch_speed,
        ball.launch_angle,
        wall_distance,
    )
    is_home_run = (
        ball_height is not None
        and carry_distance + distance_tolerance_ft >= wall_distance
        and ball_height >= wall_height
    )
    return BallParkResult(
        row_id=ball.row_id,
        park_name=park.name,
        is_home_run=is_home_run,
        spray_angle_deg=spray_angle,
        carry_distance_ft=carry_distance,
        wall_distance_ft=wall_distance,
        wall_height_ft=wall_height,
        ball_height_at_wall_ft=ball_height,
    )


def translate_balls(
    balls: Iterable[BattedBall],
    parks: dict[str, ParkProfile],
    distance_tolerance_ft: float = DEFAULT_DISTANCE_TOLERANCE_FT,
    foul_line_tolerance_deg: float = DEFAULT_FOUL_LINE_TOLERANCE_DEG,
) -> TranslationSummary:
    balls_list = list(balls)
    checked_rows = {
        ball.row_id
        for ball in balls_list
        if is_fair_spray_angle(
            spray_angle_for_ball(ball),
            tolerance_deg=foul_line_tolerance_deg,
        )
        and choose_carry_distance_ft(
            ball.hit_distance_sc, ball.launch_speed, ball.launch_angle
        )
        is not None
    }

    counts: Counter[str] = Counter({park.name: 0 for park in parks.values()})
    expected_counts: Counter[str] = Counter({park.name: 0.0 for park in parks.values()})
    source_lookup_parks = {**load_parks(), **parks}
    for ball in balls_list:
        source_park = source_park_for_ball(ball, source_lookup_parks)
        for park in parks.values():
            result = translate_ball_to_park(
                ball,
                park,
                source_park=source_park,
                distance_tolerance_ft=distance_tolerance_ft,
                foul_line_tolerance_deg=foul_line_tolerance_deg,
            )
            if result.is_home_run:
                counts[park.name] += 1
            expected_counts[park.name] += translate_ball_to_park_probability(
                ball,
                park,
                source_park=source_park,
                distance_tolerance_ft=distance_tolerance_ft,
                foul_line_tolerance_deg=foul_line_tolerance_deg,
            )

    return TranslationSummary(
        actual_home_runs=actual_home_runs(balls_list),
        batted_balls_checked=len(checked_rows),
        rows_skipped=len(balls_list) - len(checked_rows),
        park_home_runs=dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))),
        park_expected_home_runs=dict(
            sorted(expected_counts.items(), key=lambda item: (-item[1], item[0]))
        ),
    )


def summary_to_dataframe(summary: TranslationSummary) -> pd.DataFrame:
    rows = [
        {
            "park": park_name,
            "translated_hr": home_runs,
            "expected_hr": (
                None
                if summary.park_expected_home_runs is None
                else round(summary.park_expected_home_runs[park_name], 1)
            ),
        }
        for park_name, home_runs in summary.park_home_runs.items()
    ]
    return pd.DataFrame(rows)


def translate_ball_to_park_probability(
    ball: BattedBall,
    park: ParkProfile,
    source_park: ParkProfile | None = None,
    distance_tolerance_ft: float = DEFAULT_DISTANCE_TOLERANCE_FT,
    foul_line_tolerance_deg: float = DEFAULT_FOUL_LINE_TOLERANCE_DEG,
    respect_source_outcome: bool = True,
) -> float:
    if (
        respect_source_outcome
        and source_park is not None
        and source_park.mlb_id == park.mlb_id
        and ball.events is not None
    ):
        return 1.0 if is_over_wall_home_run(ball) else 0.0

    result = translate_ball_to_park(
        ball,
        park,
        source_park=source_park,
        distance_tolerance_ft=distance_tolerance_ft,
        foul_line_tolerance_deg=foul_line_tolerance_deg,
        respect_source_outcome=False,
    )
    return home_run_probability(result)


def spray_angle_for_ball(ball: BattedBall) -> float | None:
    coordinate_angle = spray_angle_from_hc(ball.hc_x, ball.hc_y)
    if coordinate_angle is not None:
        return coordinate_angle
    return spray_angle_from_description(ball.description)


def source_park_for_ball(
    ball: BattedBall, parks: dict[str, ParkProfile]
) -> ParkProfile | None:
    if ball.home_team is None:
        return None
    park_id = TEAM_HOME_PARK_ID.get(ball.home_team.upper())
    if park_id is None:
        return None
    return parks.get(park_id)


def effective_carry_distance_ft(
    ball: BattedBall,
    spray_angle_deg: float | None,
    source_park: ParkProfile | None = None,
) -> float | None:
    carry_distance = choose_carry_distance_ft(
        ball.hit_distance_sc,
        ball.launch_speed,
        ball.launch_angle,
    )
    if (
        carry_distance is None
        or not is_over_wall_home_run(ball)
        or source_park is None
        or not is_fair_spray_angle(spray_angle_deg, tolerance_deg=DEFAULT_FOUL_LINE_TOLERANCE_DEG)
    ):
        return carry_distance

    source_angle = clamp_spray_angle(spray_angle_deg)
    source_wall_distance = wall_distance_at_angle(source_park, source_angle)
    return max(carry_distance, source_wall_distance + 0.1)


def is_over_wall_home_run(ball: BattedBall) -> bool:
    if ball.events != "home_run":
        return False
    if ball.description and "inside-the-park" in ball.description.lower():
        return False
    return True
