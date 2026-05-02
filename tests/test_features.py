from parkshift.features import FEATURE_COLUMNS, build_labeled_feature_row
from parkshift.models import BattedBall, ParkProfile, WallPoint


def test_build_labeled_feature_row() -> None:
    park = ParkProfile(
        name="Test Park",
        mlb_id="test",
        wall=(
            WallPoint(angle_deg=-45, distance_ft=330, height_ft=8),
            WallPoint(angle_deg=45, distance_ft=330, height_ft=8),
        ),
    )
    ball = BattedBall(
        row_id=1,
        player_name="Test Hitter",
        events="home_run",
        launch_speed=105,
        launch_angle=28,
        hc_x=125.42,
        hc_y=100,
        hit_distance_sc=400,
        bb_type="fly_ball",
        stand="R",
    )

    row = build_labeled_feature_row(ball, park)

    assert row is not None
    assert set(FEATURE_COLUMNS).issubset(row)
    assert row["label"] == 1.0
    assert row["distance_margin"] == 70
