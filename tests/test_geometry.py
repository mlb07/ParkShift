from parkshift.geometry import (
    clamp_spray_angle,
    interpolate_by_angle,
    is_fair_spray_angle,
    spray_angle_from_description,
)


def test_interpolate_by_angle_midpoint() -> None:
    assert interpolate_by_angle(0, [(-45, 300), (45, 400)]) == 350


def test_fair_spray_angle_bounds() -> None:
    assert is_fair_spray_angle(-45)
    assert is_fair_spray_angle(45)
    assert not is_fair_spray_angle(-46)
    assert is_fair_spray_angle(-46, tolerance_deg=1)
    assert not is_fair_spray_angle(None)


def test_clamp_spray_angle_to_fair_territory() -> None:
    assert clamp_spray_angle(-50) == -45
    assert clamp_spray_angle(50) == 45
    assert clamp_spray_angle(10) == 10


def test_spray_angle_from_description() -> None:
    assert spray_angle_from_description("Aaron Judge homers on a fly ball to left field.") == -35.0
    assert spray_angle_from_description("Doubles on a fly ball to right-center field.") == 22.5
    assert spray_angle_from_description("Singles on a ground ball.") is None
