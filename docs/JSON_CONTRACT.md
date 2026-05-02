# ParkShift JSON Contract

This document defines the machine-readable Home-Park Identity contract.

The main contract is produced by:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format json
```

It is also available from Python:

```python
identity.to_dict()
```

Field names should be treated as stable app/API contract names. Rename or remove
them only as an intentional breaking change.

The current contract version is `1.0`. The full schema is in
[`docs/identity.schema.json`](identity.schema.json).

Use `--view` for smaller product-specific JSON payloads:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format json --view help-hurt
parkshift identity --player "Aaron Judge" --year 2024 --format json --view parkshift-score
```

## Full Identity Result

Top-level fields:

- `contract_version`: JSON contract version. Current value: `1.0`.
- `player_id`: MLBAM player id as a string, when known.
- `player_name`: Savant player name, when known.
- `season`: season year.
- `source_team`: source team display string, such as `NYY` or `MIA,NYY`.
- `source_teams`: teams whose home games define the slice, such as `["NYY"]`
  or `["MIA", "NYY"]` for a traded player.
- `source_park_id`: ParkShift internal park id for the source park. In
  multi-team mode this is `multiple`.
- `source_park_ids`: source park ids matching `source_teams`.
- `source_park_name`: display name for the source park. In multi-team mode this
  is `Multiple source parks`.
- `source_park_names`: source park display names matching `source_teams`.
- `cat`: Savant Home Run Tracker mode. The app default is `adj_xhr` for
  environment-adjusted translation; `xhr` remains supported for raw wall-only
  comparison.
- `game_types`: included MLB game types, usually `["R"]`.
- `home_hr_candidate_batted_balls`: source-team home rows from Savant's tracker.
- `season_hr_total`: actual full-season HR total for the included game types.
- `non_source_home_hr`: actual HR outside the home split. These HR stay
  fixed when projecting the player's total into another home park.
- `actual_home_hr`: real home runs in that home split.
- `source_park_hr`: translated home runs for the player's actual source home
  environment. In multi-team mode this sums each row against its real source
  home park.
- `source_park_matches_actual`: whether source-park translation matches reality.
- `park_average_hr`: average translated HR across all 30 MLB parks.
- `help_hurt`: source-park HR minus the 30-park average.
- `help_hurt_label`: bucketed label for `help_hurt`.
- `skipped_missing_game`: rows skipped because the schedule had no matching game.
- `skipped_game_type`: rows skipped because the game type was excluded.
- `skipped_neutral_or_alt_site`: rows skipped at neutral or alternate venues.
- `skipped_missing_game_pks`: skipped game ids for missing games.
- `skipped_game_type_pks`: skipped game ids for excluded game types.
- `skipped_neutral_or_alt_site_pks`: skipped game ids for neutral or alternate
  venues.
- `source_park_result`: park result object for the source park, or `null` in
  multi-team mode.
- `source_park_results`: park result objects for all source parks.
- `parks`: ranked list of all park result objects.

Park result fields:

- `rank`: rank in the player-specific park table.
- `park_id`: ParkShift internal park id.
- `park_name`: display name.
- `savant_code`: Savant park flag code.
- `translated_hr`: number of source-slice batted balls gone in that park.
- `projected_total_hr`: full-season HR total if only the home split were
  moved to this park. This equals `non_source_home_hr + translated_hr`.
- `parkshift_score`: `translated_hr` minus `park_average_hr`.
- `home_runs`: source-home batted balls that clear this park. Each marker
  includes `play_id`, `game_pk`, `game_date`, `distance_ft`, `launch_angle`,
  `exit_velocity`, and `spray_angle_deg` when the data is available.

## Product Views

`identity.help_hurt_view()` returns the Help vs Hurt concept only:

- `player_id`
- `player_name`
- `season`
- `source_team`
- `source_teams`
- `source_park_id`
- `source_park_ids`
- `source_park_name`
- `source_park_names`
- `home_hr_candidate_batted_balls`
- `season_hr_total`
- `non_source_home_hr`
- `actual_home_hr`
- `source_park_hr`
- `source_park_matches_actual`
- `park_average_hr`
- `help_hurt`
- `help_hurt_label`

`identity.parkshift_score_view()` returns the ParkShift Score concept:

- `player_id`
- `player_name`
- `season`
- `source_team`
- `source_teams`
- `source_park_id`
- `source_park_ids`
- `source_park_name`
- `source_park_names`
- `season_hr_total`
- `non_source_home_hr`
- `park_average_hr`
- `parks`

`parks` uses the same park result object as the full contract.

## DataFrame Export

`identity.to_dataframe()` returns one row per MLB park for notebook and data
analysis workflows. It includes the park result fields plus:

- `is_source_park`
- `projected_total_hr`
- `park_average_hr`
- `season_hr_total`
- `non_source_home_hr`
- `source_team`
- `source_teams`
- `player_id`
- `player_name`
- `season`
