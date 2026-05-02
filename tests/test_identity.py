from parkshift.identity import (
    NoDetailRowsError,
    NoHomeRowsError,
    SourceTeamInferenceError,
    calculate_home_park_identity,
    get_home_park_identity,
    help_hurt_label,
)
from parkshift.schedule import GameContext


PARK_RESULT_CONTRACT_KEYS = [
    "rank",
    "park_id",
    "park_name",
    "savant_code",
    "translated_hr",
    "projected_total_hr",
    "parkshift_score",
    "home_runs",
]

IDENTITY_CONTRACT_KEYS = [
    "contract_version",
    "player_type",
    "player_id",
    "player_name",
    "season",
    "source_team",
    "source_teams",
    "source_park_id",
    "source_park_ids",
    "source_park_name",
    "source_park_names",
    "cat",
    "game_types",
    "home_hr_candidate_batted_balls",
    "season_hr_total",
    "non_source_home_hr",
    "actual_home_hr",
    "source_park_hr",
    "source_park_matches_actual",
    "park_average_hr",
    "help_hurt",
    "help_hurt_label",
    "skipped_missing_game",
    "skipped_game_type",
    "skipped_neutral_or_alt_site",
    "skipped_missing_game_pks",
    "skipped_game_type_pks",
    "skipped_neutral_or_alt_site_pks",
    "source_park_result",
    "source_park_results",
    "parks",
]

HELP_HURT_VIEW_CONTRACT_KEYS = [
    "contract_version",
    "player_type",
    "player_id",
    "player_name",
    "season",
    "source_team",
    "source_teams",
    "source_park_id",
    "source_park_ids",
    "source_park_name",
    "source_park_names",
    "home_hr_candidate_batted_balls",
    "season_hr_total",
    "non_source_home_hr",
    "actual_home_hr",
    "source_park_hr",
    "source_park_matches_actual",
    "park_average_hr",
    "help_hurt",
    "help_hurt_label",
]

PARKSHIFT_SCORE_VIEW_CONTRACT_KEYS = [
    "contract_version",
    "player_type",
    "player_id",
    "player_name",
    "season",
    "source_team",
    "source_teams",
    "source_park_id",
    "source_park_ids",
    "source_park_name",
    "source_park_names",
    "season_hr_total",
    "non_source_home_hr",
    "park_average_hr",
    "parks",
]


def test_calculate_home_park_identity_filters_to_source_home_park() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
        "2": GameContext("2", "R", "BOS", "NYY", 3, "Fenway Park", "bos"),
        "3": GameContext("3", "R", "NYY", "BOS", 5150, "Neutral", None),
        "4": GameContext("4", "W", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
    }
    rows = [
        _row("1", "home_run", nyy="1", hou="1", sf="0"),
        _row("1", "field_out", nyy="0", hou="1", sf="0"),
        _row("2", "home_run", nyy="1", hou="1", sf="1"),
        _row("3", "home_run", nyy="1", hou="1", sf="1"),
        _row("4", "home_run", nyy="1", hou="1", sf="1"),
    ]

    identity = calculate_home_park_identity(rows, games, source_team="NYY")

    assert identity.source_park_name == "Yankee Stadium"
    assert identity.home_relevant_batted_balls == 2
    assert identity.home_hr_candidate_batted_balls == 2
    assert identity.season_hr_total == 3
    assert identity.non_source_home_hr == 2
    assert identity.actual_home_hr == 1
    assert identity.source_park_hr == 1
    assert identity.source_park_matches_actual is True
    assert identity.skipped_game_type == 1
    assert identity.skipped_neutral_or_alt_site == 1
    assert identity.skipped_game_type_pks == ("4",)
    assert identity.skipped_neutral_or_alt_site_pks == ("3",)

    by_park = {park.park_id: park for park in identity.parks}
    assert by_park["minute_maid"].translated_hr == 2
    assert by_park["oracle"].translated_hr == 0
    assert identity.source_park_result.park_id == "yankee"
    assert identity.park("minute_maid").translated_hr == 2
    assert identity.park("minute_maid").projected_total_hr == 4
    assert len(identity.park("minute_maid").home_runs) == 2
    assert identity.park("yankee").projected_total_hr == 3
    assert identity.top_parks(1)[0].translated_hr == 2
    assert identity.bottom_parks(1)[0].translated_hr == 0


