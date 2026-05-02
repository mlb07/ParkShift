# ParkShift

ParkShift is an early Home Run Translation Engine. It takes real Statcast batted
balls and asks whether each ball would clear the wall in another MLB park.

## Status

This is an early-stage experimental baseball analysis tool. Results are
estimates and should not be treated as official MLB, Baseball Savant, Statcast,
or betting-grade output.

ParkShift is not affiliated with Major League Baseball, Baseball Savant,
Statcast, or any MLB club. It uses public baseball data sources and local
translation logic.

For project context, architecture notes, validation history, and next steps,
see [docs/PROJECT_HANDOFF.md](docs/PROJECT_HANDOFF.md).

The MVP uses:

- `launch_speed`
- `launch_angle`
- `hc_x`, `hc_y`
- `hit_distance_sc` when available
- fallback distance estimated from exit velocity and launch angle
- park wall distance and height by spray angle

## Install

```bash
python -m pip install -e ".[dev,api,fetch]"
```

`api` is needed for the browser app. `fetch` is optional. Without `fetch`, use a
Baseball Savant CSV export.

## Run The Web App

```bash
parkshift app
```

Then open:

```text
http://127.0.0.1:8000
```

The browser app supports batters and pitchers, qualified high/low leaderboards,
batch queues, recent runs, and park-by-park translated home run views.

## Known Limitations

- Park wall profiles are starter approximations and should keep improving.
- Public Statcast/Savant hit coordinates and projected distances can be noisy.
- Savant Home Run Tracker detail availability varies by season, player type,
  and category.
- ParkShift currently supports seasons from 2016 through the current year.
- Pitcher mode translates home runs allowed, but it is still experimental.
- Weather, wind, roof state, game-time temperature, and defense/context effects
  are not fully modeled.

## Use A Baseball Savant CSV

```bash
parkshift translate --csv savant.csv --player "Aaron Judge"
```

## Fetch With pybaseball

```bash
parkshift translate --mlbam-id 592450 --start-date 2024-03-28 --end-date 2024-09-29
```

## Audit Distance Coverage

Baseball Savant exposes projected batted-ball distance as `hit_distance` in CSV
exports; `pybaseball` often returns the same value as `hit_distance_sc`.
ParkShift accepts either column name.

Check how complete projected distance is for HR and hard-hit balls:

```bash
python scripts/audit_distance_coverage.py --mlbam-id 592450 --start-date 2024-03-28 --end-date 2024-09-29 --source-home-team NYY
```

## Train An xHR Model

For better accuracy than hand-written thresholds, train an empirical model from
Baseball Savant CSV exports:

```bash
python -m pip install -e ".[ml]"
python scripts/train_xhr_model.py --csv statcast_2024.csv --output models/xhr_model.joblib
```

The training rows combine Statcast batted-ball inputs with the source park's
wall distance and height at that spray angle. The label is over-wall home run
versus non-over-wall batted ball.

To translate only a player's home-park batted balls, filter by the source home
team. For example, Aaron Judge's Yankee Stadium batted balls:

```bash
parkshift translate --mlbam-id 592450 --start-date 2024-03-28 --end-date 2024-09-29 --source-home-team NYY
```

When the source home team maps to one of the bundled parks, that source park's
row uses the player's actual home-run total from the source data. Other park
rows are translated estimates.

Actual source-park home runs also provide a carry lower bound for translations:
if a ball really cleared the source wall, ParkShift treats its carry as at least
the source wall distance at that spray angle, even when public Statcast
`hit_distance_sc` is shorter than the calibrated wall contour.

## Model Notes

This is intentionally simple:

1. Convert `hc_x`/`hc_y` to an approximate spray angle.
2. Interpolate a park's wall distance and wall height at that angle.
3. Use Statcast projected distance if available.
4. Estimate the batted ball's height at the fence from exit velocity and launch angle.
5. Count the ball as a translated home run only if it reaches the fence and clears the wall height.

