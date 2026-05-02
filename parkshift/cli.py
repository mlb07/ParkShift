from __future__ import annotations

import argparse
import json
import webbrowser
import sys
from pathlib import Path

from parkshift.demo import DEMO_NAMES, load_demo_identity
from parkshift.identity import (
    IdentityError,
    calculate_home_park_identity,
    get_home_park_identity,
)
from parkshift.mlb import TEAM_HOME_PARK_ID
from parkshift.parks import load_parks
from parkshift.report import render_identity_report
from parkshift.savant_hr import SavantHomeRunError, get_leaderboard, search_player_rows
from parkshift.schedule import fetch_schedule, game_context_by_pk, load_schedule_file
from parkshift.statcast import (
    dataframe_to_batted_balls,
    fetch_statcast_batter,
    filter_home_team,
    filter_player,
    load_statcast_csv,
)
from parkshift.translator import summary_to_dataframe, translate_balls


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="parkshift",
        description="Translate real Statcast batted balls into home runs by park.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    translate = subparsers.add_parser("translate", help="Run a park translation.")
    source = translate.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv", help="Path to a Baseball Savant CSV export.")
    source.add_argument("--mlbam-id", type=int, help="MLBAM batter id for pybaseball.")
    translate.add_argument("--player", help="Exact player_name filter for CSV input.")
    translate.add_argument("--start-date", help="Fetch start date, YYYY-MM-DD.")
    translate.add_argument("--end-date", help="Fetch end date, YYYY-MM-DD.")
    translate.add_argument(
        "--source-home-team",
        help="Only use batted balls from games where this team was home, e.g. NYY.",
    )
    translate.add_argument(
        "--parks",
        nargs="+",
        help="Optional park ids to include, e.g. yankee minute_maid oracle.",
    )
    translate.add_argument(
        "--distance-tolerance-ft",
        type=float,
        default=0.0,
        help="Carry-distance allowance for Statcast/wall-profile uncertainty.",
    )
    translate.add_argument(
        "--foul-line-tolerance-deg",
        type=float,
        default=4.0,
        help="Spray-angle allowance near foul poles.",
    )
    translate.add_argument(
        "--probabilistic",
        action="store_true",
        help="Rank parks by expected HR instead of hard yes/no HR.",
    )

    identity = subparsers.add_parser(
        "identity", help="Calculate Home-Park Identity from Savant tracker rows."
    )
    identity_source = identity.add_mutually_exclusive_group(required=True)
    identity_source.add_argument(
        "--details-json",
        help="Path to a Savant Home Run Tracker details JSON file.",
    )
    identity_source.add_argument(
        "--player-id",
        help="MLBAM batter id to fetch from Savant Home Run Tracker.",
    )
    identity_source.add_argument(
        "--player",
        help='Player name to look up from Savant, e.g. "Aaron Judge".',
    )
    identity.add_argument("--year", type=int, required=True)
    identity_team = identity.add_mutually_exclusive_group()
    identity_team.add_argument(
        "--source-team",
        help=(
            "Optional team override whose real home games define the identity "
            "slice, e.g. NYY."
        ),
    )
    identity_team.add_argument(
        "--source-teams",
        nargs="+",
        help=(
            "Optional team overrides whose combined real home games define the "
            "identity slice, e.g. MIA NYY for a traded player."
        ),
    )
    identity.add_argument(
        "--schedule-json",
        help="Optional MLB Stats API schedule JSON. Fetched when omitted.",
    )
    identity.add_argument(
        "--cat",
        default="xhr",
        choices=["xhr", "adj_xhr"],
        help="Savant tracker mode. Use xhr for observed trajectory.",
    )
    identity.add_argument(
        "--player-type",
        default="Batter",
        choices=["Batter", "Pitcher"],
        help="Use Batter for home runs hit or Pitcher for home runs allowed.",
    )
    identity.add_argument(
        "--game-types",
        nargs="+",
        default=["R"],
        help=(
            "MLB Stats API game types to include. Default: R. "
            "Add W/L/D/F for postseason/all special use cases."
        ),
    )
    identity.add_argument(
        "--top",
        type=int,
        default=30,
        help="Number of ranked parks to print.",
    )
    identity.add_argument(
        "--format",
        choices=["text", "json", "csv", "html"],
        default="text",
        help="Output format. Default: text.",
    )
    identity.add_argument(
        "--view",
        choices=["full", "help-hurt", "parkshift-score"],
        default="full",
        help="JSON view to output. Default: full.",
    )
    identity.add_argument(
        "--no-cache",
        action="store_true",
        help="Fetch fresh Savant/schedule data instead of using the local cache.",
    )
    identity.add_argument(
        "--debug",
        action="store_true",
        help="Include skipped game ids in text output.",
    )

    demo = subparsers.add_parser("demo", help="Run a bundled ParkShift demo.")
    demo.add_argument("name", choices=DEMO_NAMES)
    demo.add_argument(
        "--format",
        choices=["text", "json", "csv", "html"],
        default="text",
        help="Output format. Default: text.",
    )
    demo.add_argument(
        "--view",
        choices=["full", "help-hurt", "parkshift-score"],
        default="full",
        help="JSON view to output. Default: full.",
    )

    players = subparsers.add_parser("players", help="Search Savant leaderboard players.")
    players.add_argument("--query", required=True)
    players.add_argument("--year", type=int, required=True)
    players.add_argument("--cat", default="xhr", choices=["xhr", "adj_xhr"])
    players.add_argument("--player-type", default="Batter", choices=["Batter", "Pitcher"])
    players.add_argument("--team")
    players.add_argument("--limit", type=int, default=10)
    players.add_argument("--format", choices=["text", "json"], default="text")
    players.add_argument("--no-cache", action="store_true")

    app = subparsers.add_parser("app", help="Run the local ParkShift web app.")
    app.add_argument("--host", default="127.0.0.1")
    app.add_argument("--port", type=int, default=8000)
    app.add_argument("--reload", action="store_true")
    app.add_argument("--no-open", action="store_true")

    args = parser.parse_args()

    if args.command == "translate":
        run_translate(args)
    elif args.command == "identity":
        run_identity(args)
    elif args.command == "demo":
        run_demo(args)
    elif args.command == "players":
        run_players(args)
    elif args.command == "app":
        run_app(args)