def test_calculate_home_park_identity_can_include_postseason() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
        "2": GameContext("2", "W", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
    }
    rows = [
        _row("1", "home_run", nyy="1"),
        _row("2", "home_run", nyy="1"),
    ]

    identity = calculate_home_park_identity(
        rows,
        games,
        source_team="NYY",
        game_types=("R", "W"),
    )

    assert identity.home_relevant_batted_balls == 2
    assert identity.actual_home_hr == 2
    assert identity.source_park_hr == 2


def test_home_park_identity_to_dict_exports_public_contract() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
        "2": GameContext("2", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
    }
    rows = [
        _row("1", "home_run", nyy="1", hou="1"),
        _row("2", "field_out", nyy="0", hou="1"),
    ]

    identity = calculate_home_park_identity(rows, games, source_team="NYY")

    data = identity.to_dict()

    assert list(data) == IDENTITY_CONTRACT_KEYS
    assert list(data["source_park_result"]) == PARK_RESULT_CONTRACT_KEYS
    assert all(list(park) == PARK_RESULT_CONTRACT_KEYS for park in data["parks"])
    assert data["contract_version"] == "1.0"
    assert data["player_type"] == "Batter"
    assert data["player_id"] == "592450"
    assert data["player_name"] == "Judge, Aaron"
    assert data["season"] == 2024
    assert data["source_team"] == "NYY"
    assert data["source_teams"] == ["NYY"]
    assert data["source_park_id"] == "yankee"
    assert data["source_park_ids"] == ["yankee"]
    assert data["source_park_name"] == "Yankee Stadium"
    assert data["source_park_names"] == ["Yankee Stadium"]
    assert data["cat"] == "xhr"
    assert data["game_types"] == ["R"]
    assert data["home_hr_candidate_batted_balls"] == 2
    assert data["season_hr_total"] == 1
    assert data["non_source_home_hr"] == 0
    assert data["actual_home_hr"] == 1
    assert data["source_park_hr"] == 1
    assert data["source_park_matches_actual"] is True
    assert data["park_average_hr"] == identity.park_average_hr
    assert data["help_hurt"] == identity.help_hurt
    assert data["help_hurt_label"] == identity.help_hurt_label
    assert data["skipped_missing_game"] == 0
    assert data["skipped_game_type"] == 0
    assert data["skipped_neutral_or_alt_site"] == 0
    assert data["skipped_missing_game_pks"] == []
    assert data["skipped_game_type_pks"] == []
    assert data["skipped_neutral_or_alt_site_pks"] == []
    assert data["source_park_result"]["park_id"] == "yankee"
    assert data["source_park_result"]["translated_hr"] == 1
    assert data["source_park_results"] == [data["source_park_result"]]
    assert data["parks"] == [park.to_dict() for park in identity.parks]
    assert data["parks"][0] == {
        "rank": 1,
        "park_id": identity.parks[0].park_id,
        "park_name": identity.parks[0].park_name,
        "savant_code": identity.parks[0].savant_code,
        "translated_hr": identity.parks[0].translated_hr,
        "projected_total_hr": identity.parks[0].projected_total_hr,
        "parkshift_score": identity.parks[0].parkshift_score,
        "home_runs": [marker.to_dict() for marker in identity.parks[0].home_runs],
    }
    assert data["parks"][0]["home_runs"][0] == {
        "play_id": None,
        "game_pk": "1",
        "game_date": None,
        "distance_ft": None,
        "launch_angle": None,
        "exit_velocity": None,
        "spray_angle_deg": None,
    }


