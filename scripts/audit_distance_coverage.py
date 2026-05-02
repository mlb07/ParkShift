from __future__ import annotations

import argparse

from parkshift.statcast import (
    dataframe_to_batted_balls,
    fetch_statcast_batter,
    filter_home_team,
    filter_player,
    load_statcast_csv,
)
from parkshift.translator import is_over_wall_home_run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit projected distance coverage for HR and hard-hit balls."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv", help="Path to a Baseball Savant CSV export.")
    source.add_argument("--mlbam-id", type=int, help="MLBAM batter id for pybaseball.")
    parser.add_argument("--player", help="Exact player_name filter for CSV input.")
    parser.add_argument("--start-date", help="Fetch start date, YYYY-MM-DD.")
    parser.add_argument("--end-date", help="Fetch end date, YYYY-MM-DD.")
    parser.add_argument("--source-home-team", help="Only include games where this team was home.")
    parser.add_argument("--hard-hit-threshold", type=float, default=95.0)
    parser.add_argument("--show-missing", type=int, default=10)
    args = parser.parse_args()

    if args.csv:
        df = filter_player(load_statcast_csv(args.csv), args.player)
    else:
        if not args.start_date or not args.end_date:
            raise SystemExit("--start-date and --end-date are required with --mlbam-id.")
        df = fetch_statcast_batter(args.mlbam_id, args.start_date, args.end_date)

    df = filter_home_team(df, args.source_home_team)
    balls = dataframe_to_batted_balls(df)

    bbe = [ball for ball in balls if ball.launch_speed is not None or ball.launch_angle is not None]
    over_wall_hr = [ball for ball in balls if is_over_wall_home_run(ball)]
    all_hr = [ball for ball in balls if ball.events == "home_run"]
    hard_hit = [
        ball
        for ball in bbe
        if ball.launch_speed is not None and ball.launch_speed >= args.hard_hit_threshold
    ]

    print(f"Rows: {len(balls)}")
    print_coverage("Batted balls with EV/LA", bbe)
    print_coverage("All HR", all_hr)
    print_coverage("Over-wall HR", over_wall_hr)
    print_coverage(f"Hard-hit BBE >= {args.hard_hit_threshold:g} mph", hard_hit)

    missing_hr = [ball for ball in over_wall_hr if ball.hit_distance_sc is None]
    if missing_hr and args.show_missing:
        print()
        print(f"Missing over-wall HR projected distance sample ({min(args.show_missing, len(missing_hr))}):")
        for ball in missing_hr[: args.show_missing]:
            print(
                f"row={ball.row_id} player={ball.player_name} "
                f"ev={ball.launch_speed} la={ball.launch_angle} des={ball.description}"
            )


def print_coverage(label: str, balls: list) -> None:
    with_distance = [ball for ball in balls if ball.hit_distance_sc is not None]
    pct = 0.0 if not balls else 100 * len(with_distance) / len(balls)
    print(f"{label}: {len(with_distance)}/{len(balls)} with projected distance ({pct:.1f}%)")


if __name__ == "__main__":
    main()
