from parkshift.validation import validate_home_park_identities, validation_summary


def test_validate_home_park_identities_reports_pass_and_no_rows() -> None:
    leaderboard = [
        {"player_id": "1", "player": "Judge, Aaron", "team_abbrev": "NYY"},
        {"player_id": "2", "player": "Wrong, Team", "team_abbrev": "BOS"},
    ]
    details = {
        "1": [_row("1", "home_run", nyy="1")],
        "2": [_row("1", "home_run", nyy="1")],
    }
    schedule = _schedule()

    results = validate_home_park_identities(leaderboard, details, schedule)

    assert results[0].status == "PASS"
    assert results[0].actual_home_hr == 1
    assert results[0].source_park_hr == 1
    assert results[1].status == "NO_HOME_ROWS"


def test_validate_home_park_identities_reports_missing_details() -> None:
    leaderboard = [{"player_id": "1", "player": "Judge, Aaron", "team_abbrev": "NYY"}]

    [result] = validate_home_park_identities(leaderboard, {}, _schedule())

    assert result.status == "MISSING_DETAILS"


def test_validation_summary_counts_checked_results() -> None:
    leaderboard = [{"player_id": "1", "player": "Judge, Aaron", "team_abbrev": "NYY"}]
    details = {"1": [_row("1", "home_run", nyy="1")]}

    results = validate_home_park_identities(leaderboard, details, _schedule())
    summary = validation_summary(results)

    assert summary["players"] == 1
    assert summary["checked"] == 1
    assert summary["status_counts"] == {"PASS": 1}
    assert summary["total_diff"] == 0


def test_validate_home_park_identities_can_infer_traded_player_source_teams() -> None:
    leaderboard = [{"player_id": "1", "player": "Traded, Player", "team_abbrev": "NYY"}]
    details = {
        "1": [
            _row("1", "home_run", team_abbrev="MIA", mia="1", nyy="0", hou="1"),
            _row("2", "field_out", team_abbrev="NYY", mia="0", nyy="0", hou="1"),
        ]
    }

    [result] = validate_home_park_identities(
        leaderboard,
        details,
        _traded_schedule(),
    )

    assert result.status == "PASS"
    assert result.source_team == "MIA,NYY"
    assert result.home_hr_candidate_batted_balls == 2
    assert result.actual_home_hr == 1
    assert result.source_park_hr == 1


def test_validate_home_park_identities_accepts_multi_team_override() -> None:
    leaderboard = [{"player_id": "1", "player": "Traded, Player", "team_abbrev": "NYY"}]
    details = {
        "1": [
            _row("1", "home_run", mia="1", nyy="0", hou="1"),
            _row("2", "field_out", mia="0", nyy="0", hou="1"),
        ]
    }

    [result] = validate_home_park_identities(
        leaderboard,
        details,
        _traded_schedule(),
        source_teams={"1": "MIA,NYY"},
    )

    assert result.status == "PASS"
    assert result.source_team == "MIA,NYY"
    assert result.home_hr_candidate_batted_balls == 2


def _row(game_pk: str, result: str, **park_flags: str) -> dict:
    row = {
        "game_pk": game_pk,
        "result": result,
        "batter_id": "1",
        "batter_name": "Judge, Aaron",
        "year": "2024",
    }
    row.update(park_flags)
    return row


def _schedule() -> dict:
    return {
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


def _traded_schedule() -> dict:
    return {
        "dates": [
            {
                "games": [
                    {
                        "gamePk": 1,
                        "gameType": "R",
                        "teams": {
                            "home": {"team": {"id": 146}},
                            "away": {"team": {"id": 144}},
                        },
                        "venue": {"id": 4169, "name": "loanDepot park"},
                    },
                    {
                        "gamePk": 2,
                        "gameType": "R",
                        "teams": {
                            "home": {"team": {"id": 147}},
                            "away": {"team": {"id": 111}},
                        },
                        "venue": {"id": 3313, "name": "Yankee Stadium"},
                    },
                ]
            }
        ]
    }