def test_home_park_identity_help_hurt_view_exports_product_view() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
        "2": GameContext("2", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
    }
    rows = [
        _row("1", "home_run", nyy="1", hou="1"),
        _row("2", "field_out", nyy="0", hou="1"),
    ]

    identity = calculate_home_park_identity(rows, games, source_team="NYY")

    view = identity.help_hurt_view()

    assert list(view) == HELP_HURT_VIEW_CONTRACT_KEYS
    assert view == {
        "contract_version": "1.0",
        "player_type": "Batter",
        "player_id": "592450",
        "player_name": "Judge, Aaron",
        "season": 2024,
        "source_team": "NYY",
        "source_teams": ["NYY"],
        "source_park_id": "yankee",
        "source_park_ids": ["yankee"],
        "source_park_name": "Yankee Stadium",
        "source_park_names": ["Yankee Stadium"],
        "home_hr_candidate_batted_balls": 2,
        "season_hr_total": 1,
        "non_source_home_hr": 0,
        "actual_home_hr": 1,
        "source_park_hr": 1,
        "source_park_matches_actual": True,
        "park_average_hr": identity.park_average_hr,
        "help_hurt": identity.help_hurt,
        "help_hurt_label": "Neutral",
    }


def test_home_park_identity_parkshift_score_view_exports_product_view() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
        "2": GameContext("2", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
    }
    rows = [
        _row("1", "home_run", nyy="1", hou="1"),
        _row("2", "field_out", nyy="0", hou="1"),
    ]

    identity = calculate_home_park_identity(rows, games, source_team="NYY")

    view = identity.parkshift_score_view()

    assert list(view) == PARKSHIFT_SCORE_VIEW_CONTRACT_KEYS
    assert all(list(park) == PARK_RESULT_CONTRACT_KEYS for park in view["parks"])
    assert view["contract_version"] == "1.0"
    assert view["player_type"] == "Batter"
    assert view["player_id"] == "592450"
    assert view["player_name"] == "Judge, Aaron"
    assert view["season"] == 2024
    assert view["source_team"] == "NYY"
    assert view["source_teams"] == ["NYY"]
    assert view["source_park_id"] == "yankee"
    assert view["source_park_ids"] == ["yankee"]
    assert view["source_park_name"] == "Yankee Stadium"
    assert view["source_park_names"] == ["Yankee Stadium"]
    assert view["park_average_hr"] == identity.park_average_hr
    assert view["parks"] == [park.to_dict() for park in identity.parks]
    assert view["parks"][0]["rank"] == 1
    assert view["parks"][0]["park_id"] == "minute_maid"
    assert view["parks"][0]["translated_hr"] == 2


def test_home_park_identity_to_dataframe_exports_park_table() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
        "2": GameContext("2", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
    }
    rows = [
        _row("1", "home_run", nyy="1", hou="1"),
        _row("2", "field_out", nyy="0", hou="1"),
    ]

    identity = calculate_home_park_identity(rows, games, source_team="NYY")

    frame = identity.to_dataframe()

    assert len(frame) == 30
    assert list(frame.columns) == [
        "rank",
        "park_id",
        "park_name",
        "savant_code",
        "translated_hr",
        "projected_total_hr",
        "parkshift_score",
        "is_source_park",
        "park_average_hr",
        "season_hr_total",
        "non_source_home_hr",
        "source_team",
        "source_teams",
        "player_type",
        "player_id",
        "player_name",
        "season",
    ]
    yankee = frame[frame["park_id"] == "yankee"].iloc[0]
    assert bool(yankee["is_source_park"]) is True
    assert yankee["source_team"] == "NYY"
    assert yankee["source_teams"] == "NYY"
    assert yankee["player_type"] == "Batter"


