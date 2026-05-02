from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen

from parkshift.cache import default_cache_dir, load_or_fetch_json
from parkshift.geometry import spray_angle_from_hc


STATSAPI_GAME_FEED_URL = "https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"


def build_game_feed_url(game_pk: int | str) -> str:
    return STATSAPI_GAME_FEED_URL.format(game_pk=str(game_pk))


def fetch_game_feed(game_pk: int | str, timeout: float = 30.0) -> dict:
    request = Request(
        build_game_feed_url(game_pk),
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def get_game_feed(
    game_pk: int | str,
    *,
    timeout: float = 30.0,
    use_cache: bool = True,
) -> dict:
    cache_path = default_cache_dir() / "statsapi" / f"game_{game_pk}.json"
    return load_or_fetch_json(
        cache_path,
        lambda: fetch_game_feed(game_pk, timeout=timeout),
        use_cache=use_cache,
    )


def get_play_metadata_by_id(
    game_pks: list[str] | tuple[str, ...],
    *,
    timeout: float = 30.0,
    use_cache: bool = True,
) -> dict[str, dict]:
    metadata: dict[str, dict] = {}
    unique_game_pks = tuple(dict.fromkeys(str(game_pk) for game_pk in game_pks if game_pk))
    if not unique_game_pks:
        return metadata

    worker_count = min(12, len(unique_game_pks))
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = {
            executor.submit(
                get_game_feed,
                game_pk,
                timeout=timeout,
                use_cache=use_cache,
            ): game_pk
            for game_pk in unique_game_pks
        }
        for future in as_completed(futures):
            feed = future.result()
            metadata.update(extract_play_metadata(feed))

    return metadata


def extract_play_metadata(feed: dict) -> dict[str, dict]:
    metadata: dict[str, dict] = {}
    teams = feed.get("gameData", {}).get("teams", {})
    away_team = _optional_str((teams.get("away") or {}).get("abbreviation"))
    home_team = _optional_str((teams.get("home") or {}).get("abbreviation"))
    plays = feed.get("liveData", {}).get("plays", {}).get("allPlays", [])
    for play in plays:
        result = play.get("result", {})
        about = play.get("about", {})
        batting_team = away_team if about.get("isTopInning") else home_team
        pitching_team = home_team if about.get("isTopInning") else away_team
        for event in play.get("playEvents", []):
            play_id = event.get("playId")
            if not play_id:
                continue
            hit_data = event.get("hitData") or {}
            coordinates = hit_data.get("coordinates") or {}
            coord_x = _optional_float(coordinates.get("coordX"))
            coord_y = _optional_float(coordinates.get("coordY"))
            metadata[str(play_id)] = {
                "coord_x": coord_x,
                "coord_y": coord_y,
                "spray_angle_deg": spray_angle_from_hc(coord_x, coord_y),
                "distance_ft": _optional_int(hit_data.get("totalDistance")),
                "launch_angle": _optional_int(hit_data.get("launchAngle")),
                "exit_velocity": _optional_float(hit_data.get("launchSpeed")),
                "description": result.get("description"),
                "event_type": result.get("eventType"),
                "batting_team": batting_team,
                "pitching_team": pitching_team,
            }
    return metadata


def _optional_str(value: object) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _optional_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    return int(round(float(value)))


def _optional_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    return float(value)
