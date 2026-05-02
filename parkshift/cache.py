from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Callable, TypeVar


T = TypeVar("T")


def default_cache_dir() -> Path:
    env_dir = os.environ.get("PARKSHIFT_CACHE_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.home() / ".cache" / "parkshift"


def load_or_fetch_json(
    path: str | Path,
    fetcher: Callable[[], T],
    *,
    use_cache: bool = True,
) -> T:
    cache_path = Path(path)
    if use_cache and cache_path.exists():
        return json.loads(cache_path.read_text())

    data = fetcher()
    if use_cache:
        write_json(cache_path, data)
    return data


def write_json(path: str | Path, data: object) -> None:
    cache_path = Path(path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=cache_path.parent,
        delete=False,
    ) as file:
        json.dump(data, file)
        temp_name = file.name
    Path(temp_name).replace(cache_path)

