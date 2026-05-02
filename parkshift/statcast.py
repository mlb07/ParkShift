from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from parkshift.models import BattedBall


STATCAST_COLUMNS = [
    "player_name",
    "batter",
    "events",
    "launch_speed",
    "launch_angle",
    "hc_x",
    "hc_y",
    "hit_distance",
    "hit_distance_sc",
    "game_year",
    "home_team",
    "away_team",
    "des",
    "bb_type",
    "stand",
]


def load_statcast_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def fetch_statcast_batter(
    mlbam_id: int, start_date: str, end_date: str
) -> pd.DataFrame:
    try:
        from pybaseball import statcast_batter
    except ImportError as exc:
        raise RuntimeError(
            "Fetching requires pybaseball. Install with: "
            'python -m pip install -e ".[fetch]"'
        ) from exc

    return statcast_batter(start_dt=start_date, end_dt=end_date, player_id=mlbam_id)


def filter_player(df: pd.DataFrame, player_name: str | None) -> pd.DataFrame:
    if not player_name:
        return df
    if "player_name" not in df.columns:
        raise ValueError("CSV does not include a player_name column.")
    return df[df["player_name"].astype(str).str.lower() == player_name.lower()].copy()


def filter_home_team(df: pd.DataFrame, home_team: str | None) -> pd.DataFrame:
    if not home_team:
        return df
    if "home_team" not in df.columns:
        raise ValueError("Data does not include a home_team column.")
    return df[df["home_team"].astype(str).str.upper() == home_team.upper()].copy()


def dataframe_to_batted_balls(df: pd.DataFrame) -> list[BattedBall]:
    balls: list[BattedBall] = []
    for row_id, row in df.reset_index(drop=True).iterrows():
        ball = BattedBall(
            row_id=int(row_id),
            player_name=_as_str(row, "player_name"),
            events=_as_str(row, "events"),
            launch_speed=_as_float(row, "launch_speed"),
            launch_angle=_as_float(row, "launch_angle"),
            hc_x=_as_float(row, "hc_x"),
            hc_y=_as_float(row, "hc_y"),
            hit_distance_sc=_first_float(row, ["hit_distance_sc", "hit_distance"]),
            game_year=_as_int(row, "game_year"),
            home_team=_as_str(row, "home_team"),
            away_team=_as_str(row, "away_team"),
            description=_as_str(row, "des"),
            bb_type=_as_str(row, "bb_type"),
            stand=_as_str(row, "stand"),
        )
        balls.append(ball)
    return balls


def actual_home_runs(balls: Iterable[BattedBall]) -> int:
    return sum(1 for ball in balls if ball.events == "home_run")


def _as_float(row: pd.Series, column: str) -> float | None:
    if column not in row:
        return None
    value = row[column]
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_float(row: pd.Series, columns: list[str]) -> float | None:
    for column in columns:
        value = _as_float(row, column)
        if value is not None:
            return value
    return None


def _as_int(row: pd.Series, column: str) -> int | None:
    value = _as_float(row, column)
    if value is None:
        return None
    return int(value)


def _as_str(row: pd.Series, column: str) -> str | None:
    if column not in row:
        return None
    value = row[column]
    if pd.isna(value):
        return None
    return str(value)
