import json

from parkshift.download import download_savant_home_run_data
from parkshift.savant_hr import build_details_url, build_leaderboard_url


def test_download_savant_home_run_data_writes_top_player_files(
    tmp_path, monkeypatch
) -> None:
    leaderboard_url = build_leaderboard_url(year=2024, cat="xhr")
    judge_url = build_details_url(player_id="592450", year=2024, cat="xhr")
    soto_url = build_details_url(player_id="665742", year=2024, cat="xhr")
    responses = {
        leaderboard_url: (
            '<script>var data = ['
            '{"player":"Small Sample","player_id":"1","hr_total":"5"},'
            '{"player":"Judge, Aaron","player_id":"592450","hr_total":"58"},'
            '{"player":"Soto, Juan","player_id":"665742","hr_total":"41"}'
            "];</script>"
        ),
        judge_url: json.dumps([{"game_pk": "1", "result": "home_run"}]),
        soto_url: json.dumps([{"game_pk": "2", "result": "field_out"}]),
    }
    calls = []

    def fake_fetch_text(url: str, timeout: float = 30.0) -> str:
        calls.append((url, timeout))
        return responses[url]

    monkeypatch.setattr("parkshift.download.fetch_text", fake_fetch_text)

    result = download_savant_home_run_data(
        output_dir=tmp_path,
        year=2024,
        top=2,
        timeout=12.5,
    )

    assert result.leaderboard_path == tmp_path / "savant_hr_2024_xhr.html"
    assert result.details_dir == tmp_path / "savant_details_2024_xhr"
    assert result.player_count == 2
    assert result.player_ids == ("592450", "665742")
    assert result.leaderboard_path.exists()
    assert json.loads((result.details_dir / "592450.json").read_text()) == [
        {"game_pk": "1", "result": "home_run"}
    ]
    assert json.loads((result.details_dir / "665742.json").read_text()) == [
        {"game_pk": "2", "result": "field_out"}
    ]
    assert calls == [
        (leaderboard_url, 12.5),
        (judge_url, 12.5),
        (soto_url, 12.5),
    ]


def test_download_savant_home_run_data_can_skip_existing_details(
    tmp_path, monkeypatch
) -> None:
    leaderboard_url = build_leaderboard_url(year=2024, cat="xhr")
    judge_url = build_details_url(player_id="592450", year=2024, cat="xhr")
    details_dir = tmp_path / "savant_details_2024_xhr"
    details_dir.mkdir()
    details_path = details_dir / "592450.json"
    details_path.write_text(json.dumps([{"cached": True}]))
    responses = {
        leaderboard_url: (
            '<script>var data = ['
            '{"player":"Judge, Aaron","player_id":"592450","hr_total":"58"}'
            "];</script>"
        ),
        judge_url: json.dumps([{"cached": False}]),
    }
    calls = []

    def fake_fetch_text(url: str, timeout: float = 30.0) -> str:
        calls.append(url)
        return responses[url]

    monkeypatch.setattr("parkshift.download.fetch_text", fake_fetch_text)

    result = download_savant_home_run_data(
        output_dir=tmp_path,
        year=2024,
        skip_existing=True,
    )

    assert result.player_ids == ("592450",)
    assert json.loads(details_path.read_text()) == [{"cached": True}]
    assert calls == [leaderboard_url]


def test_download_savant_home_run_data_top_zero_downloads_all(
    tmp_path, monkeypatch
) -> None:
    leaderboard_url = build_leaderboard_url(year=2024, cat="xhr")
    first_url = build_details_url(player_id="1", year=2024, cat="xhr")
    second_url = build_details_url(player_id="2", year=2024, cat="xhr")
    responses = {
        leaderboard_url: (
            '<script>var data = ['
            '{"player":"First","player_id":"1","hr_total":"1"},'
            '{"player":"Second","player_id":"2","hr_total":"2"}'
            "];</script>"
        ),
        first_url: "[]",
        second_url: "[]",
    }

    def fake_fetch_text(url: str, timeout: float = 30.0) -> str:
        return responses[url]

    monkeypatch.setattr("parkshift.download.fetch_text", fake_fetch_text)

    result = download_savant_home_run_data(
        output_dir=tmp_path,
        year=2024,
        top=0,
    )

    assert result.player_ids == ("2", "1")
