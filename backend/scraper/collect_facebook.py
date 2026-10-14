"""Read salary posts from a Facebook group you are a member of.

You log in yourself in the browser window. The script only reads the post text that the
page displays: no author names, no profile links, no comments. It scrolls slowly, stops at
the first sign of a block, and never tries to get around one. Limits, cooldowns and the
run history live in scraper/run_log.py.

    PYTHONPATH=. .venv/bin/python -m scraper.collect_facebook --group-url <url> --inspect
    PYTHONPATH=. .venv/bin/python -m scraper.collect_facebook --group-url <url>
"""
import argparse
import json
import random
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from scraper import run_log
from scraper.browser import describe_units, expand_see_more, read_feed, read_page_text
from scraper.filters import block_reason, fingerprint, looks_like_salary_post, redact
from scraper.run_log import Limits, LockedError

OUTPUT_DIR = Path(__file__).parent / "output"
SOURCE_LABEL = "facebook_group"
MIN_DELAY_SECONDS = 4
MAX_DELAY_SECONDS = 9
EMPTY_ROUNDS_BEFORE_STOP = 3
KNOWN_IN_A_ROW_TO_STOP = 5
SORT_LABELS = ("פוסטים חדשים", "New posts")
PREVIEW_CHARS = 160
PLACEHOLDER_MAX_CHARS = 20
MAX_UNITS_DESCRIBED = 5

ENTER_PROMPT = """
In the browser window:
  1. Log in yourself if Facebook asks you to.
  2. Make sure the group feed is sorted by "New posts" / "פוסטים חדשים".
  3. If you have not checked today, look at Settings > Account Status for restrictions.
Keep the Chrome window open. Press Enter here to start, or Ctrl+C to cancel... """
WINDOW_CLOSED_MESSAGE = (
    "The Chrome window was closed before Enter. Nothing was read and no run was recorded. "
    "Run the command again and keep the window open."
)


@dataclass
class Diagnostics:
    units_seen: int = 0
    messages_read: int = 0
    comments_skipped: int = 0
    truncated: int = 0
    known: int = 0
    fallback_used: bool = False
    feed_warnings: list[str] = field(default_factory=list)


@dataclass
class CollectResult:
    posts: list[dict] = field(default_factory=list)
    outcome: str = ""
    block_kind: str | None = None
    examined: int = 0
    scrolls: int = 0
    expands: int = 0
    new_keys: list[str] = field(default_factory=list)
    diagnostics: Diagnostics = field(default_factory=Diagnostics)


def chronological_url(url: str) -> str:
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query) if k != "sorting_setting"]
    query.append(("sorting_setting", "CHRONOLOGICAL"))
    return urlunsplit(parts._replace(query=urlencode(query)))


def human_pause() -> None:
    time.sleep(random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS))


def make_post(text: str) -> dict:
    return {"text": redact(text.strip()), "source": SOURCE_LABEL, "collected_at": date.today().isoformat()}


