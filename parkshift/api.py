from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

from parkshift.cache import default_cache_dir, write_json
from parkshift.cli import identity_view_data
from parkshift.identity import IdentityError, get_home_park_identity
from parkshift.mlb_stats import (
    get_regular_season_hr_leaders,
    get_regular_season_pitcher_hr_allowed_leaders,
    regular_season_hr_by_player_id,
    regular_season_pitcher_hr_allowed_by_player_id,
)
from parkshift.parks import load_parks
from parkshift.savant_hr import (
    SavantHomeRunError,
    get_leaderboard,
    search_player_rows,
)


WEB_DIR = Path(__file__).resolve().parents[1] / "web"
DEFAULT_CAT = "adj_xhr"
MIN_TRANSLATION_YEAR = 2016
MAX_TRANSLATION_YEAR = date.today().year
_IDENTITY_RESPONSE_CACHE: dict[tuple, dict] = {}
IDENTITY_RESPONSE_CACHE_VERSION = "identity_response_v8"
_LAST_IDENTITY_CACHE_STATUS = "unknown"


def identity_payload(
    *,
    year: int,
    player: str | None = None,
    player_id: int | str | None = None,
    source_team: str | None = None,
    source_teams: tuple[str, ...] | None = None,
    cat: str = DEFAULT_CAT,
    player_type: str = "Batter",
    game_types: tuple[str, ...] = ("R",),
    view: str = "full",
    leaderboard_rows: list[dict] | None = None,
    detail_rows: list[dict] | None = None,
    schedule: dict | None = None,
    use_cache: bool = True,
) -> dict:
    validate_year(year)
    identity = get_home_park_identity(
        player=player,
        player_id=player_id,
        year=year,
        source_team=source_team,
        source_teams=source_teams,
        cat=cat,
        player_type=player_type,
        game_types=game_types,
        leaderboard_rows=leaderboard_rows,
        detail_rows=detail_rows,
        schedule=schedule,
        use_cache=use_cache,
    )
    return identity_view_data(identity, view)


def players_payload(
    *,
    query: str,
    year: int,
    cat: str = DEFAULT_CAT,
    player_type: str = "Batter",
    team: str | None = None,
    limit: int = 10,
    use_cache: bool = True,
) -> dict:
    validate_year(year)
    rows = search_player_rows(
        get_leaderboard(
            year=year, cat=cat, player_type=player_type_value(player_type), use_cache=use_cache
        ),
        query,
        team=team,
        limit=limit,
    )
    regular_hr = (
        regular_season_pitcher_hr_allowed_by_player_id(year=year, use_cache=use_cache)
        if is_pitcher_type(player_type)
        else regular_season_hr_by_player_id(year=year, use_cache=use_cache)
    )
    players = [
        {
            "player_id": str(row.get("player_id", "")),
            "player": row.get("player", ""),
            "team_abbrev": row.get("team_abbrev", ""),
            "hr_total": regular_hr.get(str(row.get("player_id", "")), int(row.get("hr_total") or 0)),
        }
        for row in rows
    ]
    return {
        "query": query,
        "season": year,
        "cat": cat,
        "player_type": player_type_value(player_type),
        "players": players,
    }


def leaderboard_payload(
    *,
    year: int,
    cat: str = DEFAULT_CAT,
    player_type: str = "Batter",
    order: str = "high",
    team: str | None = None,
    limit: int = 10,
    min_hr: int = 0,
    use_cache: bool = True,
) -> dict:
    validate_year(year)
    order_value = leaderboard_order_value(order)
    rows = (
        get_regular_season_pitcher_hr_allowed_leaders(
            year=year, limit=1000, use_cache=use_cache, player_pool="qualified"
        )
        if is_pitcher_type(player_type)
        else get_regular_season_hr_leaders(
            year=year, limit=1000, use_cache=use_cache, player_pool="qualified"
        )
    )
    if team:
        rows = [row for row in rows if str(row.get("team_abbrev", "")).upper() == team.upper()]
    if min_hr:
        rows = [row for row in rows if int(row.get("hr_total") or 0) >= min_hr]
    rows = [row for row in rows if int(row.get("hr_total") or 0) >= max(1, min_hr)]
    rows = sorted(
        rows,
        key=lambda row: (
            int(row.get("hr_total") or 0)
            if order_value == "low"
            else -int(row.get("hr_total") or 0),
            row.get("player", ""),
        ),
    )
    players = [
        {
            "player_id": str(row.get("player_id", "")),
            "player": row.get("player", ""),
            "team_abbrev": row.get("team_abbrev", ""),
            "hr_total": int(row.get("hr_total") or 0),
        }
        for row in rows[:limit]
    ]
    return {
        "season": year,
        "cat": cat,
        "player_type": player_type_value(player_type),
        "order": order_value,
        "team": team or "",
        "min_hr": max(1, min_hr),
        "scope": "regular_season",
        "qualified": True,
        "players": players,
    }


