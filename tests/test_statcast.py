import pandas as pd

from parkshift.statcast import dataframe_to_batted_balls, filter_home_team


def test_filter_home_team_is_case_insensitive() -> None:
    df = pd.DataFrame(
        {
            "home_team": ["NYY", "bos", "NYY"],
            "events": ["home_run", "double", "single"],
        }
    )

    filtered = filter_home_team(df, "nyy")

    assert filtered["events"].tolist() == ["home_run", "single"]


def test_dataframe_to_batted_balls_accepts_hit_distance_alias() -> None:
    df = pd.DataFrame(
        {
            "player_name": ["Test Hitter"],
            "events": ["home_run"],
            "launch_speed": [100],
            "launch_angle": [25],
            "hc_x": [125],
            "hc_y": [100],
            "hit_distance": [401],
        }
    )

    [ball] = dataframe_to_batted_balls(df)

    assert ball.hit_distance_sc == 401
