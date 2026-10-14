"""Local state that keeps the collector slow and stoppable.

Everything lives in ~/.salary-intel, outside the repository:
- fb-profile/  the persistent Chrome profile you log into by hand
- fb-runs.json every run and inspect, with its outcome and diagnostics
- fb-seen.json fingerprints of posts already examined, for incremental runs
- fb.lock      held while a run is active, so two runs never overlap
"""
import json
import os
from contextlib import contextmanager
from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from pathlib import Path

HOME = Path.home() / ".salary-intel"
PROFILE_DIR = HOME / "fb-profile"
RUNS_FILE = HOME / "fb-runs.json"
SEEN_FILE = HOME / "fb-seen.json"
LOCK_FILE = HOME / "fb.lock"

MAX_RUNS_PER_WEEK = 3
MIN_HOURS_BETWEEN_RUNS = 24
MAX_BLOCK_EVENTS = 2
COOLDOWN_DAYS = {"temporary": 7, "checkpoint": 30, "session_ended": 30}
MAX_SEEN_FINGERPRINTS = 5000


@dataclass(frozen=True)
class Limits:
    max_posts: int = 25
    hard_max_posts: int = 50
    max_examined: int = 150
    max_scrolls: int = 60
    max_expands: int = 30
    max_minutes: int = 10

    def halved(self) -> "Limits":
        return Limits(**{f.name: max(1, getattr(self, f.name) // 2) for f in fields(self)})


class LockedError(RuntimeError):
    pass


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    tmp.replace(path)


def load_runs(path: Path = RUNS_FILE) -> list[dict]:
    if not path.exists():
        return []
    runs = json.loads(path.read_text())
    if not isinstance(runs, list):
        raise ValueError(f"{path} is not a list of runs. Fix or move it by hand; it is the safety log.")
    return runs


def append_run(record: dict, path: Path = RUNS_FILE) -> None:
    _write_json(path, [*load_runs(path), record])


def _started(run: dict) -> datetime:
    return datetime.fromisoformat(run["started_at"])


def block_events(runs: list[dict]) -> list[dict]:
    return [run for run in runs if run.get("block_kind")]


def refusal(runs: list[dict], now: datetime, inspect: bool = False) -> str | None:
    """Why the collector must not start now, or None when it may."""
    blocks = block_events(runs)
    if len(blocks) >= MAX_BLOCK_EVENTS:
        return (
            f"{len(blocks)} block events are recorded. Automated collection has ended for this "
            "account. Use the admin or the anonymous-form route instead."
        )
    if blocks:
        last = blocks[-1]
        until = _started(last) + timedelta(days=COOLDOWN_DAYS[last["block_kind"]])
        if now < until:
            return f"Cooling down after a '{last['block_kind']}' event until {until:%Y-%m-%d %H:%M}."
    if inspect:
        return None

    real_runs = [run for run in runs if run.get("kind", "run") == "run"]
    if real_runs:
        next_allowed = max(map(_started, real_runs)) + timedelta(hours=MIN_HOURS_BETWEEN_RUNS)
        if now < next_allowed:
            return f"At least {MIN_HOURS_BETWEEN_RUNS} hours must pass between runs. Next run: {next_allowed:%Y-%m-%d %H:%M}."
    this_week = [run for run in real_runs if now - _started(run) < timedelta(days=7)]
    if len(this_week) >= MAX_RUNS_PER_WEEK:
        return f"Already ran {len(this_week)} times in the last 7 days (max {MAX_RUNS_PER_WEEK})."
    return None


def effective_limits(runs: list[dict]) -> Limits:
    return Limits().halved() if block_events(runs) else Limits()


def load_seen(path: Path = SEEN_FILE) -> list[str]:
    if not path.exists():
        return []
    return json.loads(path.read_text())


def save_seen(new_keys: list[str], path: Path = SEEN_FILE) -> None:
    known = load_seen(path)
    known_set = set(known)
    merged = known + [key for key in new_keys if key not in known_set]
    _write_json(path, merged[-MAX_SEEN_FINGERPRINTS:])


def _lock_is_stale(path: Path) -> bool:
    try:
        pid = int(path.read_text().strip())
    except (ValueError, FileNotFoundError):
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


@contextmanager
def run_lock(path: Path = LOCK_FILE):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        if not _lock_is_stale(path):
            raise LockedError(f"Another run is active ({path}).") from None
        path.unlink()
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, "w") as lock:
        lock.write(str(os.getpid()))
    try:
        yield
    finally:
        path.unlink(missing_ok=True)
