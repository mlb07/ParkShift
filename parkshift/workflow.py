from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from parkshift.download import SavantDownloadResult, download_savant_home_run_data
from parkshift.savant_hr import load_leaderboard_file
from parkshift.schedule import fetch_schedule, load_schedule_file
from parkshift.validation import validate_home_park_identities, validation_summary


@dataclass(frozen=True)
class ValidationWorkflowResult:
    download: SavantDownloadResult
    schedule_path: Path
    results_path: Path
    summary: dict[str, object]


def run_home_park_validation_workflow(
    *,
    output_dir: str | Path,
    year: int,
    top: int = 50,
    cat: str = "xhr",
    schedule_json: str | Path | None = None,
    skip_existing: bool = False,
) -> ValidationWorkflowResult:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    download = download_savant_home_run_data(
        output_dir=output_path,
        year=year,
        top=top,
        cat=cat,
        skip_existing=skip_existing,
    )
    if schedule_json:
        schedule_path = Path(schedule_json)
        schedule = load_schedule_file(schedule_path)
    else:
        schedule_path = output_path / f"mlb_schedule_{year}.json"
        if skip_existing and schedule_path.exists():
            schedule = load_schedule_file(schedule_path)
        else:
            schedule = fetch_schedule(year)
            schedule_path.write_text(json.dumps(schedule, indent=2))

    leaderboard = sorted(
        load_leaderboard_file(download.leaderboard_path),
        key=lambda row: int(row.get("hr_total") or 0),
        reverse=True,
    )
    if top > 0:
        leaderboard = leaderboard[:top]
    details_by_player_id = {
        path.stem: json.loads(path.read_text())
        for path in download.details_dir.glob("*.json")
    }
    results = validate_home_park_identities(
        leaderboard,
        details_by_player_id,
        schedule,
    )
    summary = validation_summary(results)
    results_path = output_path / f"home_park_identity_validation_{year}_{cat}.json"
    results_path.write_text(
        json.dumps(
            {
                "summary": summary,
                "results": [result.__dict__ for result in results],
            },
            indent=2,
        )
    )
    return ValidationWorkflowResult(
        download=download,
        schedule_path=schedule_path,
        results_path=results_path,
        summary=summary,
    )
