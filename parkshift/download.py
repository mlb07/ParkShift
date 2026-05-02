from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from parkshift.savant_hr import (
    build_details_url,
    build_leaderboard_url,
    extract_leaderboard_data,
    fetch_text,
)


@dataclass(frozen=True)
class SavantDownloadResult:
    leaderboard_path: Path
    details_dir: Path
    player_count: int
    player_ids: tuple[str, ...]


def download_savant_home_run_data(
    *,
    output_dir: str | Path,
    year: int,
    cat: str = "xhr",
    player_type: str = "Batter",
    top: int = 50,
    team: str = "",
    min_hr: int = 0,
    timeout: float = 30.0,
    skip_existing: bool = False,
) -> SavantDownloadResult:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    leaderboard_url = build_leaderboard_url(
        year=year,
        cat=cat,
        player_type=player_type,
        team=team,
        min_hr=min_hr,
    )
    leaderboard_html = fetch_text(leaderboard_url, timeout=timeout)
    leaderboard_path = output_path / f"savant_hr_{year}_{cat}.html"
    leaderboard_path.write_text(leaderboard_html)

    leaderboard_rows = _top_leaderboard_rows(
        extract_leaderboard_data(leaderboard_html),
        top=top,
    )
    details_dir = output_path / f"savant_details_{year}_{cat}"
    details_dir.mkdir(parents=True, exist_ok=True)

    player_ids: list[str] = []
    for row in leaderboard_rows:
        player_id = str(row["player_id"])
        player_ids.append(player_id)
        details_path = details_dir / f"{player_id}.json"
        if skip_existing and details_path.exists():
            continue
        details_url = build_details_url(
            player_id=player_id,
            year=year,
            cat=cat,
            player_type=player_type,
        )
        details = json.loads(fetch_text(details_url, timeout=timeout))
        details_path.write_text(json.dumps(details, indent=2))

    return SavantDownloadResult(
        leaderboard_path=leaderboard_path,
        details_dir=details_dir,
        player_count=len(player_ids),
        player_ids=tuple(player_ids),
    )


def _top_leaderboard_rows(rows: list[dict], *, top: int) -> list[dict]:
    sorted_rows = sorted(
        rows,
        key=lambda row: int(row.get("hr_total") or 0),
        reverse=True,
    )
    if top > 0:
        return sorted_rows[:top]
    return sorted_rows
