from __future__ import annotations

from dataclasses import dataclass

from parkshift.mlb import TEAM_HOME_PARK_ID
from parkshift.parks import load_parks
from parkshift.savant_hr import (
    SAVANT_PARK_CODES,
    SavantHomeRunError,
    find_player_row,
    find_player_row_by_id,
    get_details,
    get_leaderboard,
)
from parkshift.schedule import GameContext, game_context_by_pk, get_schedule
from parkshift.statsapi import get_play_metadata_by_id


PARK_ID_TO_SAVANT_CODE = {park_id: code for code, park_id in SAVANT_PARK_CODES.items()}
IDENTITY_CONTRACT_VERSION = "1.0"
DETAIL_ROW_TEAM_FIELDS = (
    "team_abbrev",
    "batter_team",
    "batting_team",
    "bat_team",
    "team",
)
PITCHER_DETAIL_ROW_TEAM_FIELDS = (
    "team_abbrev",
    "pitcher_team",
    "pitching_team",
    "team",
)


class IdentityError(ValueError):
    pass


class NoHomeRowsError(IdentityError):
    pass


class NoDetailRowsError(IdentityError):
    pass


class SourceTeamInferenceError(IdentityError):
    pass


@dataclass(frozen=True)
class ParkShiftHomeRunMarker:
    play_id: str | None
    game_pk: str
    game_date: str | None
    result: str | None
    source_park_id: str
    source_park_name: str
    distance_ft: int | None
    launch_angle: int | None
    exit_velocity: float | None
    spray_angle_deg: float | None
    coord_x: float | None
    coord_y: float | None
    coordinate_source: str | None

    def to_dict(self) -> dict:
        return {
            "play_id": self.play_id,
            "game_pk": self.game_pk,
            "game_date": self.game_date,
            "distance_ft": self.distance_ft,
            "launch_angle": self.launch_angle,
            "exit_velocity": self.exit_velocity,
            "spray_angle_deg": self.spray_angle_deg,
        }


@dataclass(frozen=True)
class ParkShiftParkResult:
    rank: int
    park_id: str
    park_name: str
    savant_code: str
    translated_hr: int
    projected_total_hr: int | None
    parkshift_score: float
    home_runs: tuple[ParkShiftHomeRunMarker, ...] = ()

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "park_id": self.park_id,
            "park_name": self.park_name,
            "savant_code": self.savant_code,
            "translated_hr": self.translated_hr,
            "projected_total_hr": self.projected_total_hr,
            "parkshift_score": self.parkshift_score,
            "home_runs": [marker.to_dict() for marker in self.home_runs],
        }


