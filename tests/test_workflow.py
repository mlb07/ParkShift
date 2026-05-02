import json
from pathlib import Path

from parkshift.download import SavantDownloadResult
from parkshift.workflow import run_home_park_validation_workflow


def test_run_home_park_validation_workflow_writes_results(tmp_path, monkeypatch) -> None:
    leaderboard_path = tmp_path / "savant_hr_2024_xhr.html"
    details_dir = tmp_path / "savant_details_2024_xhr"
    details_dir.mkdir()
    leaderboard_path.write_text(
        '<script>var data = [{"player_id":"1","player":"Judge, Aaron",'
        '"team_abbrev":"NYY","hr_total":"1"}];</script>'
    )
    (details_dir / "1.json").write_text(
        json.dumps(
            [
                {
                    "game_pk": "1",
                    "result": "home_run",
                    "batter_id": "1",
                    "batter_name": "Judge, Aaron",
                    "year": "2024",
                    "team_abbrev": "NYY",
                    "nyy": "1",
                }
            ]
        )
    )

    def fake_download(**kwargs):
        return SavantDownloadResult(
            leaderboard_path=leaderboard_path,
            details_dir=details_dir,
            player_count=1,
            player_ids=("1",),
        )

    monkeypatch.setattr("parkshift.workflow.download_savant_home_run_data", fake_download)
    monkeypatch.setattr("parkshift.workflow.fetch_schedule", lambda year: _schedule())

    result = run_home_park_validation_workflow(
        output_dir=tmp_path,
        year=2024,
        top=1,
    )

    assert result.summary["status_counts"] == {"PASS": 1}
    assert result.schedule_path == tmp_path / "mlb_schedule_2024.json"
    assert result.results_path.exists()
    payload = json.loads(Path(result.results_path).read_text())
    assert payload["summary"]["checked"] == 1
    assert payload["results"][0]["status"] == "PASS"


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
