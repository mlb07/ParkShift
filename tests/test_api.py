import pytest

from parkshift.api import (
    MAX_TRANSLATION_YEAR,
    cached_identity_payload,
    identity_payload,
    leaderboard_payload,
    parks_payload,
    players_payload,
)
from parkshift.identity import SourceTeamInferenceError


def test_identity_payload_returns_requested_view() -> None:
    payload = identity_payload(
        player="Aaron Judge",
        year=2024,
        source_team="NYY",
        leaderboard_rows=[
            {"player": "Judge, Aaron", "team_abbrev": "NYY", "player_id": "592450"}
        ],
        detail_rows=[
            {
                "game_pk": "1",
                "result": "home_run",
                "batter_id": "592450",
                "batter_name": "Judge, Aaron",
                "year": "2024",
                "nyy": "1",
                "hou": "1",
            }
        ],
        schedule={
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
        },
        view="help-hurt",
        use_cache=False,
    )

    assert payload["contract_version"] == "1.0"
    assert payload["source_team"] == "NYY"
    assert payload["actual_home_hr"] == 1
    assert "parks" not in payload


def test_create_app_maps_identity_errors(monkeypatch) -> None:
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from parkshift.api import create_app

    def fake_identity_payload(**kwargs):
        raise SourceTeamInferenceError("Could not infer source team.")

    monkeypatch.setattr("parkshift.api.identity_payload", fake_identity_payload)
    client = fastapi_testclient.TestClient(create_app())

    response = client.get("/identity", params={"year": 2024, "player": "Judge"})

    assert response.status_code == 400
    assert response.json() == {"error": "Could not infer source team."}


def test_create_app_adds_identity_cache_header(monkeypatch) -> None:
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from parkshift.api import create_app

    def fake_cached_identity_payload(**kwargs):
        from parkshift import api

        api._LAST_IDENTITY_CACHE_STATUS = "memory"
        return {
            "player_id": kwargs["player_id"],
            "season": kwargs["year"],
            "cat": kwargs["cat"],
        }

    monkeypatch.setattr("parkshift.api.cached_identity_payload", fake_cached_identity_payload)
    client = fastapi_testclient.TestClient(create_app())

    response = client.get("/identity", params={"year": 2024, "player_id": "1"})

    assert response.status_code == 200
    assert response.headers["x-parkshift-cache"] == "memory"
    assert response.json()["cat"] == "adj_xhr"


def test_create_app_rejects_unsupported_year() -> None:
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from parkshift.api import create_app

    client = fastapi_testclient.TestClient(create_app())

    response = client.get("/identity", params={"year": 2015, "player_id": "1"})

    assert response.status_code == 400
    assert "2016" in response.json()["error"]


def test_create_app_rejects_future_year() -> None:
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from parkshift.api import create_app

    client = fastapi_testclient.TestClient(create_app())

    response = client.get("/identity", params={"year": MAX_TRANSLATION_YEAR + 1, "player_id": "1"})

    assert response.status_code == 400
    assert str(MAX_TRANSLATION_YEAR) in response.json()["error"]


def test_players_payload_returns_search_results(monkeypatch) -> None:
    def fake_get_leaderboard(**kwargs):
        return [
            {
                "player_id": "592450",
                "player": "Judge, Aaron",
                "team_abbrev": "NYY",
                "hr_total": "58",
            },
            {
                "player_id": "600000",
                "player": "Other, Player",
                "team_abbrev": "BOS",
                "hr_total": "1",
            },
        ]

    monkeypatch.setattr("parkshift.api.get_leaderboard", fake_get_leaderboard)
    monkeypatch.setattr(
        "parkshift.api.regular_season_hr_by_player_id",
        lambda **kwargs: {"592450": 53},
    )

    payload = players_payload(query="judge", year=2024, use_cache=False)

    assert payload["season"] == 2024
    assert payload["player_type"] == "Batter"
    assert payload["players"] == [
        {
            "player_id": "592450",
            "player": "Judge, Aaron",
            "team_abbrev": "NYY",
            "hr_total": 53,
        }
    ]


