import json
import csv
from io import StringIO

from parkshift.cli import main


def test_identity_cli_outputs_json(tmp_path, monkeypatch, capsys) -> None:
    details_path, schedule_path = _write_identity_inputs(tmp_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "parkshift",
            "identity",
            "--details-json",
            str(details_path),
            "--schedule-json",
            str(schedule_path),
            "--year",
            "2024",
            "--source-team",
            "NYY",
            "--format",
            "json",
        ],
    )

    main()

    output = json.loads(capsys.readouterr().out)
    assert output["contract_version"] == "1.0"
    assert output["player_id"] == "592450"
    assert output["source_team"] == "NYY"
    assert output["source_teams"] == ["NYY"]
    assert output["source_park_name"] == "Yankee Stadium"
    assert output["home_hr_candidate_batted_balls"] == 2
    assert output["actual_home_hr"] == 1
    assert output["source_park_hr"] == 1
    assert output["parks"][0]["park_id"] == "minute_maid"


def test_identity_cli_outputs_help_hurt_json_view(tmp_path, monkeypatch, capsys) -> None:
    details_path, schedule_path = _write_identity_inputs(tmp_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "parkshift",
            "identity",
            "--details-json",
            str(details_path),
            "--schedule-json",
            str(schedule_path),
            "--year",
            "2024",
            "--source-team",
            "NYY",
            "--format",
            "json",
            "--view",
            "help-hurt",
        ],
    )

    main()

    output = json.loads(capsys.readouterr().out)
    assert "parks" not in output
    assert output["source_team"] == "NYY"
    assert output["help_hurt_label"] == "Neutral"


def test_identity_cli_outputs_parkshift_score_json_view(
    tmp_path, monkeypatch, capsys
) -> None:
    details_path, schedule_path = _write_identity_inputs(tmp_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "parkshift",
            "identity",
            "--details-json",
            str(details_path),
            "--schedule-json",
            str(schedule_path),
            "--year",
            "2024",
            "--source-team",
            "NYY",
            "--format",
            "json",
            "--view",
            "parkshift-score",
        ],
    )

    main()

    output = json.loads(capsys.readouterr().out)
    assert output["source_team"] == "NYY"
    assert output["parks"][0]["park_id"] == "minute_maid"
    assert "actual_home_hr" not in output


def test_identity_cli_outputs_html(tmp_path, monkeypatch, capsys) -> None:
    details_path, schedule_path = _write_identity_inputs(tmp_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "parkshift",
            "identity",
            "--details-json",
            str(details_path),
            "--schedule-json",
            str(schedule_path),
            "--year",
            "2024",
            "--source-team",
            "NYY",
            "--format",
            "html",
        ],
    )

    main()

    output = capsys.readouterr().out
    assert "<!doctype html>" in output
    assert "Judge, Aaron" in output
    assert "Minute Maid Park" in output


def test_demo_cli_outputs_bundled_json(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["parkshift", "demo", "judge-2024", "--format", "json"],
    )

    main()

    output = json.loads(capsys.readouterr().out)
    assert output["contract_version"] == "1.0"
    assert output["player_name"] == "Judge, Aaron"
    assert output["source_team"] == "NYY"


def test_players_cli_searches_leaderboard(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "parkshift.cli.get_leaderboard",
        lambda **kwargs: [
            {
                "player": "Judge, Aaron",
                "team_abbrev": "NYY",
                "player_id": "592450",
                "hr_total": "58",
            }
        ],
    )
    monkeypatch.setattr(
        "sys.argv",
        ["parkshift", "players", "--query", "judge", "--year", "2024"],
    )

    main()

    output = capsys.readouterr().out
    assert "592450" in output
    assert "Judge, Aaron" in output


def test_app_cli_starts_uvicorn(monkeypatch, capsys) -> None:
    calls = []

    class FakeUvicorn:
        @staticmethod
        def run(*args, **kwargs):
            calls.append((args, kwargs))

    monkeypatch.setitem(__import__("sys").modules, "uvicorn", FakeUvicorn)
    monkeypatch.setattr("parkshift.cli.webbrowser.open", lambda url: calls.append(("open", url)))
    monkeypatch.setattr(
        "sys.argv",
        ["parkshift", "app", "--host", "127.0.0.1", "--port", "8999"],
    )

    main()

    output = capsys.readouterr().out
    assert "http://127.0.0.1:8999" in output
    assert calls[0] == ("open", "http://127.0.0.1:8999")
    assert calls[1][0] == ("parkshift.api:create_app",)
    assert calls[1][1]["factory"] is True


def test_identity_cli_outputs_csv(tmp_path, monkeypatch, capsys) -> None:
    details_path, schedule_path = _write_identity_inputs(tmp_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "parkshift",
            "identity",
            "--details-json",
            str(details_path),
            "--schedule-json",
            str(schedule_path),
            "--year",
            "2024",
            "--source-team",
            "NYY",
            "--format",
            "csv",
        ],
    )

    main()

    rows = list(csv.DictReader(StringIO(capsys.readouterr().out)))
    assert len(rows) == 30
    assert rows[0]["park_id"] == "minute_maid"
    assert rows[0]["translated_hr"] == "2"
    yankee = next(row for row in rows if row["park_id"] == "yankee")
    assert yankee["is_source_park"] == "True"


def test_identity_cli_defaults_to_text(tmp_path, monkeypatch, capsys) -> None:
    details_path, schedule_path = _write_identity_inputs(tmp_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "parkshift",
            "identity",
            "--details-json",
            str(details_path),
            "--schedule-json",
            str(schedule_path),
            "--year",
            "2024",
            "--source-team",
            "NYY",
            "--top",
            "1",
        ],
    )

    main()

    output = capsys.readouterr().out
    assert "Player: Judge, Aaron" in output
    assert "Source validation: PASS" in output
    assert "Minute Maid Park" in output


