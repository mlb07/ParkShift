from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WallPoint:
    angle_deg: float
    distance_ft: float
    height_ft: float


@dataclass(frozen=True)
class ParkProfile:
    name: str
    mlb_id: str
    wall: tuple[WallPoint, ...]


@dataclass(frozen=True)
class BattedBall:
    row_id: int
    player_name: str | None
    events: str | None
    launch_speed: float | None
    launch_angle: float | None
    hc_x: float | None
    hc_y: float | None
    hit_distance_sc: float | None
    game_year: int | None = None
    home_team: str | None = None
    away_team: str | None = None
    description: str | None = None
    bb_type: str | None = None
    stand: str | None = None


@dataclass(frozen=True)
class BallParkResult:
    row_id: int
    park_name: str
    is_home_run: bool
    spray_angle_deg: float | None
    carry_distance_ft: float | None
    wall_distance_ft: float | None
    wall_height_ft: float | None
    ball_height_at_wall_ft: float | None
