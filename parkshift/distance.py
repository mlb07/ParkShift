from __future__ import annotations

import math

CONTACT_HEIGHT_FT = 3.0
MPH_TO_FTPS = 1.46667
GRAVITY_FTPS2 = 32.174


def valid_positive(value: float | None) -> bool:
    return value is not None and math.isfinite(value) and value > 0


def estimate_carry_distance_ft(
    launch_speed_mph: float | None, launch_angle_deg: float | None
) -> float | None:
    """Fallback carry estimate when Statcast projected distance is missing.

    This deliberately stays simple for the MVP. It is only a fallback; when
    `hit_distance_sc` exists, that projected distance is preferred.
    """
    if launch_speed_mph is None or launch_angle_deg is None:
        return None
    if not math.isfinite(launch_speed_mph) or not math.isfinite(launch_angle_deg):
        return None

    distance = (
        3.0 * launch_speed_mph
        + 5.0 * launch_angle_deg
        - 0.095 * launch_angle_deg * launch_angle_deg
    )
    return max(0.0, min(500.0, distance))


def choose_carry_distance_ft(
    hit_distance_sc: float | None,
    launch_speed_mph: float | None,
    launch_angle_deg: float | None,
) -> float | None:
    if valid_positive(hit_distance_sc):
        return hit_distance_sc
    return estimate_carry_distance_ft(launch_speed_mph, launch_angle_deg)


def height_at_wall_ft(
    carry_distance_ft: float | None,
    launch_angle_deg: float | None,
    wall_distance_ft: float,
    contact_height_ft: float = CONTACT_HEIGHT_FT,
) -> float | None:
    """Estimate batted-ball height at the wall using a constrained parabola.

    The curve starts at contact height with the measured launch angle and
    reaches ground level at the projected carry distance.
    """
    if carry_distance_ft is None or launch_angle_deg is None:
        return None
    if not math.isfinite(carry_distance_ft) or not math.isfinite(launch_angle_deg):
        return None
    if carry_distance_ft <= 0:
        return None

    theta = math.radians(max(-89.0, min(89.0, launch_angle_deg)))
    launch_slope = math.tan(theta)
    curve = (contact_height_ft + carry_distance_ft * launch_slope) / (
        carry_distance_ft * carry_distance_ft
    )
    height = contact_height_ft + wall_distance_ft * launch_slope - curve * (
        wall_distance_ft * wall_distance_ft
    )
    return height


def projectile_height_at_wall_ft(
    launch_speed_mph: float | None,
    launch_angle_deg: float | None,
    wall_distance_ft: float,
    contact_height_ft: float = CONTACT_HEIGHT_FT,
) -> float | None:
    """Estimate wall-crossing height from exit velocity and launch angle.

    This is intentionally simple and ignores drag. The engine still uses
    Statcast projected distance as the carry-distance gate, so this function's
    job is only to reject balls whose initial trajectory is clearly too low for
    a wall.
    """
    if launch_speed_mph is None or launch_angle_deg is None:
        return None
    if not math.isfinite(launch_speed_mph) or not math.isfinite(launch_angle_deg):
        return None
    if launch_speed_mph <= 0:
        return None

    velocity_ftps = launch_speed_mph * MPH_TO_FTPS
    theta = math.radians(max(-89.0, min(89.0, launch_angle_deg)))
    horizontal_velocity = velocity_ftps * math.cos(theta)
    if horizontal_velocity <= 0:
        return None

    return (
        contact_height_ft
        + wall_distance_ft * math.tan(theta)
        - GRAVITY_FTPS2
        * wall_distance_ft
        * wall_distance_ft
        / (2 * horizontal_velocity * horizontal_velocity)
    )