def collect(
    page,
    limits: Limits,
    max_posts: int,
    seen_before: set[str],
    deadline: float,
    pause: Callable[[], None] = human_pause,
    clock: Callable[[], float] = time.monotonic,
) -> CollectResult:
    result = CollectResult()
    diag = result.diagnostics
    seen_this_run: set[str] = set()
    truncated_keys: set[str] = set()
    consecutive_known = 0
    empty_rounds = 0
    feed_was_present = False

    def stop(outcome: str, block_kind: str | None = None) -> CollectResult:
        result.outcome = outcome
        result.block_kind = block_kind
        diag.messages_read = len(seen_this_run)
        diag.truncated = len(truncated_keys)
        return result

    try:
        while True:
            outside_feed, inside_feed = read_page_text(page)
            signal = block_reason(page.url, outside_feed)
            if signal:
                return stop(f"stopped: possible block ({signal.kind}: {signal.reason})", signal.kind)
            feed_signal = block_reason("", inside_feed)
            if feed_signal and feed_signal.reason not in diag.feed_warnings:
                diag.feed_warnings.append(feed_signal.reason)
            if clock() > deadline:
                return stop("stopped: time limit reached")

            result.expands += expand_see_more(page, limits.max_expands - result.expands)
            feed = read_feed(page)
            diag.units_seen = max(diag.units_seen, feed.units_seen)
            diag.comments_skipped = max(diag.comments_skipped, feed.comments_skipped)
            diag.fallback_used = diag.fallback_used or feed.used_fallback
            if feed.feed_present:
                feed_was_present = True
            elif feed_was_present:
                return stop("stopped: feed disappeared, check Facebook in the browser yourself")
            if feed.units_seen and not feed.messages:
                return stop("stopped: selectors broken")

            new_this_round = 0
            for message in feed.messages:
                key = fingerprint(message.text)
                if message.truncated:
                    truncated_keys.add(key)
                    continue
                if key in seen_this_run:
                    continue
                seen_this_run.add(key)
                if key in seen_before:
                    diag.known += 1
                    consecutive_known += 1
                    if consecutive_known >= KNOWN_IN_A_ROW_TO_STOP:
                        return stop("stopped: reached already-collected posts")
                    continue
                consecutive_known = 0
                new_this_round += 1
                result.examined += 1
                result.new_keys.append(key)
                if looks_like_salary_post(message.text):
                    result.posts.append(make_post(message.text))
                    if len(result.posts) >= max_posts:
                        return stop("done: reached the post limit")
                if result.examined >= limits.max_examined:
                    return stop("stopped: examined-posts limit reached")

            empty_rounds = 0 if new_this_round else empty_rounds + 1
            if empty_rounds >= EMPTY_ROUNDS_BEFORE_STOP:
                return stop("stopped: no new posts after several scrolls")
            if result.scrolls >= limits.max_scrolls:
                return stop("stopped: scroll limit reached")

            pause()
            page.mouse.wheel(0, random.randint(500, 900))
            result.scrolls += 1
            pause()
    except KeyboardInterrupt:
        return stop("stopped: interrupted by user")


def print_unit_breakdown(units) -> None:
    placeholders = [u for u in units if not u.has_message and u.chars < PLACEHOLDER_MAX_CHARS]
    no_body = [(i, u) for i, u in enumerate(units, 1) if not u.has_message and u.chars >= PLACEHOLDER_MAX_CHARS]
    print(f"units with a post body:            {sum(u.has_message for u in units)}")
    print(f"units with almost no text:         {len(placeholders)}  (probably not loaded yet)")
    print(f"units with text but no post body:  {len(no_body)}")
    for index, unit in no_body[:MAX_UNITS_DESCRIBED]:
        print(f"  unit {index}: {unit.chars} chars, roles={unit.roles}, data-ad={unit.data_ad}")


def inspect(page) -> tuple[int, dict]:
    """Read only what is on screen: no scrolling, no clicks, no file."""
    outside_feed, inside_feed = read_page_text(page)
    signal = block_reason(page.url, outside_feed)
    if signal:
        print(f"Possible block: {signal.kind} ({signal.reason}). Stop and check Facebook yourself.")
        return 1, {"outcome": f"inspect: possible block ({signal.reason})", "block_kind": signal.kind}

    feed = read_feed(page)
    sort_text, units = describe_units(page)
    sort_label = next((label for label in SORT_LABELS if label in sort_text or label in outside_feed), None)
    feed_signal = block_reason("", inside_feed)
    print(f"feed present:      {feed.feed_present}")
    print(f"fallback used:     {feed.used_fallback}")
    print(f"units seen:        {feed.units_seen}")
    print(f"messages read:     {len(feed.messages)}")
    print(f"comments skipped:  {feed.comments_skipped}")
    print(f"truncated:         {feed.truncated_count}")
    print(f"sort label found:  {sort_label or 'no (check the sort by eye)'}")
    if feed_signal:
        print(f"warning text inside the feed (not treated as a block): {feed_signal.reason}")
    print_unit_breakdown(units)
    for index, message in enumerate([m for m in feed.messages if not m.truncated][:2], 1):
        preview = " ".join(redact(message.text).split())[:PREVIEW_CHARS]
        print(f"preview {index}: {preview}")

    record = {"outcome": "inspect: ok", "block_kind": None, "units": feed.units_seen, "messages": len(feed.messages)}
    if feed.units_seen and not feed.messages:
        print("selectors broken")
        record["outcome"] = "inspect: selectors broken"
        return 1, record
    if not feed.units_seen and not feed.messages:
        print("No feed and no post bodies found. Is the group feed open?")
        record["outcome"] = "inspect: nothing found"
        return 1, record
    return 0, record


