from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

SOURCE_URL = (
    "https://raw.githubusercontent.com/bdilday/GeomMLBStadiums/main/"
    "inst/extdata/mlb_stadia_paths.csv"
)
MLBAM_SCALE_FT = 2.495671
HOME_X = 125.0
HOME_Y = 199.0

TEAM_TO_PARK = {
    "angels": ("angel", "Angel Stadium"),
    "astros": ("minute_maid", "Minute Maid Park"),
    "athletics": ("oakland_coliseum", "Oakland Coliseum"),
    "blue_jays": ("rogers_centre", "Rogers Centre"),
    "braves": ("truist", "Truist Park"),
    "brewers": ("american_family", "American Family Field"),
    "cardinals": ("busch", "Busch Stadium"),
    "cubs": ("wrigley", "Wrigley Field"),
    "diamondbacks": ("chase", "Chase Field"),
    "dodgers": ("dodger", "Dodger Stadium"),
    "giants": ("oracle", "Oracle Park"),
    "guardians": ("progressive", "Progressive Field"),
    "mariners": ("t_mobile", "T-Mobile Park"),
    "marlins": ("loan_depot", "loanDepot park"),
    "mets": ("citi", "Citi Field"),
    "nationals": ("nationals", "Nationals Park"),
    "orioles": ("camden", "Oriole Park at Camden Yards"),
    "padres": ("petco", "Petco Park"),
    "phillies": ("citizens_bank", "Citizens Bank Park"),
    "pirates": ("pnc", "PNC Park"),
    "rangers": ("globe_life", "Globe Life Field"),
    "rays": ("tropicana", "Tropicana Field"),
    "red_sox": ("fenway", "Fenway Park"),
    "reds": ("great_american", "Great American Ball Park"),
    "rockies": ("coors", "Coors Field"),
    "royals": ("kauffman", "Kauffman Stadium"),
    "tigers": ("comerica", "Comerica Park"),
    "twins": ("target", "Target Field"),
    "white_sox": ("guaranteed_rate", "Guaranteed Rate Field"),
    "yankees": ("yankee", "Yankee Stadium"),
}

# Wall-height profiles are intentionally separated from wall distance. The
# distance profiles come from MLBAM stadium geometry; the public geometry source
# does not include wall height, so these are editable park metadata.
HEIGHT_PROFILES = {
    "fenway": [(-45, 37), (-25, 37), (-10, 17), (15, 5), (45, 3)],
    "minute_maid": [(-45, 19), (-25, 19), (0, 10), (25, 7), (45, 7)],
    "oracle": [(-45, 8), (-10, 8), (30, 8), (45, 24)],
    "great_american": [(-45, 12), (0, 8), (45, 8)],
    "camden": [(-45, 7), (-20, 13), (15, 7), (45, 21)],
    "wrigley": [(-45, 11.5), (45, 11.5)],
    "pnc": [(-45, 6), (45, 21)],
    "progressive": [(-45, 19), (-15, 9), (45, 9)],
    "comerica": [(-45, 8.5), (45, 8.5)],
}
DEFAULT_HEIGHT_PROFILE = [(-45, 8), (45, 8)]

