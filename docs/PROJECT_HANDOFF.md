# ParkShift Project Handoff

This document is the working handoff for future agents. It captures the product
plan, architecture, validation work, and current backend state.

## Product Direction

ParkShift started as a home run translation engine:

> Take a player's real batted balls and ask how many would be home runs in each
> MLB park.

The initial homemade model used public Statcast fields:

- `launch_speed`
- `launch_angle`
- `hc_x`, `hc_y`
- `hit_distance_sc` / `hit_distance`
- generated 30-park wall distance and height profiles

After investigation, Baseball Savant's Home Run Tracker was found to already
publish the core per-ball park translation data. That changed the MVP strategy.

ParkShift should not try to beat Savant's trajectory model with public EV/LA
physics. ParkShift's edge is the custom interpretation layer Savant does not
directly package:

1. **Home-Park Identity**
   - Take only a player's source-team regular-season home-game HR-candidate
     batted balls.
   - Translate those balls into all 30 MLB parks.
   - This answers: "If this player's home batted balls happened in another
     home park, how many HR would he have?"

2. **Help vs Hurt**
   - Source-park HR minus the 30-park average.
   - This answers: "Did his real home park inflate or suppress his home HR
     output?"

3. **Player ParkShift Score**
   - Each park's translated HR minus the same 30-park average.
   - This answers: "Which parks best fit this player's home batted-ball shape?"

The product should master these three backend concepts before adding extras
like weather, roof state, schedule simulation, trade/free-agent projections, or
frontend polish.

Current display rule:

- Show the player's actual full-season HR total in the app/report.
- Keep the park math on the source-team home-game slice only.
- For each destination park, projected full-season HR is:
  `non_source_home_hr + translated_hr`.
- Park Change and ParkShift Score remain home split deltas, not whole-season
  deltas.
- The frontend no longer exposes source-team controls in the normal workflow.
  It sends player id + season, and the backend resolves source teams. When
  detail rows include per-row team data, traded-player home parks can be
  combined automatically. Live Savant detail rows may still lack those team
  fields, in which case the backend falls back to the leaderboard team.

## Important Discovery

Baseball Savant Home Run Tracker:

```text
https://baseballsavant.mlb.com/leaderboard/home-runs
```

The page embeds leaderboard data in HTML:

```javascript
var data = [...]
```

The JavaScript also exposes a detail endpoint:

```text
https://baseballsavant.mlb.com/leaderboard/home-runs?type=details&player_id=592450&year=2024&player_type=Batter&cat=xhr
```

Detail rows include:

- `game_pk`
- `play_id`
- `game_date`
- `result`
- `exit_velocity`
- `launch_angle`
- `hr_distance`
- one `0`/`1` flag per MLB park: `nyy`, `hou`, `bos`, etc.
- `ct`: number of parks where the ball was gone
- `hr_cat`

Use `cat=xhr` as the default. That is Savant's Standard mode, based on observed
trajectory. `cat=adj_xhr` applies environmental adjustment and is not the MVP
default.

## Accuracy Baseline

Do not judge accuracy by comparing actual HR to Savant leaderboard `xhr`.
That is a neutral/expected metric and intentionally differs from actual output.

The correct validation is:

> For each real batted ball, map `game_pk` to the actual MLB venue and compare
> the Savant `0`/`1` flag for that venue against the real `result`.

Source-park reconstruction results:

```text
Top 50 2024 HR hitters, regular season home splits:
Players: 50
Checked: 50
Statuses: {'PASS': 50}
Actual home HR: 728
Source-park HR: 728
Total diff: +0
Player MAE: 0.00
```

Earlier broader source-park validation also showed Savant source-park flags are
essentially exact at reconstructing real outcomes. This is why Savant per-play
flags are the backend engine.

## Current Backend Contract

Primary Python API:

```python
from parkshift import get_home_park_identity

identity = get_home_park_identity(
    player="Aaron Judge",
    year=2024,
)
```

Equivalent id-based call:

```python
identity = get_home_park_identity(
    player_id=592450,
    year=2024,
)
```

Combined traded-player home-season call:

```python
identity = get_home_park_identity(
    player_id=665862,
    year=2024,
    source_teams=("MIA", "NYY"),
)
```

Important defaults:

