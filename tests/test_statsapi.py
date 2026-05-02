from parkshift.statsapi import extract_play_metadata


def test_extract_play_metadata_returns_spray_coordinates() -> None:
    feed = {
        "gameData": {
            "teams": {
                "away": {"abbreviation": "BOS"},
                "home": {"abbreviation": "NYY"},
            }
        },
        "liveData": {
            "plays": {
                "allPlays": [
                    {
                        "about": {"isTopInning": False},
                        "result": {
                            "eventType": "home_run",
                            "description": "Batter homers on a fly ball to left field.",
                        },
                        "playEvents": [
                            {
                                "playId": "abc",
                                "hitData": {
                                    "launchSpeed": 110.9,
                                    "launchAngle": 42.0,
                                    "totalDistance": 394.0,
                                    "coordinates": {
                                        "coordX": 69.45,
                                        "coordY": 49.73,
                                    },
                                },
                            }
                        ],
                    }
                ]
            }
        }
    }

    metadata = extract_play_metadata(feed)

    assert metadata["abc"]["coord_x"] == 69.45
    assert metadata["abc"]["coord_y"] == 49.73
    assert round(metadata["abc"]["spray_angle_deg"], 1) == -20.6
    assert metadata["abc"]["distance_ft"] == 394
    assert metadata["abc"]["launch_angle"] == 42
    assert metadata["abc"]["exit_velocity"] == 110.9
    assert metadata["abc"]["event_type"] == "home_run"
    assert metadata["abc"]["batting_team"] == "NYY"
    assert metadata["abc"]["pitching_team"] == "BOS"