def test_players_payload_falls_back_to_savant_total_without_regular_hr(monkeypatch) -> None:
    def fake_get_leaderboard(**kwargs):
        return [
            {
                "player_id": "592450",
                "player": "Judge, Aaron",
                "team_abbrev": "NYY",
                "hr_total": "58",
            }
        ]

    monkeypatch.setattr("parkshift.api.get_leaderboard", fake_get_leaderboard)
    monkeypatch.setattr("parkshift.api.regular_season_hr_by_player_id", lambda **kwargs: {})

    payload = players_payload(query="judge", year=2024, use_cache=False)

    assert payload["players"][0]["hr_total"] == 58


def test_players_payload_supports_pitcher_hr_allowed(monkeypatch) -> None:
    def fake_get_leaderboard(**kwargs):
        assert kwargs["player_type"] == "Pitcher"
        return [
            {
                "player_id": "605135",
                "player": "Bassitt, Chris",
                "team_abbrev": "TOR",
                "hr_total": "28",
            }
        ]

    monkeypatch.setattr("parkshift.api.get_leaderboard", fake_get_leaderboard)
    monkeypatch.setattr(
        "parkshift.api.regular_season_pitcher_hr_allowed_by_player_id",
        lambda **kwargs: {"605135": 24},
    )

    payload = players_payload(
        query="bassitt", year=2025, player_type="Pitcher", use_cache=False
    )

    assert payload["player_type"] == "Pitcher"
    assert payload["players"] == [
        {
            "player_id": "605135",
            "player": "Bassitt, Chris",
            "team_abbrev": "TOR",
            "hr_total": 24,
        }
    ]


def test_cached_identity_payload_reuses_response(monkeypatch, tmp_path) -> None:
    calls = []

    def fake_identity_payload(**kwargs):
        calls.append(kwargs)
        return {"player_id": kwargs["player_id"], "season": kwargs["year"]}

    monkeypatch.setattr("parkshift.api.identity_payload", fake_identity_payload)
    monkeypatch.setattr(
        "parkshift.api.identity_response_cache_path",
        lambda key: tmp_path / "disabled" / "identity.json",
    )
    from parkshift import api

    api._IDENTITY_RESPONSE_CACHE.clear()
    first = cached_identity_payload(player_id="1", year=2024, source_teams=("NYY",))
    second = cached_identity_payload(player_id="1", year=2024, source_teams=("NYY",))

    assert first == second
    assert len(calls) == 1


def test_cached_identity_payload_reuses_disk_response(monkeypatch, tmp_path) -> None:
    calls = []
    cache_path = tmp_path / "identity.json"

    def fake_identity_payload(**kwargs):
        calls.append(kwargs)
        return {"player_id": kwargs["player_id"], "season": kwargs["year"]}

    monkeypatch.setattr("parkshift.api.identity_payload", fake_identity_payload)
    monkeypatch.setattr("parkshift.api.identity_response_cache_path", lambda key: cache_path)
    from parkshift import api

    api._IDENTITY_RESPONSE_CACHE.clear()
    first = cached_identity_payload(player_id="1", year=2024, source_teams=("NYY",))
    api._IDENTITY_RESPONSE_CACHE.clear()
    second = cached_identity_payload(player_id="1", year=2024, source_teams=("NYY",))

    assert first == second == {"player_id": "1", "season": 2024}
    assert len(calls) == 1


def test_leaderboard_payload_returns_regular_season_top_players(monkeypatch) -> None:
    calls = []

    def fake_get_regular_season_hr_leaders(**kwargs):
        calls.append(kwargs)
        return [
            {"player_id": "1", "player": "Low, Player", "team_abbrev": "BOS", "hr_total": "3"},
            {"player_id": "2", "player": "High, Player", "team_abbrev": "NYY", "hr_total": "9"},
            {"player_id": "3", "player": "Mid, Player", "team_abbrev": "LAD", "hr_total": "5"},
        ]

    monkeypatch.setattr(
        "parkshift.api.get_regular_season_hr_leaders", fake_get_regular_season_hr_leaders
    )

    payload = leaderboard_payload(year=2024, limit=2, use_cache=False)

    assert payload["season"] == 2024
    assert payload["player_type"] == "Batter"
    assert payload["scope"] == "regular_season"
    assert payload["qualified"] is True
    assert payload["order"] == "high"
    assert calls[0]["player_pool"] == "qualified"
    assert payload["players"] == [
        {"player_id": "2", "player": "High, Player", "team_abbrev": "NYY", "hr_total": 9},
        {"player_id": "3", "player": "Mid, Player", "team_abbrev": "LAD", "hr_total": 5},
    ]


