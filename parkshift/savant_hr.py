from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from parkshift.cache import default_cache_dir, load_or_fetch_json


BASEBALL_SAVANT_HOME_RUNS_URL = "https://baseballsavant.mlb.com/leaderboard/home-runs"

SAVANT_PARK_CODES = {
    "laa": "angel",
    "bal": "camden",
    "bos": "fenway",
    "cws": "guaranteed_rate",
    "cle": "progressive",
    "kc": "kauffman",
    "oak": "oakland_coliseum",
    "tb": "tropicana",
    "tex": "globe_life",
    "tor": "rogers_centre",
    "ari": "chase",
    "chc": "wrigley",
    "col": "coors",
    "lad": "dodger",
    "pit": "pnc",
    "mil": "american_family",
    "sea": "t_mobile",
    "hou": "minute_maid",
    "det": "comerica",
    "sf": "oracle",
    "cin": "great_american",
    "sd": "petco",
    "phi": "citizens_bank",
    "stl": "busch",
    "nym": "citi",
    "wsh": "nationals",
    "min": "target",
    "nyy": "yankee",
    "mia": "loan_depot",
    "atl": "truist",
}

_DATA_RE = re.compile(r"\bvar\s+data\s*=\s*(\[.*?\]);", re.DOTALL)


class SavantHomeRunError(ValueError):
    pass


def build_leaderboard_url(
    *,
    year: int,
    cat: str = "xhr",
    player_type: str = "Batter",
    team: str = "",
    min_hr: int = 0,
    csv: bool = False,
) -> str:
    query = {
        "player_type": player_type,
        "team": team,
        "min": str(min_hr),
        "cat": cat,
        "year": str(year),
    }
    if csv:
        query["csv"] = "true"
    return f"{BASEBALL_SAVANT_HOME_RUNS_URL}?{urlencode(query)}"


def build_details_url(
    *, player_id: int | str, year: int, cat: str = "xhr", player_type: str = "Batter"
) -> str:
    query = {
        "type": "details",
        "player_id": str(player_id),
        "year": str(year),
        "player_type": player_type,
        "cat": cat,
    }
    return f"{BASEBALL_SAVANT_HOME_RUNS_URL}?{urlencode(query)}"


def fetch_text(url: str, timeout: float = 30.0) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def fetch_leaderboard(
    *,
    year: int,
    cat: str = "xhr",
    player_type: str = "Batter",
    team: str = "",
    min_hr: int = 0,
    timeout: float = 30.0,
) -> list[dict]:
    url = build_leaderboard_url(
        year=year, cat=cat, player_type=player_type, team=team, min_hr=min_hr
    )
    return extract_leaderboard_data(fetch_text(url, timeout=timeout))


def get_leaderboard(
    *,
    year: int,
    cat: str = "xhr",
    player_type: str = "Batter",
    team: str = "",
    min_hr: int = 0,
    timeout: float = 30.0,
    use_cache: bool = True,
) -> list[dict]:
    cache_path = (
        default_cache_dir()
        / "savant"
        / f"leaderboard_{year}_{cat}_{player_type}_{team or 'all'}_{min_hr}.json"
    )
    return load_or_fetch_json(
        cache_path,
        lambda: fetch_leaderboard(
            year=year,
            cat=cat,
            player_type=player_type,
            team=team,
            min_hr=min_hr,
            timeout=timeout,
        ),
        use_cache=use_cache,
    )


def fetch_details(
    *,
    player_id: int | str,
    year: int,
    cat: str = "xhr",
    player_type: str = "Batter",
    timeout: float = 30.0,
) -> list[dict]:
    url = build_details_url(
        player_id=player_id, year=year, cat=cat, player_type=player_type
    )
    return json.loads(fetch_text(url, timeout=timeout))


def get_details(
    *,
    player_id: int | str,
    year: int,
    cat: str = "xhr",
    player_type: str = "Batter",
    timeout: float = 30.0,
    use_cache: bool = True,
) -> list[dict]:
    cache_path = (
        default_cache_dir()
        / "savant"
        / f"details_{player_id}_{year}_{cat}_{player_type}.json"
    )
    return load_or_fetch_json(
        cache_path,
        lambda: fetch_details(
            player_id=player_id,
            year=year,
            cat=cat,
            player_type=player_type,
            timeout=timeout,
        ),
        use_cache=use_cache,
    )