# Published marker dimensions. Angles are conventional: foul poles at +/-45,
# center at 0, and power alleys at +/-22.5. ESPN notes that team-provided LCF
# and RCF markers are not guaranteed to represent the exact same physical angle
# in every park, so these are calibration anchors rather than a replacement for
# the MLBAM wall path.
MARKER_PROFILES = {
    "angel": [(-45, 330, 8), (-22.5, 387, 8), (0, 400, 8), (22.5, 370, 18), (45, 330, 18)],
    "american_family": [(-45, 344, 8), (-22.5, 370, 8), (0, 400, 8), (22.5, 374, 8), (45, 345, 6)],
    "busch": [(-45, 336, 8), (-22.5, 375, 8), (0, 400, 8), (22.5, 375, 8), (45, 335, 8)],
    "camden": [(-45, 333, 7), (-22.5, 364, 7), (0, 410, 7), (22.5, 373, 7), (45, 318, 25)],
    "chase": [(-45, 330, 7.5), (-22.5, 376, 7.5), (0, 407, 25), (22.5, 376, 7.5), (45, 335, 7.5)],
    "citi": [(-45, 335, 8), (-22.5, 385, 8), (0, 408, 8), (22.5, 375, 8), (45, 330, 8)],
    "citizens_bank": [(-45, 329, 10), (-22.5, 360, 11), (0, 401, 6), (22.5, 357, 13), (45, 330, 13)],
    "coors": [(-45, 347, 8), (-22.5, 390, 8), (0, 415, 8), (22.5, 375, 8), (45, 350, 14)],
    "comerica": [(-45, 345, 7), (-22.5, 370, 9), (0, 420, 8), (22.5, 388, 12), (45, 330, 8)],
    "dodger": [(-45, 330, 4), (-22.5, 375, 8), (0, 400, 8), (22.5, 375, 8), (45, 330, 4)],
    "fenway": [(-45, 310, 37), (-22.5, 335, 37), (0, 420, 17), (22.5, 380, 5), (45, 302, 3)],
    "globe_life": [(-45, 332, 14), (-22.5, 380, 8), (0, 400, 8), (22.5, 377, 8), (45, 325, 8)],
    "great_american": [(-45, 328, 12), (-22.5, 379, 12), (0, 404, 8), (22.5, 370, 8), (45, 325, 8)],
    "guaranteed_rate": [(-45, 330, 8), (-22.5, 377, 8), (0, 400, 8), (22.5, 372, 8), (45, 335, 8)],
    "kauffman": [(-45, 330, 8), (-22.5, 387, 8), (0, 410, 8), (22.5, 387, 8), (45, 330, 8)],
    "loan_depot": [(-45, 344, 10), (-22.5, 386, 10), (0, 418, 16), (22.5, 392, 10), (45, 335, 10)],
    "minute_maid": [(-45, 315, 19), (-22.5, 362, 25), (0, 435, 10), (22.5, 373, 10), (45, 326, 7)],
    "nationals": [(-45, 336, 8), (-22.5, 377, 8), (0, 402, 8), (22.5, 370, 12), (45, 335, 8)],
    "oakland_coliseum": [(-45, 330, 8), (-22.5, 362, 15), (0, 400, 8), (22.5, 362, 15), (45, 330, 8)],
    "oracle": [(-45, 339, 6), (-22.5, 364, 6), (0, 399, 10.5), (22.5, 421, 21), (45, 309, 21)],
    "petco": [(-45, 336, 8), (-22.5, 383, 8), (0, 396, 8), (22.5, 402, 10), (45, 322, 8)],
    "pnc": [(-45, 325, 8), (-22.5, 389, 8), (0, 399, 11), (22.5, 375, 25), (45, 320, 25)],
    "progressive": [(-45, 325, 19), (-22.5, 370, 19), (0, 405, 9), (22.5, 375, 9), (45, 325, 9)],
    "rogers_centre": [(-45, 328, 10), (-22.5, 375, 10), (0, 400, 10), (22.5, 375, 10), (45, 328, 10)],
    "t_mobile": [(-45, 331, 17), (-22.5, 390, 8), (0, 405, 8), (22.5, 385, 8), (45, 326, 8)],
    "target": [(-45, 339, 8), (-22.5, 377, 8), (0, 404, 8), (22.5, 367, 23), (45, 328, 23)],
    "tropicana": [(-45, 315, 11), (-22.5, 370, 11), (0, 404, 9), (22.5, 370, 11), (45, 322, 11)],
    "wrigley": [(-45, 355, 15), (-22.5, 368, 11.5), (0, 400, 11.5), (22.5, 368, 11.5), (45, 353, 15)],
    "yankee": [(-45, 318, 8), (-22.5, 399, 8), (0, 408, 8), (22.5, 385, 8), (45, 314, 8)],
}