The CLI defaults to no carry-distance tolerance and a 4 degree foul-line
tolerance. Statcast hit coordinates, projected distance, and the starter wall
profiles are approximate, so both values can be overridden while calibrating:

```bash
parkshift translate --csv savant.csv --distance-tolerance-ft 10 --foul-line-tolerance-deg 2
```

The bundled park profiles are starter approximations. The engine is structured so
better wall surveys, weather, altitude, wind, roof state, and probabilistic
trajectory models can be added later without changing the command-line workflow.

## Baseball Savant Home Run Tracker

Baseball Savant's Home Run Tracker already publishes official park translations.
ParkShift includes `parkshift.savant_hr` helpers to parse the embedded
leaderboard and the row-detail endpoint:

```python
from parkshift.savant_hr import fetch_details, fetch_leaderboard

leaderboard = fetch_leaderboard(year=2024, cat="xhr")
judge_details = fetch_details(player_id=592450, year=2024, cat="xhr")
```

Use Savant's tracker data as the benchmark for season-level validation. Keep
ParkShift's local model for custom slices Savant does not directly expose, such
as home-only batted balls or user-supplied CSV filters.

## Home-Park Identity

The `identity` command uses Savant's per-play park flags and MLB schedule
context to isolate a player's source-team home games. When Savant detail rows
include the player's team, ParkShift can infer the source team:

```bash
parkshift identity --player "Aaron Judge" --year 2024
```

You can also pass the source team explicitly:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --source-team NYY
```

Live Savant detail rows may not include player-team fields. In that case,
ParkShift falls back to the player's leaderboard team when available. For traded
players, pass `--source-teams` when you want a combined season slice.

Search player ids from the Savant leaderboard:

```bash
parkshift players --query judge --year 2024
```

For traded players, ParkShift can combine inferred source teams when the detail
rows expose the player's team. You can also combine multiple real home-team
slices explicitly:

```bash
parkshift identity --player-id 665862 --year 2024 --source-teams MIA NYY
```

`--player-id 592450` is also supported when you already know the MLBAM id.

By default this is regular season only (`--game-types R`), matching the
81-home-game concept. Pass additional MLB game types only when you intentionally
want postseason or special-event games included.

Fetched Savant and schedule responses are cached under `~/.cache/parkshift` by
default. Set `PARKSHIFT_CACHE_DIR` to override that location, or pass
`--no-cache` to force a fresh fetch.

For reproducible runs, pass downloaded inputs:

```bash
parkshift identity \
  --details-json judge_2024_xhr_details.json \
  --schedule-json mlb_schedule_2024.json \
  --year 2024 \
  --source-team NYY
```

The output includes the three MVP concepts:

- Home-Park Identity: translated home-game HR in all 30 parks.
- Help vs Hurt: source-park HR minus the 30-park average.
- Player ParkShift Score: each park's translated HR minus the 30-park average.

Reports show the player's full-season HR total for readability. ParkShift still
changes only the source-team home-game slice; away HR and other non-source-home
HR remain fixed. Each park row can therefore show a projected full-season total
while Park Change remains the home park change.

Machine-readable JSON output is also available:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --source-team NYY --format json
```

CSV output returns the 30-park table:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format csv > judge_parkshift.csv
```

HTML output renders a standalone report directly:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format html > judge_report.html
```

Named JSON views can return smaller product-specific payloads:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format json --view help-hurt
parkshift identity --player "Aaron Judge" --year 2024 --format json --view parkshift-score
```

The JSON field contract is documented in
[docs/JSON_CONTRACT.md](docs/JSON_CONTRACT.md).

For troubleshooting skipped rows, add `--debug` to the text output:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --debug
```

An optional local API app is available with the `api` extra:

```bash
python -m pip install -e ".[api]"
uvicorn "parkshift.api:create_app" --factory --reload
```

Then call `/identity`, `/identity/help-hurt`, or `/identity/parkshift-score`.