@dataclass(frozen=True)
class HomeParkIdentity:
    player_type: str
    player_id: str | None
    player_name: str | None
    season: int | None
    source_team: str
    source_teams: tuple[str, ...]
    source_park_id: str
    source_park_ids: tuple[str, ...]
    source_park_name: str
    source_park_names: tuple[str, ...]
    cat: str
    game_types: tuple[str, ...]
    home_relevant_batted_balls: int
    season_hr_total: int | None
    non_source_home_hr: int | None
    actual_home_hr: int
    source_park_hr: int
    source_park_matches_actual: bool
    park_average_hr: float
    help_hurt: float
    help_hurt_label: str
    skipped_missing_game: int
    skipped_game_type: int
    skipped_neutral_or_alt_site: int
    skipped_missing_game_pks: tuple[str, ...]
    skipped_game_type_pks: tuple[str, ...]
    skipped_neutral_or_alt_site_pks: tuple[str, ...]
    parks: tuple[ParkShiftParkResult, ...]

    @property
    def home_hr_candidate_batted_balls(self) -> int:
        return self.home_relevant_batted_balls

    @property
    def source_park_result(self) -> ParkShiftParkResult:
        if len(self.source_park_ids) != 1:
            raise ValueError("Multiple source parks are present.")
        for park in self.parks:
            if park.park_id == self.source_park_id:
                return park
        raise ValueError(f"Source park {self.source_park_id} missing from results.")

    @property
    def source_park_results(self) -> tuple[ParkShiftParkResult, ...]:
        by_park_id = {park.park_id: park for park in self.parks}
        return tuple(by_park_id[park_id] for park_id in self.source_park_ids)

    def top_parks(self, count: int = 5) -> tuple[ParkShiftParkResult, ...]:
        return self.parks[:count]

    def bottom_parks(self, count: int = 5) -> tuple[ParkShiftParkResult, ...]:
        if count <= 0:
            return ()
        return self.parks[-count:]

    def park(self, park_id: str) -> ParkShiftParkResult:
        for park in self.parks:
            if park.park_id == park_id:
                return park
        raise KeyError(park_id)

    def help_hurt_view(self) -> dict:
        return {
            "contract_version": IDENTITY_CONTRACT_VERSION,
            "player_type": self.player_type,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "season": self.season,
            "source_team": self.source_team,
            "source_teams": list(self.source_teams),
            "source_park_id": self.source_park_id,
            "source_park_ids": list(self.source_park_ids),
            "source_park_name": self.source_park_name,
            "source_park_names": list(self.source_park_names),
            "home_hr_candidate_batted_balls": self.home_hr_candidate_batted_balls,
            "season_hr_total": self.season_hr_total,
            "non_source_home_hr": self.non_source_home_hr,
            "actual_home_hr": self.actual_home_hr,
            "source_park_hr": self.source_park_hr,
            "source_park_matches_actual": self.source_park_matches_actual,
            "park_average_hr": self.park_average_hr,
            "help_hurt": self.help_hurt,
            "help_hurt_label": self.help_hurt_label,
        }

    def parkshift_score_view(self) -> dict:
        return {
            "contract_version": IDENTITY_CONTRACT_VERSION,
            "player_type": self.player_type,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "season": self.season,
            "source_team": self.source_team,
            "source_teams": list(self.source_teams),
            "source_park_id": self.source_park_id,
            "source_park_ids": list(self.source_park_ids),
            "source_park_name": self.source_park_name,
            "source_park_names": list(self.source_park_names),
            "season_hr_total": self.season_hr_total,
            "non_source_home_hr": self.non_source_home_hr,
            "park_average_hr": self.park_average_hr,
            "parks": [park.to_dict() for park in self.parks],
        }

    def to_dataframe(self):
        import pandas as pd

        source_park_ids = set(self.source_park_ids)
        rows = []
        for park in self.parks:
            row = park.to_dict()
            row.pop("home_runs", None)
            row["is_source_park"] = park.park_id in source_park_ids
            row["projected_total_hr"] = park.projected_total_hr
            row["park_average_hr"] = self.park_average_hr
            row["season_hr_total"] = self.season_hr_total
            row["non_source_home_hr"] = self.non_source_home_hr
            row["source_team"] = self.source_team
            row["source_teams"] = ",".join(self.source_teams)
            row["player_type"] = self.player_type
            row["player_id"] = self.player_id
            row["player_name"] = self.player_name
            row["season"] = self.season
            rows.append(row)
        return pd.DataFrame(rows)

    def to_dict(self) -> dict:
        return {
            "contract_version": IDENTITY_CONTRACT_VERSION,
            "player_type": self.player_type,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "season": self.season,
            "source_team": self.source_team,
            "source_teams": list(self.source_teams),
            "source_park_id": self.source_park_id,
            "source_park_ids": list(self.source_park_ids),
            "source_park_name": self.source_park_name,
            "source_park_names": list(self.source_park_names),
            "cat": self.cat,
            "game_types": list(self.game_types),
            "home_hr_candidate_batted_balls": self.home_hr_candidate_batted_balls,
            "season_hr_total": self.season_hr_total,
            "non_source_home_hr": self.non_source_home_hr,
            "actual_home_hr": self.actual_home_hr,
            "source_park_hr": self.source_park_hr,
            "source_park_matches_actual": self.source_park_matches_actual,
            "park_average_hr": self.park_average_hr,
            "help_hurt": self.help_hurt,
            "help_hurt_label": self.help_hurt_label,
            "skipped_missing_game": self.skipped_missing_game,
            "skipped_game_type": self.skipped_game_type,
            "skipped_neutral_or_alt_site": self.skipped_neutral_or_alt_site,
            "skipped_missing_game_pks": list(self.skipped_missing_game_pks),
            "skipped_game_type_pks": list(self.skipped_game_type_pks),
            "skipped_neutral_or_alt_site_pks": list(
                self.skipped_neutral_or_alt_site_pks
            ),
            "source_park_result": (
                self.source_park_result.to_dict()
                if len(self.source_park_ids) == 1
                else None
            ),
            "source_park_results": [
                park.to_dict() for park in self.source_park_results
            ],
            "parks": [park.to_dict() for park in self.parks],
        }