def test_calculate_home_park_identity_can_combine_traded_player_home_teams() -> None:
    games = {
        "1": GameContext("1", "R", "MIA", "ATL", 4169, "loanDepot park", "mia"),
        "2": GameContext("2", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
        "3": GameContext("3", "R", "MIA", "NYM", 4169, "loanDepot park", "mia"),
        "4": GameContext("4", "R", "BOS", "NYY", 3, "Fenway Park", "bos"),
    }
    rows = [
        _row("1", "home_run", mia="1", nyy="0", hou="1"),
        _row("2", "field_out", mia="0", nyy="0", hou="1"),
        _row("3", "field_out", mia="0", nyy="1", hou="1"),
        _row("4", "home_run", mia="1", nyy="1", hou="1"),
    ]

    combined = calculate_home_park_identity(
        rows,
        games,
        source_teams=("MIA", "NYY"),
    )
    miami_only = calculate_home_park_identity(rows, games, source_team="MIA")
    yankees_only = calculate_home_park_identity(rows, games, source_team="NYY")

    assert combined.source_team == "MIA,NYY"
    assert combined.source_teams == ("MIA", "NYY")
    assert combined.source_park_id == "multiple"
    assert combined.source_park_ids == ("loan_depot", "yankee")
    assert combined.source_park_name == "Multiple source parks"
    assert combined.source_park_names == ("loanDepot park", "Yankee Stadium")
    assert combined.home_hr_candidate_batted_balls == 3
    assert combined.actual_home_hr == 1
    assert combined.source_park_hr == 1
    assert combined.source_park_matches_actual is True
    assert combined.park("minute_maid").translated_hr == 3
    assert miami_only.home_hr_candidate_batted_balls == 2
    assert miami_only.source_park_hr == 1
    assert yankees_only.home_hr_candidate_batted_balls == 1
    assert yankees_only.source_park_hr == 0

    data = combined.to_dict()

    assert data["source_park_result"] is None
    assert [park["park_id"] for park in data["source_park_results"]] == [
        "loan_depot",
        "yankee",
    ]

    try:
        combined.source_park_result
    except ValueError as exc:
        assert "Multiple source parks" in str(exc)
    else:
        raise AssertionError("Expected source_park_result to reject multiple parks")


def test_get_home_park_identity_prefers_detail_team_inference_over_leaderboard_team() -> None:
    schedule = {
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
    detail_rows = [
        _row("1", "home_run", team_abbrev="MIA", mia="1", nyy="0"),
        _row("2", "home_run", team_abbrev="NYY", mia="0", nyy="1"),
    ]

    identity = get_home_park_identity(
        player_id="592450",
        year=2024,
        leaderboard_rows=[
            {"player": "Judge, Aaron", "team_abbrev": "NYY", "player_id": "592450"}
        ],
        detail_rows=detail_rows,
        schedule=schedule,
        use_cache=False,
    )

    assert identity.source_teams == ("MIA", "NYY")
    assert identity.source_park_ids == ("loan_depot", "yankee")


def test_calculate_home_park_identity_can_infer_single_source_team() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
        "2": GameContext("2", "R", "BOS", "NYY", 3, "Fenway Park", "bos"),
    }
    rows = [
        _row("1", "home_run", team_abbrev="NYY", nyy="1", hou="1"),
        _row("2", "home_run", team_abbrev="NYY", nyy="1", hou="1"),
    ]

    identity = calculate_home_park_identity(rows, games)

    assert identity.source_team == "NYY"
    assert identity.source_teams == ("NYY",)
    assert identity.home_hr_candidate_batted_balls == 1
    assert identity.actual_home_hr == 1
    assert identity.source_park_hr == 1


def test_calculate_home_park_identity_can_infer_combined_source_teams() -> None:
    games = {
        "1": GameContext("1", "R", "MIA", "ATL", 4169, "loanDepot park", "mia"),
        "2": GameContext("2", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
        "3": GameContext("3", "R", "BOS", "NYY", 3, "Fenway Park", "bos"),
    }
    rows = [
        _row("1", "home_run", team_abbrev="MIA", mia="1", nyy="0", hou="1"),
        _row("2", "field_out", team_abbrev="NYY", mia="0", nyy="0", hou="1"),
        _row("3", "home_run", team_abbrev="NYY", mia="1", nyy="1", hou="1"),
    ]

    identity = calculate_home_park_identity(rows, games)

    assert identity.source_team == "MIA,NYY"
    assert identity.source_teams == ("MIA", "NYY")
    assert identity.home_hr_candidate_batted_balls == 2
    assert identity.actual_home_hr == 1
    assert identity.source_park_hr == 1
    assert identity.park("minute_maid").translated_hr == 2


def test_calculate_home_park_identity_can_infer_traded_teams_from_play_metadata() -> None:
    games = {
        "1": GameContext("1", "R", "AZ", "ATL", 15, "Chase Field", "ari"),
        "2": GameContext("2", "R", "SEA", "COL", 680, "T-Mobile Park", "sea"),
        "3": GameContext("3", "R", "LAA", "SEA", 1, "Angel Stadium", "laa"),
    }
    rows = [
        _row("1", "home_run", play_id="az-home", ari="1", sea="0", hou="1"),
        _row("2", "field_out", play_id="sea-home", ari="0", sea="1", hou="1"),
        _row("3", "home_run", play_id="sea-away", ari="1", sea="1", hou="1"),
    ]

    identity = calculate_home_park_identity(
        rows,
        games,
        play_metadata_by_id={
            "az-home": {"batting_team": "AZ"},
            "sea-home": {"batting_team": "SEA"},
            "sea-away": {"batting_team": "SEA"},
        },
    )

    assert identity.source_team == "AZ,SEA"
    assert identity.source_teams == ("AZ", "SEA")
    assert identity.home_hr_candidate_batted_balls == 2
    assert identity.source_park_ids == ("chase", "t_mobile")
    assert identity.park("minute_maid").translated_hr == 2


def test_calculate_home_park_identity_supports_pitcher_home_runs_allowed() -> None:
    games = {
        "1": GameContext("1", "R", "TOR", "NYY", 14, "Rogers Centre", "tor"),
        "2": GameContext("2", "R", "NYY", "TOR", 3313, "Yankee Stadium", "nyy"),
        "3": GameContext("3", "R", "TOR", "BOS", 14, "Rogers Centre", "tor"),
    }
    rows = [
        _pitcher_row("1", "home_run", play_id="tor-home-1", tor="1", nyy="1", hou="1"),
        _pitcher_row("2", "home_run", play_id="tor-away", tor="1", nyy="1", hou="1"),
        _pitcher_row("3", "field_out", play_id="tor-home-2", tor="0", nyy="1", hou="1"),
    ]

    identity = calculate_home_park_identity(
        rows,
        games,
        player_type="Pitcher",
        play_metadata_by_id={
            "tor-home-1": {"pitching_team": "TOR"},
            "tor-away": {"pitching_team": "TOR"},
            "tor-home-2": {"pitching_team": "TOR"},
        },
    )

    assert identity.player_type == "Pitcher"
    assert identity.player_id == "605135"
    assert identity.player_name == "Bassitt, Chris"
    assert identity.source_team == "TOR"
    assert identity.source_park_id == "rogers_centre"
    assert identity.home_hr_candidate_batted_balls == 2
    assert identity.season_hr_total == 2
    assert identity.actual_home_hr == 1
    assert identity.source_park_hr == 1
    assert identity.help_hurt_label == "Neutral"
    assert identity.park("rogers_centre").rank < identity.park("yankee").rank
    assert identity.park("minute_maid").translated_hr == 2
    assert identity.park("yankee").translated_hr == 2


def test_calculate_home_park_identity_requires_source_team_when_it_cannot_infer() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
    }
    rows = [_row("1", "home_run", nyy="1")]

    try:
        calculate_home_park_identity(rows, games)
    except SourceTeamInferenceError as exc:
        assert "--source-team" in str(exc)
        assert "--source-teams" in str(exc)
        assert "team_abbrev" in str(exc)
    else:
        raise AssertionError("Expected SourceTeamInferenceError")


def test_calculate_home_park_identity_raises_for_empty_detail_rows() -> None:
    try:
        calculate_home_park_identity([], {}, source_team="NYY")
    except NoDetailRowsError as exc:
        assert "No Savant Home Run Tracker detail rows found" in str(exc)
    else:
        raise AssertionError("Expected NoDetailRowsError")


def test_calculate_home_park_identity_rejects_empty_source_teams() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
    }
    rows = [_row("1", "home_run", team_abbrev="NYY", nyy="1")]

    try:
        calculate_home_park_identity(rows, games, source_teams=())
    except ValueError as exc:
        assert "At least one source team" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_calculate_home_park_identity_raises_for_wrong_source_team() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
    }
    rows = [_row("1", "home_run", nyy="1")]

    try:
        calculate_home_park_identity(rows, games, source_team="BOS")
    except NoHomeRowsError as exc:
        assert "source team BOS" in str(exc)
        assert "--source-teams" in str(exc)
    else:
        raise AssertionError("Expected NoHomeRowsError")