def extract_leaderboard_data(html: str) -> list[dict]:
    match = _DATA_RE.search(html)
    if not match:
        raise SavantHomeRunError("Could not find embedded `var data = [...]` payload.")
    return json.loads(match.group(1))


def load_leaderboard_file(path: str | Path) -> list[dict]:
    return extract_leaderboard_data(Path(path).read_text())


def row_park_totals(row: dict, *, park_ids: bool = True) -> dict[str, int]:
    totals: dict[str, int] = {}
    for savant_code, park_id in SAVANT_PARK_CODES.items():
        key = park_id if park_ids else savant_code
        value = row.get(savant_code)
        totals[key] = int(value) if value not in (None, "") else 0
    return totals


def detail_park_totals(rows: list[dict], *, park_ids: bool = True) -> dict[str, int]:
    totals = {
        (park_id if park_ids else savant_code): 0
        for savant_code, park_id in SAVANT_PARK_CODES.items()
    }
    for row in rows:
        for savant_code, park_id in SAVANT_PARK_CODES.items():
            key = park_id if park_ids else savant_code
            totals[key] += int(row.get(savant_code) or 0)
    return totals


def find_player_row(
    leaderboard_rows: list[dict], player: str, *, team: str | None = None
) -> dict:
    team_filter = _normalize_team(team) if team else None
    candidates = [
        row
        for row in leaderboard_rows
        if not team_filter or _normalize_team(row.get("team_abbrev")) == team_filter
    ]
    normalized_player = normalize_player_name(player)
    exact_matches = [
        row
        for row in candidates
        if normalize_player_name(str(row.get("player", ""))) == normalized_player
    ]
    if len(exact_matches) == 1:
        return exact_matches[0]
    if len(exact_matches) > 1:
        raise SavantHomeRunError(_ambiguous_player_message(player, exact_matches))

    partial_matches = [
        row
        for row in candidates
        if normalized_player in normalize_player_name(str(row.get("player", "")))
    ]
    if len(partial_matches) == 1:
        return partial_matches[0]
    if len(partial_matches) > 1:
        raise SavantHomeRunError(_ambiguous_player_message(player, partial_matches))

    scope = f" for team {team_filter}" if team_filter else ""
    raise SavantHomeRunError(f"Could not find player `{player}`{scope}.")


def find_player_row_by_id(leaderboard_rows: list[dict], player_id: int | str) -> dict:
    player_id = str(player_id)
    matches = [row for row in leaderboard_rows if str(row.get("player_id")) == player_id]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise SavantHomeRunError(f"Player id `{player_id}` is ambiguous.")
    raise SavantHomeRunError(f"Could not find player id `{player_id}`.")


def search_player_rows(
    leaderboard_rows: list[dict],
    query: str,
    *,
    team: str | None = None,
    limit: int = 10,
) -> list[dict]:
    team_filter = _normalize_team(team) if team else None
    normalized_query = normalize_player_name(query)
    matches = []
    for row in leaderboard_rows:
        if team_filter and _normalize_team(row.get("team_abbrev")) != team_filter:
            continue
        player_name = str(row.get("player", ""))
        normalized_name = normalize_player_name(player_name)
        if normalized_query in normalized_name:
            matches.append(row)
    return matches[:limit]


def normalize_player_name(player: str) -> str:
    ascii_name = (
        unicodedata.normalize("NFKD", player)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    if "," in ascii_name:
        last, first = [part.strip() for part in ascii_name.split(",", 1)]
        ascii_name = f"{first} {last}"
    words = re.findall(r"[a-z0-9]+", ascii_name.lower())
    return " ".join(words)


def _ambiguous_player_message(player: str, rows: list[dict]) -> str:
    options = ", ".join(
        f"{row.get('player')} ({row.get('team_abbrev')}, {row.get('player_id')})"
        for row in rows[:10]
    )
    return f"Player `{player}` is ambiguous. Matches: {options}"


def _normalize_team(team: object) -> str:
    normalized = str(team or "").upper()
    if normalized == "ARI":
        return "AZ"
    if normalized == "ATH":
        return "OAK"
    return normalized
