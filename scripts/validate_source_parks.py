from __future__ import annotations

from dataclasses import dataclass

from parkshift.mlb import TEAM_HOME_PARK_ID
from parkshift.parks import load_parks
from parkshift.statcast import dataframe_to_batted_balls, fetch_statcast_batter, filter_home_team
from parkshift.translator import (
    is_over_wall_home_run,
    source_park_for_ball,
    translate_ball_to_park,
    translate_ball_to_park_probability,
)

START_DATE = "2024-03-28"
END_DATE = "2024-09-29"


@dataclass(frozen=True)
class PlayerSample:
    team: str
    player: str
    mlbam_id: int


PLAYER_SAMPLES = [
    PlayerSample("AZ", "Ketel Marte", 606466),
    PlayerSample("ATL", "Marcell Ozuna", 542303),
    PlayerSample("BAL", "Gunnar Henderson", 683002),
    PlayerSample("BOS", "Rafael Devers", 646240),
    PlayerSample("CHC", "Ian Happ", 664023),
    PlayerSample("CWS", "Andrew Vaughn", 683734),
    PlayerSample("CIN", "Elly De La Cruz", 682829),
    PlayerSample("CLE", "Jose Ramirez", 608070),
    PlayerSample("COL", "Ryan McMahon", 641857),
    PlayerSample("DET", "Riley Greene", 682985),
    PlayerSample("HOU", "Yordan Alvarez", 670541),
    PlayerSample("KC", "Bobby Witt Jr.", 677951),
    PlayerSample("LAA", "Zach Neto", 687263),
    PlayerSample("LAD", "Shohei Ohtani", 660271),
    PlayerSample("MIA", "Jake Burger", 669394),
    PlayerSample("MIL", "William Contreras", 661388),
    PlayerSample("MIN", "Carlos Correa", 621043),
    PlayerSample("NYM", "Pete Alonso", 624413),
    PlayerSample("NYY", "Juan Soto", 665742),
    PlayerSample("ATH", "Brent Rooker", 667670),
    PlayerSample("PHI", "Bryce Harper", 547180),
    PlayerSample("PIT", "Bryan Reynolds", 668804),
    PlayerSample("SD", "Manny Machado", 592518),
    PlayerSample("SEA", "Cal Raleigh", 663728),
    PlayerSample("SF", "Matt Chapman", 656305),
    PlayerSample("STL", "Nolan Arenado", 571448),
    PlayerSample("TB", "Brandon Lowe", 664040),
    PlayerSample("TEX", "Corey Seager", 608369),
    PlayerSample("TOR", "Vladimir Guerrero Jr.", 665489),
    PlayerSample("WSH", "CJ Abrams", 682928),
]


def main() -> None:
    parks = load_parks()
    print(
        "team,park,player,rows,checked_balls,actual_hr,source_result_hr,"
        "pure_model_hr,pure_expected_hr",
        flush=True,
    )
    for sample in PLAYER_SAMPLES:
        park_id = TEAM_HOME_PARK_ID[sample.team]
        park = parks[park_id]
        print(
            f"# fetching {sample.team} {park.name} {sample.player}",
            flush=True,
        )
        df = fetch_statcast_batter(sample.mlbam_id, START_DATE, END_DATE)
        df = filter_home_team(df, sample.team)
        balls = dataframe_to_batted_balls(df)

        checked_balls = 0
        actual_hr = 0
        source_result_hr = 0
        pure_model_hr = 0
        pure_expected_hr = 0.0
        for ball in balls:
            source_park = source_park_for_ball(ball, parks)
            if source_park is not None:
                checked_balls += 1
            if is_over_wall_home_run(ball):
                actual_hr += 1
            source_result = translate_ball_to_park(
                ball,
                park,
                source_park=source_park,
                respect_source_outcome=True,
            )
            pure_result = translate_ball_to_park(
                ball,
                park,
                source_park=source_park,
                respect_source_outcome=False,
            )
            pure_expected_hr += translate_ball_to_park_probability(
                ball,
                park,
                source_park=source_park,
                respect_source_outcome=False,
            )
            if source_result.is_home_run:
                source_result_hr += 1
            if pure_result.is_home_run:
                pure_model_hr += 1

        print(
            f"{sample.team},{park.name},{sample.player},{len(balls)},"
            f"{checked_balls},{actual_hr},{source_result_hr},{pure_model_hr},"
            f"{pure_expected_hr:.1f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
