from __future__ import annotations

import json
from urllib.parse import urlencode

from parkshift.cache import default_cache_dir, load_or_fetch_json
from parkshift.savant_hr import fetch_text


MLB_STATS_URL = "https://statsapi.mlb.com/api/v1/stats"


def build_stats_url(
    *, year: int, group: str, limit: int = 1000, player_pool: str = "all"
) -> str:
    query = {
        "stats": "season",
        "group": group,
        "playerPool": _player_pool_value(player_pool),
        "season": str(year),
        "sortStat": "homeRuns",
        "hydrate": "person,team",
        "limit": str(limit),
    }
    return f"{MLB_STATS_URL}?{urlencode(query)}"


def build_hitting_stats_url(
    *, year: int, limit: int = 1000, player_pool: str = "all"
) -> str:
    return build_stats_url(year=year, group="hitting", limit=limit, player_pool=player_pool)


def build_pitching_stats_url(
    *, year: int, limit: int = 1000, player_pool: str = "all"
) -> str:
    return build_stats_url(year=year, group="pitching", limit=limit, player_pool=player_pool)


def fetch_hitting_stats(
    *, year: int, limit: int = 1000, timeout: float = 30.0, player_pool: str = "all"
) -> dict:
    return json.loads(
        fetch_text(
            build_hitting_stats_url(year=year, limit=limit, player_pool=player_pool),
            timeout=timeout,
        )
    )


def fetch_pitching_stats(
    *, year: int, limit: int = 1000, timeout: float = 30.0, player_pool: str = "all"
) -> dict:
    return json.loads(
        fetch_text(
            build_pitching_stats_url(year=year, limit=limit, player_pool=player_pool),
            timeout=timeout,
        )
    )


def get_hitting_stats(
    *,
    year: int,
    limit: int = 1000,
    timeout: float = 30.0,
    use_cache: bool = True,
    player_pool: str = "all",
) -> dict:
    pool = _player_pool_value(player_pool)
    cache_path = default_cache_dir() / "statsapi" / f"hitting_stats_{year}_{limit}_{pool}.json"
    return load_or_fetch_json(
        cache_path,
        lambda: fetch_hitting_stats(
            year=year, limit=limit, timeout=timeout, player_pool=pool
        ),
        use_cache=use_cache,
    )


def get_pitching_stats(
    *,
    year: int,
    limit: int = 1000,
    timeout: float = 30.0,
    use_cache: bool = True,
    player_pool: str = "all",
) -> dict:
    pool = _player_pool_value(player_pool)
    cache_path = default_cache_dir() / "statsapi" / f"pitching_stats_{year}_{limit}_{pool}.json"
    return load_or_fetch_json(
        cache_path,
        lambda: fetch_pitching_stats(
            year=year, limit=limit, timeout=timeout, player_pool=pool
        ),
        use_cache=use_cache,
    )


def get_regular_season_hr_leaders(
    *, year: int, limit: int = 1000, use_cache: bool = True, player_pool: str = "all"
) -> list[dict]:
    payload = get_hitting_stats(
        year=year,
        limit=max(limit, 1000),
        use_cache=use_cache,
        player_pool=player_pool,
    )
    splits = payload.get("stats", [{}])[0].get("splits", [])
    leaders = []
    for split in splits:
        player = split.get("player") or {}
        team = split.get("team") or {}
        stat = split.get("stat") or {}
        player_id = player.get("id")
        if player_id is None:
            continue
        leaders.append(
            {
                "player_id": str(player_id),
                "player": _player_display_name(player),
                "team_abbrev": str(team.get("abbreviation") or ""),
                "hr_total": int(stat.get("homeRuns") or 0),
            }
        )
    leaders.sort(key=lambda row: (-int(row.get("hr_total") or 0), row.get("player", "")))
    return leaders[:limit]


def regular_season_hr_by_player_id(*, year: int, use_cache: bool = True) -> dict[str, int]:
    return {
        row["player_id"]: int(row.get("hr_total") or 0)
        for row in get_regular_season_hr_leaders(year=year, limit=1000, use_cache=use_cache)
    }


def get_regular_season_pitcher_hr_allowed_leaders(
    *, year: int, limit: int = 1000, use_cache: bool = True, player_pool: str = "all"
) -> list[dict]:
    payload = get_pitching_stats(
        year=year,
        limit=max(limit, 1000),
        use_cache=use_cache,
        player_pool=player_pool,
    )
    splits = payload.get("stats", [{}])[0].get("splits", [])
    leaders = []
    for split in splits:
        player = split.get("player") or {}
        team = split.get("team") or {}
        stat = split.get("stat") or {}
        player_id = player.get("id")
        if player_id is None:
            continue
        leaders.append(
            {
                "player_id": str(player_id),
                "player": _player_display_name(player),
                "team_abbrev": str(team.get("abbreviation") or ""),
                "hr_total": int(stat.get("homeRuns") or 0),
            }
        )
    leaders.sort(key=lambda row: (-int(row.get("hr_total") or 0), row.get("player", "")))
    return leaders[:limit]


def regular_season_pitcher_hr_allowed_by_player_id(
    *, year: int, use_cache: bool = True
) -> dict[str, int]:
    return {
        row["player_id"]: int(row.get("hr_total") or 0)
        for row in get_regular_season_pitcher_hr_allowed_leaders(
            year=year, limit=1000, use_cache=use_cache
        )
    }


def _player_display_name(player: dict) -> str:
    last = str(player.get("lastName") or "").strip()
    first = str(player.get("useName") or player.get("firstName") or "").strip()
    full = str(player.get("fullName") or "").strip()
    if last and first:
        return f"{last}, {first}"
    return full


def _player_pool_value(player_pool: str | None) -> str:
    return "qualified" if str(player_pool or "").strip().lower() == "qualified" else "all"