def parks_payload() -> dict:
    return {
        "parks": {
            park_id: {
                "park_id": park_id,
                "park_name": park.name,
                "wall": [
                    {
                        "angle_deg": point.angle_deg,
                        "distance_ft": point.distance_ft,
                        "height_ft": point.height_ft,
                    }
                    for point in park.wall
                ],
            }
            for park_id, park in load_parks().items()
        }
    }


def validate_year(year: int) -> None:
    if year < MIN_TRANSLATION_YEAR:
        raise ValueError(
            f"ParkShift supports seasons from {MIN_TRANSLATION_YEAR} forward. "
            "Savant Home Run Tracker detail rows are not available for 2015 or earlier."
        )
    if year > MAX_TRANSLATION_YEAR:
        raise ValueError(
            f"ParkShift supports seasons through {MAX_TRANSLATION_YEAR}. "
            "Future seasons do not have Savant Home Run Tracker detail rows yet."
        )


def is_pitcher_type(player_type: str | None) -> bool:
    return str(player_type or "").strip().lower() in {"pitcher", "pitchers", "p"}


def player_type_value(player_type: str | None) -> str:
    return "Pitcher" if is_pitcher_type(player_type) else "Batter"


def leaderboard_order_value(order: str | None) -> str:
    return "low" if str(order or "").strip().lower() == "low" else "high"


def identity_cache_key(
    *,
    year: int,
    player: str | None = None,
    player_id: int | str | None = None,
    source_team: str | None = None,
    source_teams: tuple[str, ...] | None = None,
    cat: str = DEFAULT_CAT,
    player_type: str = "Batter",
    game_types: tuple[str, ...] = ("R",),
    view: str = "full",
) -> tuple:
    return (
        str(player or ""),
        str(player_id or ""),
        int(year),
        str(source_team or ""),
        tuple(source_teams or ()),
        cat,
        player_type_value(player_type),
        tuple(game_types),
        view,
    )


def cached_identity_payload(
    *,
    year: int,
    player: str | None = None,
    player_id: int | str | None = None,
    source_team: str | None = None,
    source_teams: tuple[str, ...] | None = None,
    cat: str = DEFAULT_CAT,
    player_type: str = "Batter",
    game_types: tuple[str, ...] = ("R",),
    view: str = "full",
    use_cache: bool = True,
) -> dict:
    global _LAST_IDENTITY_CACHE_STATUS
    key = identity_cache_key(
        player=player,
        player_id=player_id,
        year=year,
        source_team=source_team,
        source_teams=source_teams,
        cat=cat,
        player_type=player_type,
        game_types=game_types,
        view=view,
    )
    if use_cache and key in _IDENTITY_RESPONSE_CACHE:
        _LAST_IDENTITY_CACHE_STATUS = "memory"
        return _IDENTITY_RESPONSE_CACHE[key]
    disk_cache_path = identity_response_cache_path(key)
    if use_cache and disk_cache_path.exists():
        payload = json.loads(disk_cache_path.read_text())
        _IDENTITY_RESPONSE_CACHE[key] = payload
        _LAST_IDENTITY_CACHE_STATUS = "disk"
        return payload
    payload = identity_payload(
        player=player,
        player_id=player_id,
        year=year,
        source_team=source_team,
        source_teams=source_teams,
        cat=cat,
        player_type=player_type,
        game_types=game_types,
        view=view,
        use_cache=use_cache,
    )
    if use_cache:
        _IDENTITY_RESPONSE_CACHE[key] = payload
        write_json(disk_cache_path, payload)
        _LAST_IDENTITY_CACHE_STATUS = "miss"
    else:
        _LAST_IDENTITY_CACHE_STATUS = "bypass"
    return payload