def main() -> None:
    raw = pd.read_csv(SOURCE_URL)
    parks = {}
    for geom_team, (park_id, park_name) in TEAM_TO_PARK.items():
        points = wall_points_for_team(raw, geom_team)
        profile = []
        for angle in range(-45, 46):
            distance = ray_wall_distance(points, angle)
            if distance is None:
                raise RuntimeError(f"No wall intersection for {park_id} at {angle} degrees")
            calibrated_distance = calibrate_distance(park_id, angle, distance, points)
            profile.append(
                {
                    "angle_deg": angle,
                    "distance_ft": round(calibrated_distance, 1),
                    "height_ft": round(height_at_angle(park_id, angle), 1),
                }
            )

        parks[park_id] = {
            "name": park_name,
            "source": (
                "GeomMLBStadiums MLBAM stadium path data, calibrated to "
                "published LF/LCF/CF/RCF/RF markers where available"
            ),
            "wall": profile,
        }

    output_path = Path("parkshift/data/parks.json")
    output_path.write_text(json.dumps(parks, indent=2) + "\n")


def wall_points_for_team(raw: pd.DataFrame, geom_team: str) -> list[tuple[float, float]]:
    stadium = raw[(raw["team"] == geom_team) & (raw["segment"] == "outfield_outer")]
    points = [
        (MLBAM_SCALE_FT * (row.x - HOME_X), MLBAM_SCALE_FT * (HOME_Y - row.y))
        for row in stadium.itertuples(index=False)
    ]
    if len(points) < 2:
        raise RuntimeError(f"No outfield wall path found for {geom_team}")
    return points


def ray_wall_distance(points: list[tuple[float, float]], angle_deg: int) -> float | None:
    theta = math.radians(angle_deg)
    hits = []
    for point_a, point_b in zip(points, points[1:] + points[:1]):
        distance = ray_segment_intersection(theta, point_a, point_b)
        if distance is not None and distance > 250:
            hits.append(distance)
    return min(hits) if hits else None


def ray_segment_intersection(
    theta: float, point_a: tuple[float, float], point_b: tuple[float, float]
) -> float | None:
    ray_dx = math.sin(theta)
    ray_dy = math.cos(theta)
    x1, y1 = point_a
    seg_dx = point_b[0] - x1
    seg_dy = point_b[1] - y1
    determinant = seg_dx * ray_dy - ray_dx * seg_dy
    if abs(determinant) < 1e-9:
        return None

    ray_distance = (-x1 * seg_dy + seg_dx * y1) / determinant
    segment_position = (ray_dx * y1 - x1 * ray_dy) / determinant
    if ray_distance >= 0 and -1e-6 <= segment_position <= 1 + 1e-6:
        return ray_distance
    return None


def height_at_angle(park_id: str, angle_deg: int) -> float:
    marker_points = MARKER_PROFILES.get(park_id)
    if marker_points is not None:
        points = [(angle, height) for angle, _distance, height in marker_points]
    else:
        points = HEIGHT_PROFILES.get(park_id, DEFAULT_HEIGHT_PROFILE)
    return interpolate(angle_deg, points)


def calibrate_distance(
    park_id: str,
    angle_deg: int,
    raw_distance: float,
    raw_points: list[tuple[float, float]],
) -> float:
    marker_points = MARKER_PROFILES.get(park_id)
    if marker_points is None:
        return raw_distance

    correction_points = []
    for marker_angle, marker_distance, _height in marker_points:
        raw_marker_distance = ray_wall_distance(raw_points, marker_angle)
        if raw_marker_distance is not None:
            correction_points.append((marker_angle, marker_distance - raw_marker_distance))

    if not correction_points:
        return raw_distance
    return raw_distance + interpolate(angle_deg, correction_points)


def interpolate(angle_deg: float, points: list[tuple[float, float]]) -> float:
    if angle_deg <= points[0][0]:
        return points[0][1]
    if angle_deg >= points[-1][0]:
        return points[-1][1]

    for (left_angle, left_value), (right_angle, right_value) in zip(
        points, points[1:]
    ):
        if left_angle <= angle_deg <= right_angle:
            span = right_angle - left_angle
            weight = (angle_deg - left_angle) / span
            return left_value + weight * (right_value - left_value)
    return points[-1][1]


if __name__ == "__main__":
    main()