- `cat="xhr"`
- `game_types=("R",)`
- `use_cache=True`

The regular-season default matches the original 81-home-game concept.
Postseason or special games are opt-in via `game_types`.

Useful fields and methods:

```python
identity.player_name
identity.player_id
identity.source_team
identity.source_teams
identity.source_park_name
identity.source_park_names
identity.home_hr_candidate_batted_balls
identity.actual_home_hr
identity.source_park_hr
identity.source_park_matches_actual
identity.park_average_hr
identity.help_hurt
identity.help_hurt_label
identity.parks
identity.source_park_result
identity.top_parks(5)
identity.bottom_parks(5)
identity.park("yankee")
identity.to_dict()
identity.help_hurt_view()
identity.parkshift_score_view()
identity.to_dataframe()
```

Terminology:

- `home_hr_candidate_batted_balls` means Savant Home Run Tracker detail rows
  from source-team home games. These are not every BBE; they are HR-relevant
  rows, generally actual HR plus non-HR balls that would have left at least one
  MLB park.
- Balls gone in zero parks do not change HR totals and are not needed for these
  counts.

## CLI Usage

User-facing Identity command:

```bash
parkshift identity --player "Aaron Judge" --year 2024
```

Player lookup:

```bash
parkshift players --query judge --year 2024
```

With MLBAM id:

```bash
parkshift identity --player-id 592450 --year 2024
```

Combined traded-player home-season slice:

```bash
parkshift identity --player-id 665862 --year 2024 --source-teams MIA NYY
```

With downloaded inputs:

```bash
parkshift identity \
  --details-json /tmp/judge_2024_xhr_details.json \
  --schedule-json /tmp/mlb_schedule_2024_alltypes.json \
  --year 2024 \
  --source-team NYY
```

Include postseason/special game types only when intentional:

```bash
parkshift identity \
  --player "Aaron Judge" \
  --year 2024 \
  --source-team NYY \
  --game-types R W L D F
```

Bypass cache:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --no-cache
```

Machine-readable JSON output:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format json
```

Named JSON views:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format json --view help-hurt
parkshift identity --player "Aaron Judge" --year 2024 --format json --view parkshift-score
```

CSV park table:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format csv > judge_parkshift.csv
```

Direct HTML report:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format html > judge_report.html
```

Debug skipped rows:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --debug
```

Optional local API:

```bash
python -m pip install -e ".[api]"
uvicorn "parkshift.api:create_app" --factory --reload
```

Report prototype:

```bash
parkshift identity --player "Aaron Judge" --year 2024 --format json > judge_identity.json
python scripts/render_identity_report.py --input-json judge_identity.json --output-html judge_report.html
```

Static frontend prototype:

```text
web/index.html
```

Run the local app:

```bash
parkshift app
```

The frontend renders the same `HomeParkIdentity.to_dict()` contract used by the
CLI, HTML report, and FastAPI app. It has a bundled no-network demo path and an
API mode pointed at `/identity`. The local FastAPI app enables CORS for this
static prototype and serves the app at `/`. Player search is exposed through
`/players`, using the Savant leaderboard cache/fetch path. The frontend keeps a
local-storage recent-run list and can queue multiple player/source-team specs
for sequential API execution. Saved runs power comparison, target-park ranking,
local leaderboards, plain-English notes, warning readouts, and CSV exports. The
API keeps an in-memory response cache for repeated identity calls during one app
server process. `/leaderboard` exposes top Savant leaderboard players for the
Season Leaders frontend panel, which can queue individual leaders or the
displayed top-N list into batch runs.

Bundled no-network demo:

```bash
parkshift demo judge-2024
parkshift demo judge-2024 --format html > demo_report.html
```

## Example Output

Aaron Judge 2024, regular season, Yankees home games:

```text
Player: Judge, Aaron
Season: 2024
Source team: NYY
Source home park: Yankee Stadium
Mode: xhr
Game types: R

Home HR-candidate batted balls: 39
Actual home HR: 31
Source-park HR: 31
Source validation: PASS
30-park average: 24.1
Park Change: +6.9 HR (Strong Help)

 rank                     park  translated_hr  parkshift_score
    1 Great American Ball Park             33              8.9
    2           Yankee Stadium             31              6.9
    3           Dodger Stadium             30              5.9
```

