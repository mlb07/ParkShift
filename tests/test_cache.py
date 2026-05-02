from parkshift.cache import load_or_fetch_json


def test_load_or_fetch_json_writes_and_reuses_cache(tmp_path) -> None:
    path = tmp_path / "cache.json"
    calls = 0

    def fetcher() -> dict:
        nonlocal calls
        calls += 1
        return {"ok": True}

    assert load_or_fetch_json(path, fetcher) == {"ok": True}
    assert load_or_fetch_json(path, fetcher) == {"ok": True}

    assert calls == 1


def test_load_or_fetch_json_can_bypass_cache(tmp_path) -> None:
    path = tmp_path / "cache.json"
    calls = 0

    def fetcher() -> dict:
        nonlocal calls
        calls += 1
        return {"calls": calls}

    assert load_or_fetch_json(path, fetcher, use_cache=False) == {"calls": 1}
    assert load_or_fetch_json(path, fetcher, use_cache=False) == {"calls": 2}
    assert not path.exists()