def get_home_park_identity(
    *,
    player: str | None = None,
    player_id: int | str | None = None,
    year: int,
    source_team: str | None = None,
    source_teams: tuple[str, ...] | None = None,
    cat: str = "xhr",
    player_type: str = "Batter",
    game_types: tuple[str, ...] = ("R",),
    leaderboard_rows: list[dict] | None = None,
    detail_rows: list[dict] | None = None,
    schedule: dict | None = None,
    use_cache: bool = True,
    require_home_rows: bool = True,
    enrich_play_metadata: bool = True,
) -> HomeParkIdentity:
    player_type = normalize_player_type(player_type)
    leaderboard_team: str | None = None
    if detail_rows is None:
        resolved_player_id = str(player_id) if player_id is not None else None
        leaderboard = leaderboard_rows
        if resolved_player_id is None:
            if not player:
                raise ValueError("Either player, player_id, or detail_rows is required.")
            leaderboard = leaderboard or get_leaderboard(
                year=year,
                cat=cat,
                player_type=player_type,
                use_cache=use_cache,
            )
            player_row = find_player_row(leaderboard, player)
            resolved_player_id = str(player_row["player_id"])
            leaderboard_team = _optional_str(player_row.get("team_abbrev"))
        elif source_team is None and source_teams is None:
            leaderboard = leaderboard or get_leaderboard(
                year=year,
                cat=cat,
                player_type=player_type,
                use_cache=use_cache,
            )
            try:
                player_row = find_player_row_by_id(leaderboard, resolved_player_id)
                leaderboard_team = _optional_str(player_row.get("team_abbrev"))
            except SavantHomeRunError:
                leaderboard_team = None
        detail_rows = get_details(
            player_id=resolved_player_id,
            year=year,
            cat=cat,
            player_type=player_type,
            use_cache=use_cache,
        )

    resolved_schedule = schedule or get_schedule(year, use_cache=use_cache)
    games = game_context_by_pk(resolved_schedule)
    play_metadata_by_id = (
        _safe_play_metadata(detail_rows, use_cache=use_cache)
        if enrich_play_metadata
        else {}
    )
    if source_team or source_teams is not None:
        return calculate_home_park_identity(
            detail_rows,
            games,
            source_team=source_team,
            source_teams=source_teams,
            cat=cat,
            player_type=player_type,
            game_types=game_types,
            require_home_rows=require_home_rows,
            play_metadata_by_id=play_metadata_by_id,
        )
    try:
        return calculate_home_park_identity(
            detail_rows,
            games,
            cat=cat,
            player_type=player_type,
            game_types=game_types,
            require_home_rows=require_home_rows,
            play_metadata_by_id=play_metadata_by_id,
        )
    except SourceTeamInferenceError:
        if not leaderboard_team:
            raise
        return calculate_home_park_identity(
            detail_rows,
            games,
            source_team=leaderboard_team,
            cat=cat,
            player_type=player_type,
            game_types=game_types,
            require_home_rows=require_home_rows,
            play_metadata_by_id=play_metadata_by_id,
        )


