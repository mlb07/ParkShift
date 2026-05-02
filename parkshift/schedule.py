from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode

from parkshift.cache import default_cache_dir, load_or_fetch_json
from parkshift.savant_hr import fetch_text


MLB_SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule"

TEAM_ID_TO_ABBREV = {
    108: "LAA",
    109: "AZ",
    110: "BAL",
    111: "BOS",
    112: "CHC",
    113: "CIN",
    114: "CLE",
    115: "COL",
    116: "DET",
    117: "HOU",
    118: "KC",
    119: "LAD",
    120: "WSH",
    121: "NYM",
    133: "OAK",
    134: "PIT",
    135: "SD",
    136: "SEA",
    137: "SF",
    138: "STL",
    139: "TB",
    140: "TEX",
    141: "TOR",
    142: "MIN",
    143: "PHI",
    144: "ATL",
    145: "CWS",
    146: "MIA",
    147: "NYY",
    158: "MIL",
}

VENUE_ID_TO_SAVANT_CODE = {
    1: "laa",
    15: "ari",
    2: "bal",
    3: "bos",
    17: "chc",
    2602: "cin",
    5: "cle",
    19: "col",
    2394: "det",
    2392: "hou",
    7: "kc",
    22: "lad",
    3309: "wsh",
    3289: "nym",
    10: "oak",
    31: "pit",
    2680: "sd",
    680: "sea",
    2395: "sf",
    2889: "stl",
    12: "tb",
    5325: "tex",
    14: "tor",
    3312: "min",
    2681: "phi",
    4705: "atl",
    4: "cws",
    4169: "mia",
    3313: "nyy",
    32: "mil",
}


@dataclass(frozen=True)
class GameContext:
    game_pk: str
    game_type: str
    home_team: str
    away_team: str
    venue_id: int
    venue_name: str
    savant_park_code: str | None


def build_schedule_url(year: int) -> str:
    query = {
        "sportId": "1",
        "startDate": f"{year}-03-01",
        "endDate": f"{year}-11-30",
        "gameTypes": "R,F,D,L,W",
    }
    return f"{MLB_SCHEDULE_URL}?{urlencode(query)}"


def fetch_schedule(year: int, timeout: float = 30.0) -> dict:
    return json.loads(fetch_text(build_schedule_url(year), timeout=timeout))


def get_schedule(year: int, timeout: float = 30.0, use_cache: bool = True) -> dict:
    cache_path = default_cache_dir() / "schedule" / f"mlb_schedule_{year}.json"
    return load_or_fetch_json(
        cache_path,
        lambda: fetch_schedule(year, timeout=timeout),
        use_cache=use_cache,
    )


def load_schedule_file(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def game_context_by_pk(schedule: dict) -> dict[str, GameContext]:
    games: dict[str, GameContext] = {}
    for date in schedule.get("dates", []):
        for game in date.get("games", []):
            home_team_id = int(game["teams"]["home"]["team"]["id"])
            away_team_id = int(game["teams"]["away"]["team"]["id"])
            venue_id = int(game["venue"]["id"])
            games[str(game["gamePk"])] = GameContext(
                game_pk=str(game["gamePk"]),
                game_type=str(game["gameType"]),
                home_team=TEAM_ID_TO_ABBREV[home_team_id],
                away_team=TEAM_ID_TO_ABBREV[away_team_id],
                venue_id=venue_id,
                venue_name=str(game["venue"]["name"]),
                savant_park_code=VENUE_ID_TO_SAVANT_CODE.get(venue_id),
            )
    return games