The same backend is available directly from Python:

```python
from parkshift.identity import get_home_park_identity

identity = get_home_park_identity(
    player="Aaron Judge",
    year=2024,
    source_team="NYY",
)

print(identity.source_park_hr)
print(identity.home_hr_candidate_batted_balls)
print(identity.parks[0])
print(identity.top_parks(5))
print(identity.to_dict())
print(identity.help_hurt_view())
print(identity.parkshift_score_view())
print(identity.to_dataframe())
```

Render a standalone HTML report from saved identity JSON:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format json > judge_identity.json
python scripts/render_identity_report.py --input-json judge_identity.json --output-html judge_report.html
```

Run a bundled no-network demo:

```bash
parkshift demo judge-2024
parkshift demo judge-2024 --format html > demo_report.html
```

## Frontend Prototype

A static browser prototype lives in `web/`. It opens without Node or a build
step and starts with the bundled Judge demo data:

```text
web/index.html
```

The API mode points at the optional FastAPI backend:

```bash
python -m pip install -e ".[api]"
uvicorn "parkshift.api:create_app" --factory --reload
```

Then use API mode in the browser with `http://127.0.0.1:8000` as the API base.
The local API allows browser requests from the static prototype.

The backend can also serve the prototype directly:

```bash
parkshift app
```

Open `http://127.0.0.1:8000`, search for a player, select a result, and run the
identity report from the same page. The normal app flow does not ask for player
ids, API URLs, or source teams.

The browser app also keeps recent runs in local storage and includes a batch
queue. Search/select players, confirm source teams, click `Queue`, then `Run
Queue` to run several reports and save the results for quick reloads.

Saved runs power the comparison table, saved-run leaderboard, target-park
readout, CSV exports, and plain-English run notes. The API also keeps an
in-memory identity response cache while the server process is running.

Use the Season Leaders panel to load the top Home Run Tracker players for a
season, queue individual leaders, or queue the displayed leaderboard for batch
runs. Source teams are resolved by the backend: per-row team data is used when
available, otherwise the Savant leaderboard team is used as the fallback.

Validate a batch of already-downloaded Savant detail files:

```bash
python scripts/download_savant_home_run_data.py \
  --output-dir savant_downloads_2024_xhr \
  --year 2024 \
  --top 50

python scripts/validate_home_park_identity.py \
  --leaderboard-html savant_downloads_2024_xhr/savant_hr_2024_xhr.html \
  --schedule-json mlb_schedule_2024.json \
  --details-dir savant_downloads_2024_xhr/savant_details_2024_xhr \
  --top 50
```

Or run the combined download + validation workflow:

```bash
python scripts/run_home_park_validation_workflow.py \
  --output-dir savant_validation_2024_xhr \
  --year 2024 \
  --top 50
```

For traded-player checks, pass the source team explicitly by player id:

```bash
python scripts/validate_home_park_identity.py \
  --leaderboard-html savant_hr_2024_xhr.html \
  --schedule-json mlb_schedule_2024.json \
  --details-dir savant_details_2024_xhr \
  --source-team 665862=NYY
```

For combined traded-player validation, use a comma-separated override:

```bash
python scripts/validate_home_park_identity.py \
  --leaderboard-html savant_hr_2024_xhr.html \
  --schedule-json mlb_schedule_2024.json \
  --details-dir savant_details_2024_xhr \
  --source-team 665862=MIA,NYY
```

## Park Wall Data

`parkshift/data/parks.json` contains one wall point per spray degree from `-45`
to `45`. Wall distances are generated from the open-source `GeomMLBStadiums`
MLBAM stadium path data:

```bash
python scripts/build_wall_profiles.py
```

The generated distance contours are then calibrated to published
LF/LCF/CF/RCF/RF distance markers where available. Wall heights are stored in the
same JSON file as editable park metadata because the MLBAM path geometry does
not include height.
