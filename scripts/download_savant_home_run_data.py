from __future__ import annotations

import argparse

from parkshift.download import download_savant_home_run_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download Savant Home Run Tracker leaderboard and detail files."
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--cat", default="xhr", choices=["xhr", "adj_xhr"])
    parser.add_argument("--player-type", default="Batter")
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--team", default="")
    parser.add_argument("--min-hr", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Keep existing per-player detail JSON files instead of refetching them.",
    )
    args = parser.parse_args()

    result = download_savant_home_run_data(
        output_dir=args.output_dir,
        year=args.year,
        cat=args.cat,
        player_type=args.player_type,
        top=args.top,
        team=args.team,
        min_hr=args.min_hr,
        timeout=args.timeout,
        skip_existing=args.skip_existing,
    )

    print(f"Leaderboard: {result.leaderboard_path}")
    print(f"Details dir: {result.details_dir}")
    print(f"Players: {result.player_count}")
    print("Player ids:")
    for player_id in result.player_ids:
        print(player_id)


if __name__ == "__main__":
    main()