def calculate_home_park_identity(
    detail_rows: list[dict],
    games: dict[str, GameContext],
    *,
    source_team: str | None = None,
    source_teams: tuple[str, ...] | None = None,
    cat: str = "xhr",
    player_type: str = "Batter",
    game_types: tuple[str, ...] = ("R",),
    require_home_rows: bool = True,
    play_metadata_by_id: dict[str, dict] | None = None,
) -> HomeParkIdentity:
    player_type = normalize_player_type(player_type)
    if require_home_rows and not detail_rows:
        raise NoDetailRowsError(
            "No Savant Home Run Tracker detail rows found. "
            "Check the player, year, and cat mode, or pass a details JSON file "
            "that contains at least one row."
        )

    allowed_game_types = tuple(game_type.upper() for game_type in game_types)
    teams = _resolve_source_teams(
        detail_rows,
        games,
        source_team=source_team,
        source_teams=source_teams,
        allowed_game_types=allowed_game_types,
        player_type=player_type,
        play_metadata_by_id=play_metadata_by_id,
    )
    unknown_teams = [team for team in teams if team not in TEAM_HOME_PARK_ID]
    if unknown_teams:
        raise ValueError(
            f"Unknown source team: {', '.join(unknown_teams)}. "
            "Use MLB abbreviations such as NYY, LAD, MIA, or AZ."
        )

    source_park_ids = tuple(TEAM_HOME_PARK_ID[team] for team in teams)
    source_savant_codes = {
        team: PARK_ID_TO_SAVANT_CODE[TEAM_HOME_PARK_ID[team]] for team in teams
    }
    parks = load_parks()
    totals = {park_id: 0 for park_id in parks}
    home_runs_by_park: dict[str, list[ParkShiftHomeRunMarker]] = {
        park_id: [] for park_id in parks
    }
    season_hr_total = 0
    actual_home_hr = 0
    source_park_hr = 0
    home_rows = 0
    skipped_missing_game = 0
    skipped_game_type = 0
    skipped_neutral_or_alt_site = 0
    skipped_missing_game_pks: list[str] = []
    skipped_game_type_pks: list[str] = []
    skipped_neutral_or_alt_site_pks: list[str] = []

    for row in detail_rows:
        game_pk = str(row["game_pk"])
        game = games.get(game_pk)
        if game is None:
            skipped_missing_game += 1
            skipped_missing_game_pks.append(game_pk)
            continue
        if allowed_game_types and game.game_type.upper() not in allowed_game_types:
            skipped_game_type += 1
            skipped_game_type_pks.append(game_pk)
            continue
        season_hr_total += int(row.get("result") == "home_run")
        row_team = _team_for_row(row, player_type, play_metadata_by_id or {})
        if row_team is not None and row_team != game.home_team:
            continue
        if game.home_team not in teams:
            continue
        source_savant_code = source_savant_codes[game.home_team]
        if game.savant_park_code != source_savant_code:
            skipped_neutral_or_alt_site += 1
            skipped_neutral_or_alt_site_pks.append(game_pk)
            continue

        home_rows += 1
        actual_home_hr += int(row.get("result") == "home_run")
        source_park_hr += int(row.get(source_savant_code) or 0)
        for savant_code, park_id in SAVANT_PARK_CODES.items():
            clears_park = int(row.get(savant_code) or 0)
            totals[park_id] += clears_park
            if clears_park:
                home_runs_by_park[park_id].append(
                    _home_run_marker(
                        row,
                        game=game,
                        source_park_id=TEAM_HOME_PARK_ID[game.home_team],
                        source_park_name=parks[TEAM_HOME_PARK_ID[game.home_team]].name,
                        metadata=(
                            play_metadata_by_id or {}
                        ).get(str(row.get("play_id"))),
                    )
                )

    if require_home_rows and home_rows == 0:
        player_name = _player_name_from_row(detail_rows[0], player_type) if detail_rows else "Unknown"
        source_label = "source team" if len(teams) == 1 else "source teams"
        raise NoHomeRowsError(
            f"No home HR-candidate batted balls found for {player_name} "
            f"with {source_label} {', '.join(teams)} "
            f"and game types {', '.join(allowed_game_types)}. "
            "Check that the source team matches the player's team for that "
            "season, or use source_teams/--source-teams for traded players."
        )

    if not totals:
        park_average_hr = 0.0
    else:
        park_average_hr = sum(totals.values()) / len(totals)
    help_hurt = source_park_hr - park_average_hr
    non_source_home_hr = season_hr_total - actual_home_hr

    if player_type == "Pitcher":
        ranked = sorted(
            totals.items(),
            key=lambda item: (
                item[1] - park_average_hr,
                item[1],
                parks[item[0]].name,
            ),
        )
    else:
        ranked = sorted(
            totals.items(),
            key=lambda item: (
                -(item[1] - park_average_hr),
                -item[1],
                parks[item[0]].name,
            ),
        )
    park_results = tuple(
        ParkShiftParkResult(
            rank=index,
            park_id=park_id,
            park_name=parks[park_id].name,
            savant_code=PARK_ID_TO_SAVANT_CODE[park_id],
            translated_hr=translated_hr,
            projected_total_hr=non_source_home_hr + translated_hr,
            parkshift_score=translated_hr - park_average_hr,
            home_runs=tuple(home_runs_by_park[park_id]),
        )
        for index, (park_id, translated_hr) in enumerate(ranked, start=1)
    )

    first_row = detail_rows[0] if detail_rows else {}
    source_park_names = tuple(parks[park_id].name for park_id in source_park_ids)
    return HomeParkIdentity(
        player_type=player_type,
        player_id=_player_id_from_row(first_row, player_type),
        player_name=_player_name_from_row(first_row, player_type),
        season=_optional_int(first_row.get("year")),
        source_team=",".join(teams),
        source_teams=teams,
        source_park_id=source_park_ids[0] if len(source_park_ids) == 1 else "multiple",
        source_park_ids=source_park_ids,
        source_park_name=source_park_names[0]
        if len(source_park_names) == 1
        else "Multiple source parks",
        source_park_names=source_park_names,
        cat=cat,
        game_types=allowed_game_types,
        home_relevant_batted_balls=home_rows,
        season_hr_total=season_hr_total,
        non_source_home_hr=non_source_home_hr,
        actual_home_hr=actual_home_hr,
        source_park_hr=source_park_hr,
        source_park_matches_actual=source_park_hr == actual_home_hr,
        park_average_hr=park_average_hr,
        help_hurt=help_hurt,
        help_hurt_label=park_effect_label(help_hurt, player_type),
        skipped_missing_game=skipped_missing_game,
        skipped_game_type=skipped_game_type,
        skipped_neutral_or_alt_site=skipped_neutral_or_alt_site,
        skipped_missing_game_pks=tuple(skipped_missing_game_pks),
        skipped_game_type_pks=tuple(skipped_game_type_pks),
        skipped_neutral_or_alt_site_pks=tuple(skipped_neutral_or_alt_site_pks),
        parks=park_results,
    )