Randomized 25-player 2024 spot check had source validation `PASS` for all 25.
Examples:

```text
Juan Soto, NYY: actual home HR 20, source HR 20, avg 20.9, best Wrigley 26
Fernando Tatis Jr., SD: actual home HR 13, source HR 13, avg 11.5, best Great American 16
Paul Goldschmidt, STL: actual home HR 11, source HR 11, avg 13.6, best Great American 19
```

## Key Files

Core Home-Park Identity backend:

- `parkshift/identity.py`
  - `HomeParkIdentity`
  - `ParkShiftParkResult`
  - `get_home_park_identity`
  - `calculate_home_park_identity`
  - `IdentityError`
  - `NoHomeRowsError`

Savant Home Run Tracker helpers:

- `parkshift/savant_hr.py`
  - URL builders
  - fetchers
  - cached getters
  - `find_player_row`
  - player-name normalization
  - Savant code to local park id mapping

MLB schedule/venue mapping:

- `parkshift/schedule.py`
  - MLB Stats API schedule fetch/get
  - `GameContext`
  - venue id to Savant park code mapping
  - neutral/alternate sites return `savant_park_code=None`

Caching:

- `parkshift/cache.py`
  - default cache dir: `~/.cache/parkshift`
  - override env var: `PARKSHIFT_CACHE_DIR`

Validation:

- `parkshift/validation.py`
  - batch Home-Park Identity validation helpers
- `parkshift/download.py`
  - reusable Savant leaderboard/detail download workflow
- `scripts/download_savant_home_run_data.py`
  - fetches leaderboard HTML plus top-N per-player detail JSON files
- `scripts/validate_home_park_identity.py`
  - validates source-park reconstruction over downloaded detail files
- `scripts/validate_savant_source_flags.py`
  - lower-level source-flag validation script

Original/local physics model:

- `parkshift/translator.py`
- `parkshift/geometry.py`
- `parkshift/distance.py`
- `parkshift/parks.py`
- `parkshift/data/parks.json`
- `scripts/build_wall_profiles.py`

ML helpers:

- `parkshift/features.py`
- `parkshift/ml.py`
- `scripts/train_xhr_model.py`

Statcast CSV/pybaseball loading:

- `parkshift/statcast.py`
- `scripts/audit_distance_coverage.py`

CLI:

- `parkshift/cli.py`
  - `translate`
  - `identity`

Tests:

- `tests/test_identity.py`
- `tests/test_savant_hr.py`
- `tests/test_schedule.py`
- `tests/test_validation.py`
- `tests/test_cache.py`
- existing local-model tests

## Validation Commands

Run tests:

```bash
python -m pytest -q
```

Current expected result at the time of this handoff:

```text
43 passed
```

Batch validate downloaded details:

```bash
python scripts/download_savant_home_run_data.py \
  --output-dir /tmp/savant_downloads_2024_xhr \
  --year 2024 \
  --top 50

python scripts/validate_home_park_identity.py \
  --leaderboard-html /tmp/savant_downloads_2024_xhr/savant_hr_2024_xhr.html \
  --schedule-json /tmp/mlb_schedule_2024_alltypes.json \
  --details-dir /tmp/savant_downloads_2024_xhr/savant_details_2024_xhr \
  --top 50
```

Combined live/download validation workflow:

```bash
python scripts/run_home_park_validation_workflow.py \
  --output-dir /tmp/savant_validation_2024_xhr \
  --year 2024 \
  --top 50
```

Expected from existing 2024 top-50 downloaded set:

```text
Players: 50
Checked: 50
Statuses: {'PASS': 50}
Actual home HR: 728
Source-park HR: 728
Total diff: +0
Player MAE: 0.00
```

Traded-player example:

```bash
parkshift identity \
  --details-json /tmp/savant_details_2024_xhr/665862.json \
  --schedule-json /tmp/mlb_schedule_2024_alltypes.json \
  --year 2024 \
  --source-team MIA

parkshift identity \
  --details-json /tmp/savant_details_2024_xhr/665862.json \
  --schedule-json /tmp/mlb_schedule_2024_alltypes.json \
  --year 2024 \
  --source-team NYY
```

Combined traded-player validation override:

