from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence
from typing import Mapping

from parkshift.identity import (
    DETAIL_ROW_TEAM_FIELDS,
    IdentityError,
    NoHomeRowsError,
    calculate_home_park_identity,
)
from parkshift.schedule import game_context_by_pk


@dataclass(frozen=True)
class IdentityValidationResult:
    player_id: str
    player_name: str
    source_team: str
    status: str
    home_hr_candidate_batted_balls: int
    actual_home_hr: int
    source_park_hr: int
    diff: int
    error: str | None = None


def validate_home_park_identities(
    leaderboard_rows: list[dict],
    details_by_player_id: Mapping[str, list[dict]],
    schedule: dict,
    *,
    source_teams: Mapping[str, str | Sequence[str]] | None = None,
    game_types: tuple[str, ...] = ("R",),
) -> list[IdentityValidationResult]:
    games = game_context_by_pk(schedule)
    team_overrides = source_teams or {}
    results: list[IdentityValidationResult] = []

    for row in leaderboard_rows:
        player_id = str(row["player_id"])
        player_name = str(row.get("player", player_id))
        source_team_display = _source_team_display(
            team_overrides.get(player_id, str(row.get("team_abbrev", "")))
        )
        detail_rows = details_by_player_id.get(player_id)
        if detail_rows is None:
            results.append(
                IdentityValidationResult(
                    player_id=player_id,
                    player_name=player_name,
                    source_team=source_team_display,
                    status="MISSING_DETAILS",
                    home_hr_candidate_batted_balls=0,
                    actual_home_hr=0,
                    source_park_hr=0,
                    diff=0,
                    error="No details JSON found for player.",
                )
            )
            continue

        source_team_arg, source_teams_arg = _source_team_args(
            team_overrides.get(player_id),
            leaderboard_team=str(row.get("team_abbrev", "")),
            detail_rows=detail_rows,
        )
        try:
            identity = calculate_home_park_identity(
                detail_rows,
                games,
                source_team=source_team_arg,
                source_teams=source_teams_arg,
                game_types=game_types,
            )
        except NoHomeRowsError as exc:
            results.append(
                IdentityValidationResult(
                    player_id=player_id,
                    player_name=player_name,
                    source_team=source_team_display,
                    status="NO_HOME_ROWS",
                    home_hr_candidate_batted_balls=0,
                    actual_home_hr=0,
                    source_park_hr=0,
                    diff=0,
                    error=str(exc),
                )
            )
            continue
        except IdentityError as exc:
            results.append(
                IdentityValidationResult(
                    player_id=player_id,
                    player_name=player_name,
                    source_team=source_team_display,
                    status="ERROR",
                    home_hr_candidate_batted_balls=0,
                    actual_home_hr=0,
                    source_park_hr=0,
                    diff=0,
                    error=str(exc),
                )
            )
            continue

        diff = identity.source_park_hr - identity.actual_home_hr
        results.append(
            IdentityValidationResult(
                player_id=player_id,
                player_name=identity.player_name or player_name,
                source_team=identity.source_team,
                status="PASS" if diff == 0 else "FAIL",
                home_hr_candidate_batted_balls=identity.home_hr_candidate_batted_balls,
                actual_home_hr=identity.actual_home_hr,
                source_park_hr=identity.source_park_hr,
                diff=diff,
            )
        )

    return results


def _source_team_args(
    override: str | Sequence[str] | None,
    *,
    leaderboard_team: str,
    detail_rows: list[dict],
) -> tuple[str | None, tuple[str, ...] | None]:
    if override is not None:
        teams = _source_teams_from_value(override)
        if len(teams) == 1:
            return teams[0], None
        return None, teams
    if _details_have_team_field(detail_rows):
        return None, None
    return leaderboard_team, None


def _source_team_display(value: str | Sequence[str] | None) -> str:
    if value is None:
        return ""
    teams = _source_teams_from_value(value)
    return ",".join(teams)


def _source_teams_from_value(value: str | Sequence[str]) -> tuple[str, ...]:
    if isinstance(value, str):
        raw_teams = value.replace(",", " ").split()
    else:
        raw_teams = [str(team) for team in value]
    return tuple(team.upper() for team in raw_teams if team)


def _details_have_team_field(detail_rows: list[dict]) -> bool:
    return any(
        any(row.get(field) not in (None, "") for field in DETAIL_ROW_TEAM_FIELDS)
        for row in detail_rows
    )


def validation_summary(results: list[IdentityValidationResult]) -> dict[str, object]:
    status_counts: dict[str, int] = {}
    for result in results:
        status_counts[result.status] = status_counts.get(result.status, 0) + 1
    checked = [result for result in results if result.status in {"PASS", "FAIL"}]
    total_actual = sum(result.actual_home_hr for result in checked)
    total_source = sum(result.source_park_hr for result in checked)
    return {
        "players": len(results),
        "checked": len(checked),
        "status_counts": status_counts,
        "actual_home_hr": total_actual,
        "source_park_hr": total_source,
        "total_diff": total_source - total_actual,
        "player_mae": (
            sum(abs(result.diff) for result in checked) / len(checked)
            if checked
            else 0.0
        ),
    }