def run_translate(args: argparse.Namespace) -> None:
    if args.csv:
        df = load_statcast_csv(args.csv)
        df = filter_player(df, args.player)
    else:
        if not args.start_date or not args.end_date:
            raise SystemExit("--start-date and --end-date are required with --mlbam-id.")
        df = fetch_statcast_batter(args.mlbam_id, args.start_date, args.end_date)
    df = filter_home_team(df, args.source_home_team)

    balls = dataframe_to_batted_balls(df)
    parks = load_parks()
    if args.parks:
        requested = set(args.parks)
        missing = sorted(requested - set(parks))
        if missing:
            raise SystemExit(f"Unknown park ids: {', '.join(missing)}")
        parks = {park_id: parks[park_id] for park_id in args.parks}

    summary = translate_balls(
        balls,
        parks,
        distance_tolerance_ft=args.distance_tolerance_ft,
        foul_line_tolerance_deg=args.foul_line_tolerance_deg,
    )
    table = summary_to_dataframe(summary)
    if args.source_home_team:
        source_park_id = TEAM_HOME_PARK_ID.get(args.source_home_team.upper())
        if source_park_id in parks and not table.empty:
            source_park_name = parks[source_park_id].name
            table["method"] = "translated"
            table.loc[table["park"] == source_park_name, "translated_hr"] = (
                summary.actual_home_runs
            )
            table.loc[table["park"] == source_park_name, "expected_hr"] = (
                summary.actual_home_runs
            )
            table.loc[table["park"] == source_park_name, "method"] = "actual"
    if not table.empty:
        sort_column = "expected_hr" if args.probabilistic else "translated_hr"
        table = table.sort_values(
            [sort_column, "park"], ascending=[False, True]
        ).reset_index(drop=True)

    print(f"Rows loaded: {len(balls)}")
    print(f"Batted balls checked: {summary.batted_balls_checked}")
    print(f"Rows skipped: {summary.rows_skipped}")
    print(f"Actual HR in source data: {summary.actual_home_runs}")
    print()
    if table.empty:
        print("No translated home runs found.")
    else:
        print(table.to_string(index=False))


def run_identity(args: argparse.Namespace) -> None:
    if args.details_json:
        detail_rows = json.loads(Path(args.details_json).read_text())
        schedule = (
            load_schedule_file(args.schedule_json)
            if args.schedule_json
            else fetch_schedule(args.year)
        )
        identity = calculate_home_park_identity(
            detail_rows,
            game_context_by_pk(schedule),
            source_team=args.source_team,
            source_teams=tuple(args.source_teams) if args.source_teams else None,
            cat=args.cat,
            player_type=args.player_type,
            game_types=tuple(args.game_types),
        )
    else:
        schedule = load_schedule_file(args.schedule_json) if args.schedule_json else None
        identity = get_home_park_identity(
            player=args.player,
            player_id=args.player_id,
            year=args.year,
            source_team=args.source_team,
            source_teams=tuple(args.source_teams) if args.source_teams else None,
            cat=args.cat,
            player_type=args.player_type,
            game_types=tuple(args.game_types),
            schedule=schedule,
            use_cache=not args.no_cache,
        )

    if args.format == "json":
        print(json.dumps(identity_view_data(identity, args.view), indent=2))
        return
    if args.format == "csv":
        print(identity.to_dataframe().to_csv(index=False), end="")
        return
    if args.format == "html":
        print(render_identity_report(identity.to_dict()), end="")
        return

    print_identity_text(identity, year=args.year, top=args.top, debug=args.debug)


