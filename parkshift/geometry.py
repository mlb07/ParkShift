from __future__ import annotations

import math
import re

SAVANT_HOME_X = 125.42
SAVANT_HOME_Y = 198.27
LEFT_FIELD_LINE_DEG = -45.0
RIGHT_FIELD_LINE_DEG = 45.0


def spray_angle_from_hc(hc_x: float | None, hc_y: float | None) -> float | None:
    """Convert Baseball Savant hit coordinates to approximate spray angle.

    The returned angle is centered at 0 degrees for straightaway center field,
    with negative angles toward left field and positive angles toward right.
    """
    if hc_x is None or hc_y is None:
        return None
    if not math.isfinite(hc_x) or not math.isfinite(hc_y):
        return None

    return math.degrees(math.atan2(hc_x - SAVANT_HOME_X, SAVANT_HOME_Y - hc_y))


def spray_angle_from_description(description: str | None) -> float | None:
    """Infer a coarse spray angle from Statcast's play description.

    This is only a fallback for rows where Baseball Savant omits `hc_x/hc_y`.
    The values are intentionally conservative buckets, not precise locations.
    """
    if not description:
        return None

    text = description.lower()
    text = re.sub(r"\\s+", " ", text)
    if "left-center field" in text or "left center field" in text:
        return -22.5
    if "right-center field" in text or "right center field" in text:
        return 22.5
    if "left field" in text:
        return -35.0
    if "right field" in text:
        return 35.0
    if "center field" in text:
        return 0.0
    return None


def is_fair_spray_angle(angle_deg: float | None, tolerance_deg: float = 0.0) -> bool:
    if angle_deg is None:
        return False
    return (
        LEFT_FIELD_LINE_DEG - tolerance_deg
        <= angle_deg
        <= RIGHT_FIELD_LINE_DEG + tolerance_deg
    )


def clamp_spray_angle(angle_deg: float) -> float:
    return max(LEFT_FIELD_LINE_DEG, min(RIGHT_FIELD_LINE_DEG, angle_deg))


def interpolate_by_angle(angle_deg: float, points: list[tuple[float, float]]) -> float:
    """Linearly interpolate a value from sorted angle/value points."""
    if not points:
        raise ValueError("At least one interpolation point is required.")

    sorted_points = sorted(points, key=lambda item: item[0])
    if angle_deg <= sorted_points[0][0]:
        return sorted_points[0][1]
    if angle_deg >= sorted_points[-1][0]:
        return sorted_points[-1][1]

    for (left_angle, left_value), (right_angle, right_value) in zip(
        sorted_points, sorted_points[1:]
    ):
        if left_angle <= angle_deg <= right_angle:
            span = right_angle - left_angle
            if span == 0:
                return left_value
            weight = (angle_deg - left_angle) / span
            return left_value + weight * (right_value - left_value)

    return sorted_points[-1][1]
