from __future__ import annotations

import json
from importlib import resources

from parkshift.geometry import interpolate_by_angle
from parkshift.models import ParkProfile, WallPoint


def load_parks() -> dict[str, ParkProfile]:
    with resources.files("parkshift.data").joinpath("parks.json").open() as file:
        raw_parks = json.load(file)

    parks: dict[str, ParkProfile] = {}
    for park_id, raw in raw_parks.items():
        wall = tuple(
            WallPoint(
                angle_deg=float(point["angle_deg"]),
                distance_ft=float(point["distance_ft"]),
                height_ft=float(point["height_ft"]),
            )
            for point in raw["wall"]
        )
        parks[park_id] = ParkProfile(
            name=str(raw["name"]),
            mlb_id=park_id,
            wall=wall,
        )
    return parks


def wall_distance_at_angle(park: ParkProfile, angle_deg: float) -> float:
    return interpolate_by_angle(
        angle_deg,
        [(point.angle_deg, point.distance_ft) for point in park.wall],
    )


def wall_height_at_angle(park: ParkProfile, angle_deg: float) -> float:
    return interpolate_by_angle(
        angle_deg,
        [(point.angle_deg, point.height_ft) for point in park.wall],
    )