def help_hurt_label(value: float) -> str:
    if value >= 3.0:
        return "Strong Help"
    if value >= 1.0:
        return "Help"
    if value <= -3.0:
        return "Strong Hurt"
    if value <= -1.0:
        return "Hurt"
    return "Neutral"


def park_effect_label(value: float, player_type: str) -> str:
    if normalize_player_type(player_type) != "Pitcher":
        return help_hurt_label(value)
    if value >= 3.0:
        return "Strong Added"
    if value >= 1.0:
        return "Added"
    if value <= -3.0:
        return "Strong Saved"
    if value <= -1.0:
        return "Saved"
    return "Neutral"


def normalize_player_type(player_type: str | None) -> str:
    normalized = str(player_type or "Batter").strip().lower()
    if normalized in {"pitcher", "pitchers", "p"}:
        return "Pitcher"
    return "Batter"


def _normalize_team(team: str) -> str:
    normalized = team.upper()
    if normalized == "ARI":
        return "AZ"
    if normalized == "ATH":
        return "OAK"
    return normalized


def _normalize_source_teams(
    *, source_team: str | None, source_teams: tuple[str, ...] | None
) -> tuple[str, ...]:
    if source_team and source_teams:
        raise ValueError("Pass source_team or source_teams, not both.")
    raw_teams = source_teams if source_teams is not None else (source_team,)
    teams = tuple(_normalize_team(team) for team in raw_teams if team)
    if not teams:
        raise ValueError("At least one source team is required.")
    return tuple(dict.fromkeys(teams))


def _resolve_source_teams(
    detail_rows: list[dict],
    games: dict[str, GameContext],
    *,
    source_team: str | None,
    source_teams: tuple[str, ...] | None,
    allowed_game_types: tuple[str, ...],
    player_type: str,
    play_metadata_by_id: dict[str, dict] | None = None,
) -> tuple[str, ...]:
    if source_team or source_teams is not None:
        return _normalize_source_teams(
            source_team=source_team,
            source_teams=source_teams,
        )

    inferred = _infer_source_teams(
        detail_rows,
        games,
        allowed_game_types=allowed_game_types,
        player_type=player_type,
        play_metadata_by_id=play_metadata_by_id,
    )
    if inferred:
        return inferred

    raise SourceTeamInferenceError(
        "Could not infer source team from Savant detail rows. "
        "Detail rows must include player-team fields or game feed metadata. "
        "Known fields include "
        f"{', '.join(dict.fromkeys((*DETAIL_ROW_TEAM_FIELDS, *PITCHER_DETAIL_ROW_TEAM_FIELDS)))}. "
        "Pass --source-team for one home-team slice or --source-teams to combine "
        "multiple home-team slices."
    )