```bash
python scripts/validate_home_park_identity.py \
  --leaderboard-html savant_hr_2024_xhr.html \
  --schedule-json mlb_schedule_2024.json \
  --details-dir savant_details_2024_xhr \
  --source-team 665862=MIA,NYY
```

Jazz Chisholm 2024 examples from prior run:

```text
MIA home split: actual 7, source 7, PASS
NYY home split: actual 4, source 4, PASS
```

## Current Design Decisions

1. **Savant Standard xHR detail flags are authoritative for MVP.**
   - Do not rebuild the trajectory model unless later features require custom
     data Savant cannot provide.

2. **Regular season only by default.**
   - This matches the 81-home-game concept.
   - Savant detail endpoints include postseason unless filtered by schedule
     `game_type`.

3. **Source team can be inferred or explicit.**
   - ParkShift infers source teams when Savant detail rows expose the player's
     team.
   - Live Savant detail rows currently do not expose a player-team field, so
     `get_home_park_identity` falls back to the player's leaderboard team when
     possible.
   - Explicit `--source-team` and `--source-teams` remain available as
     overrides and for data that lacks a team field.
   - Example: Jazz Chisholm can be run for `MIA` and `NYY` separately.
   - `--source-teams MIA NYY` can also combine multiple real home-team slices
     into one season-level identity.

4. **Neutral/alternate sites are excluded from Home-Park Identity.**
   - Example venues: Gocheok Sky Dome, London Stadium, Rickwood Field,
     Mexico City.
   - These do not map to one of the 30 MLB park flags.

5. **No-home-row cases should error.**
   - `NoHomeRowsError` prevents misleading zero-HR outputs when the wrong
     source team is used.

6. **JSON/export exists for Identity.**
   - `HomeParkIdentity.to_dict()` is the full machine-readable contract.
   - `parkshift identity --format json` prints that contract.
   - `--view full|help-hurt|parkshift-score` exposes named JSON views.
   - `parkshift identity --format csv` exports the 30-park table.
   - `parkshift identity --format html` creates a standalone report directly.
   - `identity.to_dataframe()` supports notebook and data-analysis workflows.
   - `scripts/render_identity_report.py` creates a standalone HTML report from
     saved identity JSON.
   - `parkshift.api.create_app()` exposes optional FastAPI endpoints.
   - The full JSON schema is documented in `docs/identity.schema.json`.
   - The contract is documented in `docs/JSON_CONTRACT.md`.
   - Field names are pinned by tests and should change only as intentional
     app/API contract changes.

## Known Caveats

- The Savant Home Run Tracker details endpoint is not a documented stable API.
  It currently works and is used by Savant's own page JavaScript.
- Network requests may require a browser-like User-Agent. `fetch_text` already
  sends one.
- Public Statcast EV/LA/distance data is not enough to perfectly reproduce
  Savant's per-play trajectory calls.
- `Home HR-candidate batted balls` are not all batted balls.
- Source-team inference requires detail rows to expose the player's team on
  each row. Live Savant detail rows currently lack that field, so non-traded
  player calls use the leaderboard-team fallback; traded combined slices still
  need `--source-teams`.
- The local wall profiles are useful for experimentation but are no longer the
  MVP truth engine.
- Team naming:
  - Internally use `AZ` for Arizona in schedule/team mapping.
  - `ARI` is accepted in some normalization paths.
  - `OAK` is used for 2024 Athletics; `ATH` aliases exist in MLB mapping.

## Next Backend Steps

Do these before frontend work.

1. **Add a simple API/frontend boundary**
   - The JSON contract is stable enough to wrap in a small API route.
   - `--view full|help-hurt|parkshift-score` already mirrors likely API views.

2. **Improve schedule/detail diagnostics further**
   - Missing schedule games are counted, but not yet listed by `game_pk`.
   - If live data has surprising skips, add optional debug output.

3. **Add frontend or report prototype**
   - Use the JSON contract to render Home-Park Identity, Help vs Hurt, and
     ParkShift Score without changing backend logic.

## How To Think About The Project

The current product thesis:

> Savant provides the per-ball park truth. ParkShift turns that truth into
> player-specific home environment identity, park help/hurt, and park fit.

Do not spend time tuning the old physics model unless the user explicitly
chooses to pursue an independent model. The strongest MVP is accurate,
explainable, player-specific interpretation built on Savant detail flags.
