import pytest

from parkshift.savant_hr import (
    SavantHomeRunError,
    build_details_url,
    build_leaderboard_url,
    detail_park_totals,
    extract_leaderboard_data,
    find_player_row,
    find_player_row_by_id,
    normalize_player_name,
    row_park_totals,
    search_player_rows,
)


def test_extract_leaderboard_data_from_html_payload() -> None:
    html = '<script>var data = [{"player":"Judge, Aaron","year":"2024","nyy":"58"}];</script>'

    rows = extract_leaderboard_data(html)

    assert rows == [{"player": "Judge, Aaron", "year": "2024", "nyy": "58"}]


def test_extract_leaderboard_data_raises_for_missing_payload() -> None:
    with pytest.raises(SavantHomeRunError):
        extract_leaderboard_data("<html></html>")


def test_row_park_totals_normalizes_savant_codes_to_park_ids() -> None:
    row = {"nyy": "58", "hou": "62", "sf": None}

    totals = row_park_totals(row)

    assert totals["yankee"] == 58
    assert totals["minute_maid"] == 62
    assert totals["oracle"] == 0


def test_detail_park_totals_sums_per_play_flags() -> None:
    rows = [{"nyy": "1", "hou": "0"}, {"nyy": "1", "hou": "1"}]

    totals = detail_park_totals(rows)

    assert totals["yankee"] == 2
    assert totals["minute_maid"] == 1


def test_build_savant_urls() -> None:
    assert build_leaderboard_url(year=2024, cat="xhr").endswith(
        "player_type=Batter&team=&min=0&cat=xhr&year=2024"
    )
    assert build_details_url(player_id=592450, year=2024).endswith(
        "type=details&player_id=592450&year=2024&player_type=Batter&cat=xhr"
    )


def test_normalize_player_name_handles_savant_and_common_order() -> None:
    assert normalize_player_name("Judge, Aaron") == "aaron judge"
    assert normalize_player_name("Aaron Judge") == "aaron judge"
    assert normalize_player_name("Ramírez, José") == "jose ramirez"


def test_find_player_row_by_name() -> None:
    rows = [
        {"player": "Judge, Aaron", "team_abbrev": "NYY", "player_id": "592450"},
        {"player": "Ramírez, José", "team_abbrev": "CLE", "player_id": "608070"},
    ]

    row = find_player_row(rows, "Jose Ramirez")

    assert row["player_id"] == "608070"


def test_find_player_row_raises_for_ambiguous_partial_name() -> None:
    rows = [
        {"player": "Smith, Will", "team_abbrev": "LAD", "player_id": "669257"},
        {"player": "Smith, Pavin", "team_abbrev": "AZ", "player_id": "656976"},
    ]

    with pytest.raises(SavantHomeRunError):
        find_player_row(rows, "Smith")


def test_find_player_row_can_filter_by_team() -> None:
    rows = [
        {"player": "Smith, Will", "team_abbrev": "LAD", "player_id": "669257"},
        {"player": "Smith, Pavin", "team_abbrev": "AZ", "player_id": "656976"},
    ]

    row = find_player_row(rows, "Smith", team="LAD")

    assert row["player_id"] == "669257"


def test_find_player_row_by_id() -> None:
    rows = [
        {"player": "Judge, Aaron", "team_abbrev": "NYY", "player_id": "592450"},
    ]

    row = find_player_row_by_id(rows, 592450)

    assert row["team_abbrev"] == "NYY"


def test_search_player_rows_filters_by_query_and_team() -> None:
    rows = [
        {"player": "Judge, Aaron", "team_abbrev": "NYY", "player_id": "592450"},
        {"player": "Judge, Aaron", "team_abbrev": "SF", "player_id": "999999"},
        {"player": "Ramírez, José", "team_abbrev": "CLE", "player_id": "608070"},
    ]

    matches = search_player_rows(rows, "judge", team="NYY")

    assert [row["player_id"] for row in matches] == ["592450"]
