from parkshift.models import BattedBall, ParkProfile, WallPoint
from parkshift.parks import load_parks
from parkshift.translator import (
    translate_ball_to_park,
    translate_ball_to_park_probability,
    translate_balls,
)


def test_ball_must_clear_wall_height() -> None:
    park = ParkProfile(
        name="Test Park",
        mlb_id="test",
        wall=(WallPoint(angle_deg=-45, distance_ft=300, height_ft=100), WallPoint(angle_deg=45, distance_ft=300, height_ft=100)),
    )
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="double",
        launch_speed=100,
        launch_angle=20,
        hc_x=125.42,
        hc_y=100,
        hit_distance_sc=390,
    )

    result = translate_ball_to_park(ball, park)

    assert not result.is_home_run
    assert result.ball_height_at_wall_ft is not None


def test_ball_over_wall_counts_as_home_run() -> None:
    park = ParkProfile(
        name="Test Park",
        mlb_id="test",
        wall=(WallPoint(angle_deg=-45, distance_ft=300, height_ft=8), WallPoint(angle_deg=45, distance_ft=300, height_ft=8)),
    )
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="double",
        launch_speed=100,
        launch_angle=28,
        hc_x=125.42,
        hc_y=100,
        hit_distance_sc=390,
    )

    result = translate_ball_to_park(ball, park)

    assert result.is_home_run


def test_probability_downweights_borderline_home_run() -> None:
    park = ParkProfile(
        name="Test Park",
        mlb_id="test",
        wall=(WallPoint(angle_deg=-45, distance_ft=390, height_ft=8), WallPoint(angle_deg=45, distance_ft=390, height_ft=8)),
    )
    borderline = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="double",
        launch_speed=100,
        launch_angle=28,
        hc_x=125.42,
        hc_y=100,
        hit_distance_sc=391,
    )
    crushed = BattedBall(
        row_id=2,
        player_name="Test Hitter",
        events="home_run",
        launch_speed=115,
        launch_angle=28,
        hc_x=125.42,
        hc_y=100,
        hit_distance_sc=450,
    )

    borderline_probability = translate_ball_to_park_probability(borderline, park)
    crushed_probability = translate_ball_to_park_probability(crushed, park)

    assert 0 < borderline_probability < 0.5
    assert crushed_probability > 0.9


def test_summary_includes_zero_home_run_parks() -> None:
    park = ParkProfile(
        name="Test Park",
        mlb_id="test",
        wall=(WallPoint(angle_deg=-45, distance_ft=450, height_ft=8), WallPoint(angle_deg=45, distance_ft=450, height_ft=8)),
    )
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="double",
        launch_speed=100,
        launch_angle=28,
        hc_x=125.42,
        hc_y=100,
        hit_distance_sc=390,
    )

    summary = translate_balls([ball], {"test": park})

    assert summary.park_home_runs == {"Test Park": 0}


def test_distance_tolerance_handles_wall_profile_uncertainty() -> None:
    park = ParkProfile(
        name="Test Park",
        mlb_id="test",
        wall=(WallPoint(angle_deg=-45, distance_ft=390, height_ft=8), WallPoint(angle_deg=45, distance_ft=390, height_ft=8)),
    )
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="home_run",
        launch_speed=105,
        launch_angle=32,
        hc_x=125.42,
        hc_y=100,
        hit_distance_sc=380,
    )

    strict_result = translate_ball_to_park(ball, park, distance_tolerance_ft=0)
    tolerant_result = translate_ball_to_park(ball, park, distance_tolerance_ft=15)

    assert not strict_result.is_home_run
    assert tolerant_result.is_home_run


def test_description_fallback_handles_missing_coordinates() -> None:
    park = ParkProfile(
        name="Test Park",
        mlb_id="test",
        wall=(WallPoint(angle_deg=-45, distance_ft=330, height_ft=8), WallPoint(angle_deg=45, distance_ft=330, height_ft=8)),
    )
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="home_run",
        launch_speed=110,
        launch_angle=28,
        hc_x=None,
        hc_y=None,
        hit_distance_sc=400,
        description="Test Hitter homers on a fly ball to left field.",
    )

    result = translate_ball_to_park(ball, park)

    assert result.is_home_run
    assert result.spray_angle_deg == -35.0


def test_long_left_field_homer_clears_every_bundled_park() -> None:
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="home_run",
        launch_speed=114.4,
        launch_angle=28,
        hc_x=None,
        hc_y=None,
        hit_distance_sc=433,
        description="Test Hitter homers on a fly ball to left field.",
    )

    failures = [
        park.name
        for park in load_parks().values()
        if not translate_ball_to_park(ball, park).is_home_run
    ]

    assert failures == []


def test_source_park_outcome_is_truth_when_requested() -> None:
    park = ParkProfile(
        name="Test Park",
        mlb_id="test",
        wall=(WallPoint(angle_deg=-45, distance_ft=300, height_ft=8), WallPoint(angle_deg=45, distance_ft=300, height_ft=8)),
    )
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="field_out",
        launch_speed=110,
        launch_angle=28,
        hc_x=125.42,
        hc_y=100,
        hit_distance_sc=420,
    )

    result = translate_ball_to_park(ball, park, source_park=park)

    assert not result.is_home_run


def test_source_park_outcome_is_truth_with_missing_geometry() -> None:
    park = ParkProfile(
        name="Test Park",
        mlb_id="test",
        wall=(WallPoint(angle_deg=-45, distance_ft=300, height_ft=8), WallPoint(angle_deg=45, distance_ft=300, height_ft=8)),
    )
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="home_run",
        launch_speed=None,
        launch_angle=None,
        hc_x=None,
        hc_y=None,
        hit_distance_sc=None,
    )

    result = translate_ball_to_park(ball, park, source_park=park)

    assert result.is_home_run


def test_inside_the_park_home_run_is_not_over_wall_home_run() -> None:
    park = ParkProfile(
        name="Test Park",
        mlb_id="test",
        wall=(WallPoint(angle_deg=-45, distance_ft=300, height_ft=8), WallPoint(angle_deg=45, distance_ft=300, height_ft=8)),
    )
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="home_run",
        launch_speed=86.5,
        launch_angle=21,
        hc_x=125.42,
        hc_y=100,
        hit_distance_sc=282,
        description="Test Hitter hits an inside-the-park home run.",
    )

    result = translate_ball_to_park(ball, park, source_park=park)

    assert not result.is_home_run


def test_actual_homer_gets_source_wall_carry_lower_bound() -> None:
    source_park = ParkProfile(
        name="Source Park",
        mlb_id="source",
        wall=(WallPoint(angle_deg=-45, distance_ft=400, height_ft=8), WallPoint(angle_deg=45, distance_ft=400, height_ft=8)),
    )
    target_park = ParkProfile(
        name="Target Park",
        mlb_id="target",
        wall=(WallPoint(angle_deg=-45, distance_ft=395, height_ft=8), WallPoint(angle_deg=45, distance_ft=395, height_ft=8)),
    )
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="home_run",
        launch_speed=108,
        launch_angle=32,
        hc_x=125.42,
        hc_y=100,
        hit_distance_sc=380,
    )

    without_source = translate_ball_to_park(ball, target_park)
    with_source = translate_ball_to_park(ball, target_park, source_park=source_park)

    assert not without_source.is_home_run
    assert with_source.is_home_run