def test_calculate_home_park_identity_raises_for_unknown_source_team() -> None:
    try:
        calculate_home_park_identity([], {}, source_team="XYZ", require_home_rows=False)
    except ValueError as exc:
        assert "Unknown source team: XYZ" in str(exc)
        assert "NYY" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_calculate_home_park_identity_can_allow_zero_home_rows() -> None:
    games = {
        "1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy"),
    }
    rows = [_row("1", "home_run", nyy="1")]

    identity = calculate_home_park_identity(
        rows,
        games,
        source_team="BOS",
        require_home_rows=False,
    )

    assert identity.home_hr_candidate_batted_balls == 0
    assert identity.actual_home_hr == 0


def test_get_home_park_identity_accepts_player_name_with_injected_backend_data() -> None:
    leaderboard_rows = [
        {"player": "Judge, Aaron", "team_abbrev": "NYY", "player_id": "592450"}
    ]
    detail_rows = [_row("1", "home_run", nyy="1", hou="1")]
    schedule = _schedule(
        game_pk=1,
        game_type="R",
        home_team_id=147,
        away_team_id=111,
        venue_id=3313,
        venue_name="Yankee Stadium",
    )

    identity = get_home_park_identity(
        player="Aaron Judge",
        year=2024,
        source_team="NYY",
        leaderboard_rows=leaderboard_rows,
        detail_rows=detail_rows,
        schedule=schedule,
        use_cache=False,
    )

    assert identity.player_id == "592450"
    assert identity.source_park_hr == 1
    assert identity.source_park_matches_actual is True