def _infer_source_teams(
    detail_rows: list[dict],
    games: dict[str, GameContext],
    *,
    allowed_game_types: tuple[str, ...],
    player_type: str,
    play_metadata_by_id: dict[str, dict] | None = None,
) -> tuple[str, ...]:
    inferred: dict[str, tuple[str, int]] = {}
    play_metadata_by_id = play_metadata_by_id or {}
    for index, row in enumerate(detail_rows):
        team = _team_for_row(row, player_type, play_metadata_by_id)
        if team is None or team not in TEAM_HOME_PARK_ID:
            continue
        game = games.get(str(row.get("game_pk")))
        if game is None:
            continue
        if allowed_game_types and game.game_type.upper() not in allowed_game_types:
            continue
        if game.home_team != team:
            continue
        source_park_id = TEAM_HOME_PARK_ID[team]
        if game.savant_park_code != PARK_ID_TO_SAVANT_CODE[source_park_id]:
            continue
        inferred.setdefault(team, (_optional_str(row.get("game_date")) or "", index))
    return tuple(
        team
        for team, _ in sorted(
            inferred.items(),
            key=lambda item: (item[1][0], item[1][1], item[0]),
        )
    )


def _team_for_row(
    row: dict, player_type: str, play_metadata_by_id: dict[str, dict]
) -> str | None:
    team = _team_from_detail_row(row, player_type)
    if team is not None:
        return team
    return _team_from_play_metadata(row, player_type, play_metadata_by_id)


def _team_from_detail_row(row: dict, player_type: str) -> str | None:
    fields = (
        PITCHER_DETAIL_ROW_TEAM_FIELDS
        if normalize_player_type(player_type) == "Pitcher"
        else DETAIL_ROW_TEAM_FIELDS
    )
    for field in fields:
        value = row.get(field)
        if value not in (None, ""):
            return _normalize_team(str(value))
    return None


def _team_from_play_metadata(
    row: dict, player_type: str, play_metadata_by_id: dict[str, dict]
) -> str | None:
    play_id = row.get("play_id")
    if play_id in (None, ""):
        return None
    metadata = play_metadata_by_id.get(str(play_id)) or {}
    key = "pitching_team" if normalize_player_type(player_type) == "Pitcher" else "batting_team"
    team = metadata.get(key)
    if team in (None, ""):
        return None
    return _normalize_team(str(team))


def _player_id_from_row(row: dict, player_type: str) -> str | None:
    field = "pitcher_id" if normalize_player_type(player_type) == "Pitcher" else "batter_id"
    return _optional_str(row.get(field))


def _player_name_from_row(row: dict, player_type: str) -> str | None:
    field = "pitcher_name" if normalize_player_type(player_type) == "Pitcher" else "batter_name"
    return _optional_str(row.get(field))


def _home_run_marker(
    row: dict,
    *,
    game: GameContext,
    source_park_id: str,
    source_park_name: str,
    metadata: dict | None = None,
) -> ParkShiftHomeRunMarker:
    metadata = metadata or {}
    spray_angle = _optional_float(metadata.get("spray_angle_deg"))
    coord_x = _optional_float(metadata.get("coord_x"))
    coord_y = _optional_float(metadata.get("coord_y"))
    return ParkShiftHomeRunMarker(
        play_id=_optional_str(row.get("play_id")),
        game_pk=str(row.get("game_pk")),
        game_date=_optional_str(row.get("game_date")),
        result=_optional_str(row.get("result")),
        source_park_id=source_park_id,
        source_park_name=source_park_name or game.venue_name,
        distance_ft=_optional_int(row.get("hr_distance"))
        or _optional_int(metadata.get("distance_ft")),
        launch_angle=_optional_int(row.get("launch_angle"))
        or _optional_int(metadata.get("launch_angle")),
        exit_velocity=_optional_float(row.get("exit_velocity"))
        or _optional_float(metadata.get("exit_velocity")),
        spray_angle_deg=spray_angle,
        coord_x=coord_x,
        coord_y=coord_y,
        coordinate_source="mlb_statsapi" if spray_angle is not None else None,
    )


def _safe_play_metadata(detail_rows: list[dict], *, use_cache: bool) -> dict[str, dict]:
    game_pks = [
        str(row.get("game_pk"))
        for row in detail_rows
        if row.get("game_pk") and row.get("play_id")
    ]
    if not game_pks:
        return {}
    try:
        return get_play_metadata_by_id(game_pks, use_cache=use_cache)
    except Exception:
        return {}


def _optional_str(value: object) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _optional_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _optional_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    return float(value)
