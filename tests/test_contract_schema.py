import json
from pathlib import Path

from parkshift.identity import calculate_home_park_identity
from parkshift.schedule import GameContext


def test_identity_schema_matches_contract_keys() -> None:
    schema = json.loads(Path("docs/identity.schema.json").read_text())
    identity = calculate_home_park_identity(
        [
            {
                "game_pk": "1",
                "result": "home_run",
                "batter_id": "592450",
                "batter_name": "Judge, Aaron",
                "year": "2024",
                "nyy": "1",
            }
        ],
        {"1": GameContext("1", "R", "NYY", "BOS", 3313, "Yankee Stadium", "nyy")},
        source_team="NYY",
    )
    data = identity.to_dict()

    assert schema["properties"]["contract_version"]["const"] == data["contract_version"]
    assert set(schema["required"]).issubset(data)
    assert set(data).issubset(schema["properties"])