def test_get_home_park_identity_uses_leaderboard_team_as_live_fallback(
    monkeypatch,
) -> None:
    leaderboard_rows = [
        {"player": "Judge, Aaron", "team_abbrev": "NYY", "player_id": "592450"}
    ]
    detail_rows = [_row("1", "home_run", nyy="1", hou="1")]
    monkeypatch.setattr("parkshift.identity.get_details", lambda **kwargs: detail_rows)

    identity = get_home_park_identity(
        player_id="592450",
        year=2024,
        leaderboard_rows=leaderboard_rows,
        schedule=_schedule(
            game_pk=1,
            game_type="R",
            home_team_id=147,
            away_team_id=111,
            venue_id=3313,
            venue_name="Yankee Stadium",
        ),
        use_cache=False,
    )

    assert identity.source_team == "NYY"
    assert identity.source_park_hr == 1


def test_help_hurt_label_thresholds() -> None:
    assert help_hurt_label(3.0) == "Strong Help"
    assert help_hurt_label(1.0) == "Help"
    assert help_hurt_label(0.5) == "Neutral"
    assert help_hurt_label(-1.0) == "Hurt"
    assert help_hurt_label(-3.0) == "Strong Hurt"


def _row(game_pk: str, result: str, **park_flags: str) -> dict:
    row = {
        "game_pk": game_pk,
        "result": result,
        "batter_id": "592450",
        "batter_name": "Judge, Aaron",
        "year": "2024",
    }
    row.update(park_flags)
    return row


def _pitcher_row(game_pk: str, result: str, **park_flags: str) -> dict:
    row = {
        "game_pk": game_pk,
        "result": result,
        "pitcher_id": "605135",
        "pitcher_name": "Bassitt, Chris",
        "year": "2025",
    }
    row.update(park_flags)
    return row


def _schedule(
    *,
    game_pk: int,
    game_type: str,
    home_team_id: int,
    away_team_id: int,
    venue_id: int,
    venue_name: str,
) -> dict:
    return {
        "dates": [
            {
                "games": [
                    {
                        "gamePk": game_pk,
                        "gameType": game_type,
                        "teams": {
                            "home": {"team": {"id": home_team_id}},
                            "away": {"team": {"id": away_team_id}},
                        },
                        "venue": {"id": venue_id, "name": venue_name},
                    }
                ]
            }
        ]
    }