def run_demo(args: argparse.Namespace) -> None:
    identity = load_demo_identity(args.name)
    if args.format == "json":
        print(json.dumps(identity_view_data(identity, args.view), indent=2))
    elif args.format == "csv":
        print(identity.to_dataframe().to_csv(index=False), end="")
    elif args.format == "html":
        print(render_identity_report(identity.to_dict()), end="")
    else:
        print_identity_text(identity, year=identity.season or 2024, top=10, debug=False)


def run_players(args: argparse.Namespace) -> None:
    rows = search_player_rows(
        get_leaderboard(
            year=args.year,
            cat=args.cat,
            player_type=args.player_type,
            use_cache=not args.no_cache,
        ),
        args.query,
        team=args.team,
        limit=args.limit,
    )
    if args.format == "json":
        print(json.dumps(rows, indent=2))
        return
    if not rows:
        print("No players found.")
        return
    for row in rows:
        print(
            f"{row.get('player_id')}  {row.get('player')}  "
            f"{row.get('team_abbrev', '')}  HR={row.get('hr_total', '')}"
        )


def run_app(args: argparse.Namespace) -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise SystemExit("Install the API extra first: python -m pip install -e '.[api]'") from exc

    url = f"http://{args.host}:{args.port}"
    print(f"ParkShift app: {url}")
    if not args.no_open:
        webbrowser.open(url)
    uvicorn.run(
        "parkshift.api:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


def print_identity_text(identity, *, year: int, top: int, debug: bool) -> None:
    print(f"Player: {identity.player_name or identity.player_id or 'Unknown'}")
    print(f"Season: {identity.season or year}")
    source_team_label = "Source teams" if len(identity.source_teams) > 1 else "Source team"
    source_park_label = (
        "Source home parks"
        if len(identity.source_park_names) > 1
        else "Source home park"
    )
    print(f"{source_team_label}: {identity.source_team}")
    print(f"{source_park_label}: {identity.source_park_name}")
    print(f"Mode: {identity.cat}")
    print(f"Game types: {', '.join(identity.game_types) or 'all'}")
    print()
    print(
        "Home HR-candidate batted balls: "
        f"{identity.home_hr_candidate_batted_balls}"
    )
    if identity.season_hr_total is not None:
        print(f"Season HR: {identity.season_hr_total}")
    print(f"Home HR: {identity.actual_home_hr}")
    print(f"Source-park HR: {identity.source_park_hr}")
    print(
        "Source validation: "
        f"{'PASS' if identity.source_park_matches_actual else 'FAIL'}"
    )
    print(f"30-park home split average: {identity.park_average_hr:.1f}")
    effect_label = "Park Added" if identity.player_type == "Pitcher" else "Park Change"
    print(
        f"{effect_label}: {identity.help_hurt:+.1f} HR "
        f"({identity.help_hurt_label})"
    )
    if (
        identity.skipped_missing_game
        or identity.skipped_game_type
        or identity.skipped_neutral_or_alt_site
    ):
        print(
            "Skipped rows: "
            f"{identity.skipped_missing_game} missing game, "
            f"{identity.skipped_game_type} game type, "
            f"{identity.skipped_neutral_or_alt_site} neutral/alternate site"
        )
        if debug:
            print(
                "Skipped game ids: "
                f"missing={','.join(identity.skipped_missing_game_pks) or '-'}; "
                f"game_type={','.join(identity.skipped_game_type_pks) or '-'}; "
                "neutral_or_alternate="
                f"{','.join(identity.skipped_neutral_or_alt_site_pks) or '-'}"
            )
    print()

    rows = [
        {
            "rank": park.rank,
            "park": park.park_name,
            "translated_hr": park.translated_hr,
            "parkshift_score": round(park.parkshift_score, 1),
        }
        for park in identity.parks[:top]
    ]
    try:
        import pandas as pd

        table = pd.DataFrame(rows)
        print(table.to_string(index=False))
    except ImportError:
        for row in rows:
            print(
                f"{row['rank']:>2} {row['park']:<32} "
                f"{row['translated_hr']:>3} {row['parkshift_score']:+.1f}"
            )


def identity_view_data(identity, view: str) -> dict:
    if view == "full":
        return identity.to_dict()
    if view == "help-hurt":
        return identity.help_hurt_view()
    if view == "parkshift-score":
        return identity.parkshift_score_view()
    raise ValueError(f"Unknown identity view: {view}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
    except (IdentityError, SavantHomeRunError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)
