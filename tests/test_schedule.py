from parkshift.schedule import game_context_by_pk


def test_game_context_by_pk_maps_mlb_venue_to_savant_code() -> None:
    schedule = {
        "dates": [
            {
                "games": [
                    {
                        "gamePk": 1,
                        "gameType": "R",
                        "teams": {
                            "home": {"team": {"id": 147}},
                            "away": {"team": {"id": 111}},
                        },
                        "venue": {"id": 3313, "name": "Yankee Stadium"},
                    }
                ]
            }
        ]
    }

    games = game_context_by_pk(schedule)

    assert games["1"].home_team == "NYY"
    assert games["1"].away_team == "BOS"
    assert games["1"].savant_park_code == "nyy"


def test_game_context_by_pk_marks_neutral_site_as_unmapped() -> None:
    schedule = {
        "dates": [
            {
                "games": [
                    {
                        "gamePk": 1,
                        "gameType": "R",
                        "teams": {
                            "home": {"team": {"id": 119}},
                            "away": {"team": {"id": 135}},
                        },
                        "venue": {"id": 5150, "name": "Gocheok Sky Dome"},
                    }
                ]
            }
        ]
    }

    games = game_context_by_pk(schedule)

    assert games["1"].savant_park_code is None