def identity_response_cache_path(key: tuple) -> Path:
    digest = hashlib.sha256(
        json.dumps(key, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return default_cache_dir() / "api" / f"{IDENTITY_RESPONSE_CACHE_VERSION}_{digest}.json"


def create_app():
    try:
        from fastapi import FastAPI, HTTPException, Query
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi import Response
        from fastapi.responses import FileResponse
        from fastapi.responses import JSONResponse
    except ImportError as exc:
        raise RuntimeError(
            "FastAPI is required for the API app. Install with `pip install -e .[api]`."
        ) from exc

    app = FastAPI(title="ParkShift API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/", include_in_schema=False)
    def frontend_index():
        return FileResponse(WEB_DIR / "index.html")

    @app.get("/app.js", include_in_schema=False)
    def frontend_script():
        return FileResponse(WEB_DIR / "app.js", media_type="text/javascript")

    @app.get("/styles.css", include_in_schema=False)
    def frontend_styles():
        return FileResponse(WEB_DIR / "styles.css", media_type="text/css")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(status_code=204)

    @app.exception_handler(IdentityError)
    def identity_error_handler(request, exc):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.exception_handler(SavantHomeRunError)
    def savant_error_handler(request, exc):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.exception_handler(ValueError)
    def value_error_handler(request, exc):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.get("/identity")
    def identity_endpoint(
        year: int,
        player: str | None = None,
        player_id: str | None = None,
        source_team: str | None = None,
        source_teams: list[str] | None = Query(default=None),
        cat: str = DEFAULT_CAT,
        player_type: str = "Batter",
        game_types: list[str] = Query(default=["R"]),
        view: str = "full",
        no_cache: bool = False,
    ):
        if view not in {"full", "help-hurt", "parkshift-score"}:
            raise HTTPException(
                status_code=400,
                detail="view must be one of: full, help-hurt, parkshift-score",
            )
        payload = cached_identity_payload(
            player=player,
            player_id=player_id,
            year=year,
            source_team=source_team,
            source_teams=tuple(source_teams) if source_teams else None,
            cat=cat,
            player_type=player_type,
            game_types=tuple(game_types),
            view=view,
            use_cache=not no_cache,
        )
        return JSONResponse(
            content=payload,
            headers={"X-ParkShift-Cache": _LAST_IDENTITY_CACHE_STATUS},
        )

    @app.get("/players")
    def players_endpoint(
        query: str,
        year: int,
        cat: str = DEFAULT_CAT,
        player_type: str = "Batter",
        team: str | None = None,
        limit: int = 10,
        no_cache: bool = False,
    ) -> dict:
        if not query.strip():
            raise HTTPException(status_code=400, detail="query is required")
        if limit < 1 or limit > 25:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 25")
        return players_payload(
            query=query,
            year=year,
            cat=cat,
            player_type=player_type,
            team=team,
            limit=limit,
            use_cache=not no_cache,
        )

    @app.get("/leaderboard")
    def leaderboard_endpoint(
        year: int,
        cat: str = DEFAULT_CAT,
        player_type: str = "Batter",
        order: str = "high",
        team: str | None = None,
        limit: int = 10,
        min_hr: int = 0,
        no_cache: bool = False,
    ) -> dict:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
        if min_hr < 0:
            raise HTTPException(status_code=400, detail="min_hr must be 0 or greater")
        return leaderboard_payload(
            year=year,
            cat=cat,
            player_type=player_type,
            order=order,
            team=team,
            limit=limit,
            min_hr=min_hr,
            use_cache=not no_cache,
        )

    @app.get("/parks")
    def parks_endpoint() -> dict:
        return parks_payload()

    @app.get("/identity/help-hurt")
    def help_hurt_endpoint(
        year: int,
        player: str | None = None,
        player_id: str | None = None,
        source_team: str | None = None,
        source_teams: list[str] | None = Query(default=None),
        cat: str = DEFAULT_CAT,
        player_type: str = "Batter",
        game_types: list[str] = Query(default=["R"]),
        no_cache: bool = False,
    ) -> dict:
        return identity_endpoint(
            year=year,
            player=player,
            player_id=player_id,
            source_team=source_team,
            source_teams=source_teams,
            cat=cat,
            player_type=player_type,
            game_types=game_types,
            view="help-hurt",
            no_cache=no_cache,
        )

    @app.get("/identity/parkshift-score")
    def parkshift_score_endpoint(
        year: int,
        player: str | None = None,
        player_id: str | None = None,
        source_team: str | None = None,
        source_teams: list[str] | None = Query(default=None),
        cat: str = DEFAULT_CAT,
        player_type: str = "Batter",
        game_types: list[str] = Query(default=["R"]),
        no_cache: bool = False,
    ) -> dict:
        return identity_endpoint(
            year=year,
            player=player,
            player_id=player_id,
            source_team=source_team,
            source_teams=source_teams,
            cat=cat,
            player_type=player_type,
            game_types=game_types,
            view="parkshift-score",
            no_cache=no_cache,
        )

    return app
