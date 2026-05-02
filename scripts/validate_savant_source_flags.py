from __future__ import annotations

import argparse
import json
from pathlib import Path

from parkshift.savant_hr import load_leaderboard_file
from parkshift.schedule import game_context_by_pk


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate Savant per-play HR flags against real source parks."
    )
    parser.add_argument("--leaderboard-html", required=True)
    parser.add_argument("--schedule-json", required=True)
    parser.add_argument("--details-dir", required=True)
    parser.add_argument(
        "--game-types",
        nargs="+",
        default=["R"],
        help="MLB Stats API game types to include. Default: R.",
    )
    args = parser.parse_args()

    leaderboard = load_leaderboard_file(args.leaderboard_html)
    players = {row["player_id"]: row for row in leaderboard}
    schedule = json.loads(Path(args.schedule_json).read_text())
    games = game_context_by_pk(schedule)
    allowed_game_types = {game_type.upper() for game_type in args.game_types}

    results = []
    for path in sorted(Path(args.details_dir).glob("*.json")):
        player_id = path.stem
        if player_id not in players:
            continue

        rows = json.loads(path.read_text())
        actual = 0
        predicted = 0
        skipped = 0
        for row in rows:
            game = games.get(str(row["game_pk"]))
            if (
                not game
                or game.game_type.upper() not in allowed_game_types
                or not game.savant_park_code
            ):
                skipped += 1
                continue
            actual += int(row["result"] == "home_run")
            predicted += int(row.get(game.savant_park_code) or 0)

        player = players[player_id]
        results.append(
            {
                "player": player["player"],
                "team": player["team_abbrev"],
                "rows": len(rows),
                "actual_hr": actual,
                "source_flag_hr": predicted,
                "diff": predicted - actual,
                "skipped_rows": skipped,
            }
        )

    total_actual = sum(row["actual_hr"] for row in results)
    total_predicted = sum(row["source_flag_hr"] for row in results)
    mae = (
        sum(abs(row["diff"]) for row in results) / len(results) if results else 0.0
    )

    print(f"Players: {len(results)}")
    print(f"Actual HR: {total_actual}")
    print(f"Savant source-park flags: {total_predicted}")
    print(f"Total diff: {total_predicted - total_actual:+d}")
    print(f"Player MAE: {mae:.2f}")
    print(f"Skipped rows: {sum(row['skipped_rows'] for row in results)}")
    print()
    print("player,team,rows,actual_hr,source_flag_hr,diff,skipped_rows")
    for row in results:
        print(
            f"{row['player']},{row['team']},{row['rows']},{row['actual_hr']},"
            f"{row['source_flag_hr']},{row['diff']:+d},"
            f"{row['skipped_rows']}"
        )


if __name__ == "__main__":
    main()
