import json
import os
from datetime import datetime, timedelta

import pytest

from scraper.run_log import (
    Limits,
    LockedError,
    append_run,
    effective_limits,
    load_runs,
    load_seen,
    refusal,
    run_lock,
    save_seen,
)

NOW = datetime(2026, 10, 14, 12, 0)


def run(hours_ago, block_kind=None, kind="run"):
    started = NOW - timedelta(hours=hours_ago)
    return {"started_at": started.isoformat(), "kind": kind, "outcome": "x", "block_kind": block_kind}


def test_first_run_is_allowed():
    assert refusal([], NOW) is None


def test_needs_24_hours_between_runs():
    assert "24 hours" in refusal([run(23)], NOW)
    assert refusal([run(25)], NOW) is None


def test_at_most_three_runs_in_seven_days():
    assert "3 times" in refusal([run(30), run(80), run(130)], NOW)
    assert refusal([run(30), run(80), run(24 * 8)], NOW) is None


def test_inspect_records_do_not_count_as_runs():
    assert refusal([run(1, kind="inspect")], NOW) is None


@pytest.mark.parametrize(
    "kind, blocked_days, cooled_days",
    [("temporary", 6, 8), ("checkpoint", 29, 31), ("session_ended", 29, 31)],
)
def test_cooldown_after_block(kind, blocked_days, cooled_days):
    assert "Cooling down" in refusal([run(blocked_days * 24, block_kind=kind)], NOW)
    assert refusal([run(cooled_days * 24, block_kind=kind)], NOW) is None


def test_second_block_ends_collection_for_good():
    runs = [run(24 * 400, block_kind="temporary"), run(24 * 300, block_kind="temporary")]
    assert "ended" in refusal(runs, NOW)
    assert "ended" in refusal(runs, NOW, inspect=True)


def test_inspect_skips_run_limits_but_not_cooldown():
    assert refusal([run(1)], NOW, inspect=True) is None
    assert "Cooling down" in refusal([run(24, block_kind="temporary")], NOW, inspect=True)


def test_limits_are_halved_after_a_block():
    assert effective_limits([]) == Limits()
    halved = effective_limits([run(24 * 10, block_kind="temporary")])
    assert halved == Limits(max_posts=12, hard_max_posts=25, max_examined=75, max_scrolls=30, max_expands=15, max_minutes=5)


def test_runs_file_keeps_history(tmp_path):
    path = tmp_path / "fb-runs.json"
    append_run(run(48), path)
    append_run(run(1), path)
    assert len(load_runs(path)) == 2


def test_runs_file_that_is_not_a_list_is_refused(tmp_path):
    path = tmp_path / "fb-runs.json"
    path.write_text(json.dumps({"2026-10-14": 1}))
    with pytest.raises(ValueError):
        load_runs(path)


def test_seen_file_merges_and_caps(tmp_path, monkeypatch):
    path = tmp_path / "fb-seen.json"
    monkeypatch.setattr("scraper.run_log.MAX_SEEN_FINGERPRINTS", 3)
    save_seen(["a", "b"], path)
    save_seen(["b", "c", "d"], path)
    assert load_seen(path) == ["b", "c", "d"]


def test_lock_blocks_a_second_run(tmp_path):
    path = tmp_path / "fb.lock"
    with run_lock(path):
        with pytest.raises(LockedError):
            with run_lock(path):
                pass
    assert not path.exists()


def test_stale_lock_from_a_dead_process_is_taken_over(tmp_path):
    path = tmp_path / "fb.lock"
    path.write_text("999999")
    with run_lock(path):
        assert path.read_text() == str(os.getpid())
