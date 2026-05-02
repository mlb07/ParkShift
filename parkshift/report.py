from __future__ import annotations

import json
from html import escape
from pathlib import Path


def render_identity_report(data: dict) -> str:
    player = escape(str(data.get("player_name") or data.get("player_id") or "Unknown"))
    season = escape(str(data.get("season") or ""))
    source_team = escape(str(data.get("source_team") or ""))
    source_park = escape(str(data.get("source_park_name") or ""))
    help_hurt = float(data.get("help_hurt") or 0.0)
    help_hurt_label = escape(str(data.get("help_hurt_label") or ""))
    is_pitcher = str(data.get("player_type") or "").lower() == "pitcher"
    season_hr_total = data.get("season_hr_total")
    if season_hr_total is None:
        season_hr_total = data.get("actual_home_hr", 0)
    parks = data.get("parks") or []
    table_rows = "\n".join(_park_row(park) for park in parks)
    source_validation = "PASS" if data.get("source_park_matches_actual") else "FAIL"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ParkShift Report - {player}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 32px; color: #151515; }}
    header {{ border-bottom: 1px solid #ddd; padding-bottom: 16px; margin-bottom: 24px; }}
    h1 {{ font-size: 28px; margin: 0 0 8px; }}
    .meta {{ color: #555; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 24px; }}
    .metric {{ border: 1px solid #ddd; border-radius: 6px; padding: 12px; }}
    .metric span {{ display: block; color: #555; font-size: 13px; }}
    .metric strong {{ display: block; font-size: 22px; margin-top: 4px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #e5e5e5; padding: 8px; text-align: left; }}
    th {{ background: #f7f7f7; }}
    td.num {{ text-align: right; }}
  </style>
</head>
<body>
  <header>
    <h1>{player}</h1>
    <div class="meta">{season} · {source_team} · {source_park}</div>
  </header>
  <section class="metrics">
    <div class="metric"><span>{"Season HR Allowed" if is_pitcher else "Season HR"}</span><strong>{season_hr_total}</strong></div>
    <div class="metric"><span>{"Home HR Allowed" if is_pitcher else "Home HR"}</span><strong>{data.get("actual_home_hr", 0)}</strong></div>
    <div class="metric"><span>{"Home split average allowed" if is_pitcher else "Home split average"}</span><strong>{float(data.get("park_average_hr") or 0.0):.1f}</strong></div>
    <div class="metric"><span>{"Park added" if is_pitcher else "Park change"}</span><strong>{help_hurt:+.1f} ({help_hurt_label})</strong></div>
    <div class="metric"><span>Source validation</span><strong>{source_validation}</strong></div>
  </section>
  <table>
    <thead>
      <tr><th>Rank</th><th>Park</th><th>{"Total HR Allowed" if is_pitcher else "Total HR"}</th><th>{"Home HR Allowed" if is_pitcher else "Home HR"}</th><th>ParkShift Score</th></tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
</body>
</html>
"""


def render_identity_report_file(input_json: str | Path, output_html: str | Path) -> None:
    data = json.loads(Path(input_json).read_text())
    Path(output_html).write_text(render_identity_report(data))


def _park_row(park: dict) -> str:
    return (
        "<tr>"
        f"<td>{int(park.get('rank') or 0)}</td>"
        f"<td>{escape(str(park.get('park_name') or ''))}</td>"
        f"<td class=\"num\">{int(park.get('projected_total_hr') or park.get('translated_hr') or 0)}</td>"
        f"<td class=\"num\">{int(park.get('translated_hr') or 0)}</td>"
        f"<td class=\"num\">{float(park.get('parkshift_score') or 0.0):+.1f}</td>"
        "</tr>"
    )