def test_leaderboard_payload_returns_low_qualified_players(monkeypatch) -> None:
    def fake_get_regular_season_hr_leaders(**kwargs):
        return [
            {"player_id": "0", "player": "Zero, Player", "team_abbrev": "COL", "hr_total": "0"},
            {"player_id": "1", "player": "Low, Player", "team_abbrev": "BOS", "hr_total": "3"},
            {"player_id": "2", "player": "High, Player", "team_abbrev": "NYY", "hr_total": "9"},
            {"player_id": "3", "player": "Mid, Player", "team_abbrev": "LAD", "hr_total": "5"},
        ]

    monkeypatch.setattr(
        "parkshift.api.get_regular_season_hr_leaders", fake_get_regular_season_hr_leaders
    )

    payload = leaderboard_payload(year=2024, order="low", limit=2, use_cache=False)

    assert payload["order"] == "low"
    assert payload["players"] == [
        {"player_id": "1", "player": "Low, Player", "team_abbrev": "BOS", "hr_total": 3},
        {"player_id": "3", "player": "Mid, Player", "team_abbrev": "LAD", "hr_total": 5},
    ]


def test_leaderboard_payload_supports_pitcher_hr_allowed(monkeypatch) -> None:
    calls = []

    def fake_pitcher_leaders(**kwargs):
        calls.append(kwargs)
        return [
            {"player_id": "1", "player": "Low, Pitcher", "team_abbrev": "BOS", "hr_total": "3"},
            {"player_id": "2", "player": "High, Pitcher", "team_abbrev": "NYY", "hr_total": "9"},
        ]

    monkeypatch.setattr(
        "parkshift.api.get_regular_season_pitcher_hr_allowed_leaders",
        fake_pitcher_leaders,
    )

    payload = leaderboard_payload(year=2024, player_type="Pitcher", limit=1, use_cache=False)

    assert payload["player_type"] == "Pitcher"
    assert payload["qualified"] is True
    assert calls[0]["player_pool"] == "qualified"
    assert payload["players"] == [
        {"player_id": "2", "player": "High, Pitcher", "team_abbrev": "NYY", "hr_total": 9},
    ]


def test_parks_payload_returns_wall_profiles() -> None:
    payload = parks_payload()

    yankee = payload["parks"]["yankee"]

    assert yankee["park_name"] == "Yankee Stadium"
    assert len(yankee["wall"]) == 91
    assert yankee["wall"][0] == {
        "angle_deg": -45.0,
        "distance_ft": 318.0,
        "height_ft": 8,
    }


def test_create_app_serves_frontend_and_players(monkeypatch) -> None:
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from parkshift.api import create_app

    def fake_players_payload(**kwargs):
        return {"query": kwargs["query"], "season": kwargs["year"], "players": []}

    def fake_leaderboard_payload(**kwargs):
        return {"season": kwargs["year"], "players": []}

    monkeypatch.setattr("parkshift.api.players_payload", fake_players_payload)
    monkeypatch.setattr("parkshift.api.leaderboard_payload", fake_leaderboard_payload)
    client = fastapi_testclient.TestClient(create_app())

    frontend = client.get("/")
    favicon = client.get("/favicon.ico")
    players = client.get("/players", params={"query": "judge", "year": 2024})
    leaderboard = client.get("/leaderboard", params={"year": 2024, "limit": 5})
    parks = client.get("/parks")

    assert frontend.status_code == 200
    assert "ParkShift" in frontend.text
    assert favicon.status_code == 204
    assert players.status_code == 200
    assert players.json() == {"query": "judge", "season": 2024, "players": []}
    assert leaderboard.status_code == 200
    assert leaderboard.json() == {"season": 2024, "players": []}
    assert parks.status_code == 200
    assert "yankee" in parks.json()["parks"]
