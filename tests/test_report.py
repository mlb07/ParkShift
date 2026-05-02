import json

from parkshift.report import render_identity_report, render_identity_report_file


def test_render_identity_report_contains_summary_and_table() -> None:
    html = render_identity_report(_identity_data())

    assert "Judge, Aaron" in html
    assert "Park change" in html
    assert "Minute Maid Park" in html
    assert "+1.9" in html


def test_render_identity_report_file_writes_html(tmp_path) -> None:
    input_json = tmp_path / "identity.json"
    output_html = tmp_path / "report.html"
    input_json.write_text(json.dumps(_identity_data()))

    render_identity_report_file(input_json, output_html)

    assert output_html.exists()
    assert "ParkShift Report" in output_html.read_text()


def _identity_data() -> dict:
    return {
        "player_id": "592450",
        "player_name": "Judge, Aaron",
        "season": 2024,
        "source_team": "NYY",
        "source_park_name": "Yankee Stadium",
        "home_hr_candidate_batted_balls": 2,
        "actual_home_hr": 1,
        "source_park_hr": 1,
        "source_park_matches_actual": True,
        "park_average_hr": 0.1,
        "help_hurt": 0.9,
        "help_hurt_label": "Neutral",
        "parks": [
            {
                "rank": 1,
                "park_name": "Minute Maid Park",
                "translated_hr": 2,
                "parkshift_score": 1.9,
            }
        ],
    }
