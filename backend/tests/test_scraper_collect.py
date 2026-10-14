import time

from scraper.collect_facebook import chronological_url, collect, inspect
from scraper.filters import fingerprint
from scraper.run_log import Limits

SALARY = "מפתח backend עם {n} שנות ניסיון, {n}0 אלף ברוטו בחברה בתל אביב. טלפון 050-1234567"
CHAT = "מישהו מכיר חברה טובה שמגייסת עכשיו בצפון? שאלה מספר {n} בשבילי"


def feed_html(texts, before_feed=""):
    units = "".join(
        f'<div><div data-ad-rendering-role="story_message">{t}</div></div>' for t in texts
    )
    return f'<html><body>{before_feed}<div role="feed"><div>sort</div>{units}</div></body></html>'


def run_collect(page, texts, limits=Limits(), max_posts=25, seen=(), deadline=None, before_feed=""):
    page.set_content(feed_html(texts, before_feed))
    return collect(
        page,
        limits,
        max_posts,
        set(seen),
        deadline if deadline is not None else time.monotonic() + 60,
        pause=lambda: None,
    )


def test_chronological_url():
    assert chronological_url("https://www.facebook.com/groups/123") == (
        "https://www.facebook.com/groups/123?sorting_setting=CHRONOLOGICAL"
    )
    assert chronological_url("https://www.facebook.com/groups/123/?ref=share&sorting_setting=TOP") == (
        "https://www.facebook.com/groups/123/?ref=share&sorting_setting=CHRONOLOGICAL"
    )


def test_stops_at_post_limit_and_redacts(chrome_page):
    texts = [SALARY.format(n=n) for n in range(1, 5)]

    result = run_collect(chrome_page, texts, max_posts=2)

    assert result.outcome == "done: reached the post limit"
    assert len(result.posts) == 2
    assert "[phone]" in result.posts[0]["text"]
    assert result.posts[0]["source"] == "facebook_group"
    assert len(result.posts[0]["collected_at"]) == 10


def test_non_salary_posts_count_as_examined_but_are_not_saved(chrome_page):
    texts = [CHAT.format(n=1), SALARY.format(n=2), CHAT.format(n=3)]

    result = run_collect(chrome_page, texts)

    assert result.examined == 3
    assert len(result.posts) == 1
    assert len(result.new_keys) == 3


def test_stops_after_five_known_posts_in_a_row(chrome_page):
    texts = [SALARY.format(n=n) for n in range(1, 8)]
    known = [fingerprint(t) for t in texts[1:]]

    result = run_collect(chrome_page, texts, seen=known)

    assert result.outcome == "stopped: reached already-collected posts"
    assert result.examined == 1
    assert result.diagnostics.known == 5


def test_stops_on_block_outside_the_feed(chrome_page):
    result = run_collect(
        chrome_page,
        [SALARY.format(n=1)],
        before_feed='<div role="dialog">You’re Temporarily Blocked</div>',
    )

    assert result.block_kind == "temporary"
    assert result.outcome.startswith("stopped: possible block")
    assert result.posts == []


def test_warning_text_inside_the_feed_does_not_stop(chrome_page):
    texts = [SALARY.format(n=1), "This content isn't available right now"]

    result = run_collect(chrome_page, texts)

    assert result.block_kind is None
    assert result.diagnostics.feed_warnings == ["page says 'this content isn't available'"]


def test_selectors_broken_when_units_have_no_messages(chrome_page):
    chrome_page.set_content('<html><body><div role="feed"><div>sort</div><div>a</div><div>b</div></div></body></html>')

    result = collect(chrome_page, Limits(), 25, set(), time.monotonic() + 60, pause=lambda: None)

    assert result.outcome == "stopped: selectors broken"


def test_stops_after_three_rounds_without_new_posts(chrome_page):
    result = run_collect(chrome_page, [SALARY.format(n=1), CHAT.format(n=2)])

    assert result.outcome == "stopped: no new posts after several scrolls"
    assert result.scrolls == 3


def test_stops_at_examined_limit(chrome_page):
    texts = [CHAT.format(n=n) for n in range(5)]

    result = run_collect(chrome_page, texts, limits=Limits(max_examined=3))

    assert result.outcome == "stopped: examined-posts limit reached"
    assert result.examined == 3


def test_stops_at_scroll_limit(chrome_page):
    result = run_collect(chrome_page, [SALARY.format(n=1)], limits=Limits(max_scrolls=1))

    assert result.outcome == "stopped: scroll limit reached"
    assert result.scrolls == 1


def test_stops_at_time_limit(chrome_page):
    result = run_collect(chrome_page, [SALARY.format(n=1)], deadline=time.monotonic() - 1)

    assert result.outcome == "stopped: time limit reached"


def test_truncated_posts_are_not_saved_or_remembered(chrome_page):
    result = run_collect(chrome_page, [SALARY.format(n=1) + "… עוד"])

    assert result.posts == []
    assert result.new_keys == []
    assert result.diagnostics.truncated == 1


def test_inspect_reports_and_saves_nothing(chrome_page, capsys):
    chrome_page.set_content(feed_html([SALARY.format(n=1), CHAT.format(n=2)], before_feed="<span>פוסטים חדשים</span>"))

    code, record = inspect(chrome_page)

    out = capsys.readouterr().out
    assert code == 0
    assert "messages read:     2" in out
    assert "sort label found:  פוסטים חדשים" in out
    assert "[phone]" in out and "050-1234567" not in out
    assert record["block_kind"] is None


def test_inspect_says_selectors_broken(chrome_page, capsys):
    chrome_page.set_content('<html><body><div role="feed"><div>sort</div><div>a</div></div></body></html>')

    code, record = inspect(chrome_page)

    assert code == 1
    assert "selectors broken" in capsys.readouterr().out


def test_inspect_breaks_down_units_without_a_post_body(chrome_page, capsys):
    units = (
        '<div><div role="button">פוסטים חדשים</div></div>'
        f'<div><div data-ad-rendering-role="story_message">{SALARY.format(n=1)}</div></div>'
        "<div></div>"
        '<div><div role="article" data-ad-rendering-role="image">A photo post with a long caption text</div></div>'
    )
    chrome_page.set_content(f'<html><body><div role="feed">{units}</div></body></html>')

    inspect(chrome_page)

    out = capsys.readouterr().out
    assert "sort label found:  פוסטים חדשים" in out
    assert "units with a post body:            1" in out
    assert "units with almost no text:         1" in out
    assert "units with text but no post body:  1" in out
    assert "chars, roles=['article']" in out
    assert "data-ad-rendering-role=image" in out