def write_output(posts: list[dict]) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    out_file = OUTPUT_DIR / f"posts_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
    out_file.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in posts))
    return out_file


def run_in_browser(args, limits: Limits) -> int:
    with sync_playwright() as playwright:
        try:
            context = playwright.chromium.launch_persistent_context(
                str(run_log.PROFILE_DIR), channel="chrome", headless=False
            )
        except PlaywrightError as error:
            print(f"Could not open Chrome with the profile ({error}). Close any window that uses it and retry.")
            return 1
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(chronological_url(args.group_url))
            page.bring_to_front()
            print("A Chrome window opened. It may be hidden behind your editor.")
            try:
                input(ENTER_PROMPT)
            except KeyboardInterrupt:
                print("\nCancelled. Nothing was read and no run was recorded.")
                return 0
            if page.is_closed():
                print(WINDOW_CLOSED_MESSAGE)
                return 1

            started_at = datetime.now().isoformat(timespec="seconds")
            if args.inspect:
                code, record = inspect(page)
                run_log.append_run({"started_at": started_at, "kind": "inspect", **record})
                return code

            deadline = time.monotonic() + limits.max_minutes * 60
            seen_before = set(run_log.load_seen())
            try:
                result = collect(page, limits, args.max_posts, seen_before, deadline)
            except PlaywrightError as error:
                closed = page.is_closed()
                result = CollectResult(outcome="stopped: browser window was closed" if closed else f"crashed: {error}")
        finally:
            try:
                context.close()
            except PlaywrightError:
                pass

    run_log.append_run(
        {
            "started_at": started_at,
            "kind": "run",
            "outcome": result.outcome,
            "posts": len(result.posts),
            "examined": result.examined,
            "block_kind": result.block_kind,
            "scrolls": result.scrolls,
            "expands": result.expands,
            "diagnostics": asdict(result.diagnostics),
        }
    )
    run_log.save_seen(result.new_keys)

    print(result.outcome)
    print(json.dumps(asdict(result.diagnostics), ensure_ascii=False))
    if result.block_kind:
        days = run_log.COOLDOWN_DAYS[result.block_kind]
        print(f"No runs for {days} days. Use Facebook normally in the meantime and resolve any prompt by hand.")
    if not result.posts:
        print("No salary posts were saved.")
        return 1
    out_file = write_output(result.posts)
    print(f"Saved {len(result.posts)} posts to {out_file}")
    print(f"Next: PYTHONPATH=. .venv/bin/python -m scraper.scrub_posts {out_file}")
    return 0 if not result.outcome.startswith(("crashed", "stopped: selectors", "stopped: browser")) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--group-url", required=True)
    parser.add_argument("--max-posts", type=int, default=None)
    parser.add_argument("--inspect", action="store_true", help="read only what is on screen, save nothing")
    args = parser.parse_args(argv)

    runs = run_log.load_runs()
    reason = run_log.refusal(runs, datetime.now(), inspect=args.inspect)
    if reason:
        print(reason)
        return 2
    limits = run_log.effective_limits(runs)
    if args.max_posts is None:
        args.max_posts = limits.max_posts
    if not 1 <= args.max_posts <= limits.hard_max_posts:
        print(f"--max-posts must be between 1 and {limits.hard_max_posts}")
        return 2

    try:
        with run_log.run_lock():
            return run_in_browser(args, limits)
    except LockedError as error:
        print(error)
        return 2


if __name__ == "__main__":
    sys.exit(main())
