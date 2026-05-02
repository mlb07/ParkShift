from __future__ import annotations

import argparse

from parkshift.workflow import run_home_park_validation_workflow


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download Savant data and run Home-Park Identity validation."
    )
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--cat", default="xhr", choices=["xhr", "adj_xhr"])
    parser.add_argument("--schedule-json")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    result = run_home_park_validation_workflow(
        output_dir=args.output_dir,
        year=args.year,
        top=args.top,
        cat=args.cat,
        schedule_json=args.schedule_json,
        skip_existing=args.skip_existing,
    )

    print(f"Leaderboard: {result.download.leaderboard_path}")
    print(f"Details dir: {result.download.details_dir}")
    print(f"Schedule: {result.schedule_path}")
    print(f"Results: {result.results_path}")
    print(f"Players: {result.summary['players']}")
    print(f"Checked: {result.summary['checked']}")
    print(f"Statuses: {result.summary['status_counts']}")
    print(f"Actual home HR: {result.summary['actual_home_hr']}")
    print(f"Source-park HR: {result.summary['source_park_hr']}")
    print(f"Total diff: {result.summary['total_diff']:+d}")
    print(f"Player MAE: {result.summary['player_mae']:.2f}")


if __name__ == "__main__":
    main()
