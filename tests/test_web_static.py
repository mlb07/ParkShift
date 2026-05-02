from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = ROOT / "web"


def test_static_frontend_files_exist() -> None:
    assert (WEB_DIR / "index.html").exists()
    assert (WEB_DIR / "styles.css").exists()
    assert (WEB_DIR / "app.js").exists()


def test_static_frontend_has_player_first_api_paths() -> None:
    html = (WEB_DIR / "index.html").read_text()
    script = (WEB_DIR / "app.js").read_text()

    assert 'id="app"' in html
    assert 'id="playerSearchInput"' in html
    assert 'id="seasonInput" type="number" min="2016"' in html
    assert 'max="2026"' in html
    assert 'id="exportCsvButton"' in html
    assert 'id="addBatchButton"' in html
    assert 'id="runBatchButton"' in html
    assert 'id="runHistory"' in html
    assert 'id="seasonLeaders"' in html
    assert 'id="adjustedModeButton"' in html
    assert 'id="standardModeButton"' in html
    assert 'id="batterTypeButton"' in html
    assert 'id="pitcherTypeButton"' in html
    assert "data-player-type" in html
    assert "player_type" in script
    assert "selectedPlayerType" in script
    assert "Stadium Adjusted HR" in html + script
    assert "Observed Flight HR" in html + script
    assert "Environment Adjusted" not in html + script
    assert "Adjusted Home Run" not in html + script
    assert 'id="loadLeadersButton"' in html
    assert 'id="leaderboardOrderSelect"' in html
    assert 'id="toggleLeadersPanelButton"' in html
    assert 'id="toggleTrailsButton"' in html
    assert 'id="ballTooltip"' in html
    assert 'id="toggleHistoryPanelButton"' in html
    assert "Readout" not in html
    assert "Target Park" not in html
    assert "Source team shortcuts" not in html
    assert ">Player ID<" not in html
    assert ">API base<" not in html
    assert "DEMO_IDENTITY" in script
    assert 'DEFAULT_CAT = "adj_xhr"' in script
    assert "MIN_TRANSLATION_YEAR = 2016" in script
    assert "MAX_TRANSLATION_YEAR" in script
    assert "displayErrorMessage" in script
    assert "categoryLabel" in script
    assert "data-cat-mode" in html
    assert "shouldDefaultToApiMode" in script
    assert "parkshift.identityHistory.v1" in script
    assert "handleRunBatch" in script
    assert "renderComparison" in script
    assert "renderSavedLeaderboard" in script
    assert "handleLoadLeaders" in script
    assert "leaderboardOrder" in script
    assert "leaderboardPanelOpen" in script
    assert "bindBallTooltips" in script
    assert "spreadOverlappingPoints" in script
    assert "/leaderboard?" in script
    assert "/identity?" in script
    assert "/players?" in script
    assert "/parks" in script
    assert "source_teams" in script
    assert "Click another park name" not in script
    assert "skipped by schedule filters" not in script
    assert "No coordinate-backed trails" not in script
    assert "clearing balls plotted" not in script
    assert "No warnings for this run" not in script
    assert "Home-Slice" not in html + script
    assert "home-slice" not in html + script
    assert "Source Home" not in html + script
    assert "TODO" not in html + script


def test_static_frontend_uses_identity_contract_fields() -> None:
    script = (WEB_DIR / "app.js").read_text()

    for field in (
        "actual_home_hr",
        "season_hr_total",
        "projected_total_hr",
        "source_park_hr",
        "park_average_hr",
        "help_hurt",
        "home_hr_candidate_batted_balls",
        "source_park_matches_actual",
        "parkshift_score",
        "home_runs",
        "spray_angle_deg",
    ):
        assert field in script