def test_identity_cli_debug_prints_skipped_game_ids(tmp_path, monkeypatch, capsys) -> None:
    details_path, schedule_path = _write_skipped_identity_inputs(tmp_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "parkshift",
            "identity",
            "--details-json",
            str(details_path),
            "--schedule-json",
            str(schedule_path),
            "--year",
            "2024",
            "--source-team",
            "NYY",
            "--debug",
            "--top",
            "1",
        ],
    )

    main()

    output = capsys.readouterr().out
    assert "Skipped rows: 1 missing game, 1 game type, 1 neutral/alternate site" in output
    assert "missing=99" in output
    assert "game_type=2" in output
    assert "neutral_or_alternate=3" in output


def test_identity_cli_accepts_combined_source_teams(
    tmp_path, monkeypatch, capsys
) -> None:
    details_path, schedule_path = _write_traded_player_identity_inputs(tmp_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "parkshift",
            "identity",
            "--details-json",
            str(details_path),
            "--schedule-json",
            str(schedule_path),
            "--year",
            "2024",
            "--source-teams",
            "MIA",
            "NYY",
            "--format",
            "json",
        ],
    )

    main()

    output = json.loads(capsys.readouterr().out)
    assert output["source_team"] == "MIA,NYY"
    assert output["source_teams"] == ["MIA", "NYY"]
    assert output["source_park_id"] == "multiple"
    assert output["source_park_ids"] == ["loan_depot", "yankee"]
    assert output["source_park_result"] is None
    assert output["home_hr_candidate_batted_balls"] == 2
    assert output["actual_home_hr"] == 1
    assert output["source_park_hr"] == 1


def test_identity_cli_can_infer_source_teams(tmp_path, monkeypatch, capsys) -> None:
    details_path, schedule_path = _write_traded_player_identity_inputs(tmp_path)

    monkeypatch.setattr(
        "sys.argv",
        [
            "parkshift",
            "identity",
            "--details-json",
            str(details_path),
            "--schedule-json",
            str(schedule_path),
            "--year",
            "2024",
            "--format",
            "json",
        ],
    )

    main()

    output = json.loads(capsys.readouterr().out)
    assert output["source_team"] == "MIA,NYY"
    assert output["source_teams"] == ["MIA", "NYY"]
    assert output["home_hr_candidate_batted_balls"] == 2


def _write_identity_inputs(tmp_path):
    details_path = tmp_path / "details.json"
    details_path.write_text(
        json.dumps(
            [
                _row("1", "home_run", nyy="1", hou="1"),
                _row("2", "field_out", nyy="0", hou="1"),
            ]
        )
    )

    schedule_path = tmp_path / "schedule.json"
    schedule_path.write_text(
        json.dumps(
            {
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
                                "venue": {
                                    "id": 3313,
                                    "name": "Yankee Stadium",
                                },
                            },
                            {
                                "gamePk": 2,
                                "gameType": "R",
                                "teams": {
                                    "home": {"team": {"id": 147}},
                                    "away": {"team": {"id": 111}},
                                },
                                "venue": {
                                    "id": 3313,
                                    "name": "Yankee Stadium",
                                },
                            },
                        ]
                    }
                ]
            }
        )
    )
    return details_path, schedule_path


def _write_traded_player_identity_inputs(tmp_path):
    details_path = tmp_path / "traded-details.json"
    details_path.write_text(
        json.dumps(
            [
                _row("1", "home_run", team_abbrev="MIA", mia="1", nyy="0", hou="1"),
                _row("2", "field_out", team_abbrev="NYY", mia="0", nyy="0", hou="1"),
            ]
        )
    )

    schedule_path = tmp_path / "traded-schedule.json"
    schedule_path.write_text(
        json.dumps(
            {
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
                                "venue": {
                                    "id": 4169,
                                    "name": "loanDepot park",
                                },
                            },
                            {
                                "gamePk": 2,
                                "gameType": "R",
                                "teams": {
                                    "home": {"team": {"id": 147}},
                                    "away": {"team": {"id": 111}},
                                },
                                "venue": {
                                    "id": 3313,
                                    "name": "Yankee Stadium",
                                },
                            },
                        ]
                    }
                ]
            }
        )
    )
    return details_path, schedule_path


def _write_skipped_identity_inputs(tmp_path):
    details_path = tmp_path / "skipped-details.json"
    details_path.write_text(
        json.dumps(
            [
                _row("1", "home_run", nyy="1", hou="1"),
                _row("2", "home_run", nyy="1", hou="1"),
                _row("3", "home_run", nyy="1", hou="1"),
                _row("99", "home_run", nyy="1", hou="1"),
            ]
        )
    )

    schedule_path = tmp_path / "skipped-schedule.json"
    schedule_path.write_text(
        json.dumps(
            {
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
                            },
                            {
                                "gamePk": 2,
                                "gameType": "W",
                                "teams": {
                                    "home": {"team": {"id": 147}},
                                    "away": {"team": {"id": 111}},
                                },
                                "venue": {"id": 3313, "name": "Yankee Stadium"},
                            },
                            {
                                "gamePk": 3,
                                "gameType": "R",
                                "teams": {
                                    "home": {"team": {"id": 147}},
                                    "away": {"team": {"id": 111}},
                                },
                                "venue": {"id": 5150, "name": "Neutral"},
                            },
                        ]
                    }
                ]
            }
        )
    )
    return details_path, schedule_path


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
