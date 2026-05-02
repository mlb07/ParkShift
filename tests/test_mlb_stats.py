from parkshift.mlb_stats import build_hitting_stats_url, get_regular_season_hr_leaders


def test_build_hitting_stats_url_requests_regular_season_hitting_leaders() -> None:
    url = build_hitting_stats_url(year=2025, limit=1000)

    assert "season=2025" in url
    assert "stats=season" in url
    assert "group=hitting" in url
    assert "playerPool=all" in url
    assert "sortStat=homeRuns" in url


def test_build_hitting_stats_url_can_request_qualified_pool() -> None:
    url = build_hitting_stats_url(year=2025, limit=1000, player_pool="qualified")

    assert "playerPool=qualified" in url


def test_get_regular_season_hr_leaders_normalizes_statsapi_payload(monkeypatch) -> None:
    def fake_get_hitting_stats(**kwargs):
        return {
            "stats": [
                {
                    "splits": [
                        {
                            "player": {
                                "id": 663728,
                                "lastName": "Raleigh",
                                "useName": "Cal",
                            },
                            "team": {"abbreviation": "SEA"},
                            "stat": {"homeRuns": 60},
                        },
                        {
                            "player": {
                                "id": 592450,
                                "lastName": "Judge",
                                "useName": "Aaron",
                            },
                            "team": {"abbreviation": "NYY"},
                            "stat": {"homeRuns": 53},
                        },
                    ]
                }
            ]
        }

    monkeypatch.setattr("parkshift.mlb_stats.get_hitting_stats", fake_get_hitting_stats)

    assert get_regular_season_hr_leaders(year=2025, limit=1, use_cache=False) == [
        {
            "player_id": "663728",
            "player": "Raleigh, Cal",
            "team_abbrev": "SEA",
            "hr_total": 60,
        }
    ]
