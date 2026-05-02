from __future__ import annotations

import argparse
import json
from pathlib import Path

from parkshift.savant_hr import load_leaderboard_file
from parkshift.schedule import load_schedule_file
from parkshift.validation import (
    validate_home_park_identities,
    validation_summary,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch-validate Home-Park Identity source-park reconstruction."
    )
    parser.add_argument("--leaderboard-html", required=True)
    parser.add_argument("--schedule-json", required=True)
    parser.add_argument("--details-dir", required=True)
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument(
        "--game-types",
        nargs="+",
        default=["R"],
        help="MLB Stats API game types to include. Default: R.",
    )
    parser.add_argument(
        "--source-team",
        action="append",
        default=[],
        metavar="PLAYER_ID=TEAM",
        help=(
            "Override a player's source team, useful for traded players. "
            "Use PLAYER_ID=MIA,NYY to combine multiple source teams."
        ),
    )
    args = parser.parse_args()

    leaderboard = sorted(
        load_leaderboard_file(args.leaderboard_html),
        key=lambda row: int(row["hr_total"]),
        reverse=True,
    )
    if args.top > 0:
        leaderboard = leaderboard[: args.top]

    details_by_player_id = _load_details(Path(args.details_dir))
    source_teams = _parse_source_team_overrides(args.source_team)
    results = validate_home_park_identities(
        leaderboard,
        details_by_player_id,
        load_schedule_file(args.schedule_json),
        source_teams=source_teams,
        game_types=tuple(args.game_types),
    )
    summary = validation_summary(results)

    print(f"Players: {summary['players']}")
    print(f"Checked: {summary['checked']}")
    print(f"Statuses: {summary['status_counts']}")
    print(f"Actual home HR: {summary['actual_home_hr']}")
    print(f"Source-park HR: {summary['source_park_hr']}")
    print(f"Total diff: {summary['total_diff']:+d}")
    print(f"Player MAE: {summary['player_mae']:.2f}")
    print()
    print(
        "player_id,player,source_team,status,home_hr_candidate_batted_balls,"
        "actual_home_hr,source_park_hr,diff,error"
    )
    for result in results:
        print(
            f"{result.player_id},{result.player_name},{result.source_team},"
            f"{result.status},{result.home_hr_candidate_batted_balls},"
            f"{result.actual_home_hr},{result.source_park_hr},"
            f"{result.diff:+d},{result.error or ''}"
        )


def _load_details(details_dir: Path) -> dict[str, list[dict]]:
    details_by_player_id: dict[str, list[dict]] = {}
    for path in details_dir.glob("*.json"):
        details_by_player_id[path.stem] = json.loads(path.read_text())
    return details_by_player_id


def _parse_source_team_overrides(values: list[str]) -> dict[str, str]:
    overrides: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid --source-team value: {value}")
        player_id, team = value.split("=", 1)
        overrides[player_id] = team
    return overrides


if __name__ == "__main__":
    main()
