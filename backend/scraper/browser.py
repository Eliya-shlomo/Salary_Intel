"""The only module that knows Facebook's page structure.

When Facebook changes its markup, fix the selectors here and nowhere else.
"""
from dataclasses import dataclass, field

from playwright.sync_api import Page

from scraper.filters import is_truncated

MESSAGE_SELECTOR = ", ".join(
    [
        '[data-ad-rendering-role="story_message"]',
        '[data-ad-comet-preview="message"]',
        '[data-ad-preview="message"]',
    ]
)
SEE_MORE_PATTERN = "^(See more|עוד|ראה עוד|הצג עוד)$"
MAX_EXPANDS_PER_PASS = 5

FIND_POST_MESSAGES_JS = """
(selector) => {
  const COMMENT_LABEL = /^(Comment by|Reply by)/;
  const feed = document.querySelector('[role="feed"]');
  const outermost = (root) => [...root.querySelectorAll(selector)].filter((el) => {
    const outer = el.parentElement && el.parentElement.closest(selector);
    return !outer || !root.contains(outer);
  });
  const isComment = (el, unit) => {
    const article = el.closest('[role="article"]');
    if (!article) return false;
    if (COMMENT_LABEL.test(article.getAttribute('aria-label') || '')) return true;
    if (unit) return article !== unit && unit.contains(article);
    return Boolean(article.parentElement && article.parentElement.closest('[role="article"]'));
  };
  const found = {feedPresent: Boolean(feed), fallback: !feed, units: 0, comments: 0, messages: []};
  if (feed) {
    const units = [...feed.children];
    if (units.length && !units[0].querySelector(selector)) units.shift();
    found.units = units.length;
    for (const unit of units) {
      const candidates = outermost(unit);
      const posts = candidates.filter((el) => !isComment(el, unit));
      found.comments += candidates.length - posts.length;
      if (posts.length) found.messages.push(posts[0]);
    }
  } else {
    const candidates = outermost(document);
    const posts = candidates.filter((el) => !isComment(el, null));
    found.comments = candidates.length - posts.length;
    found.messages = posts;
  }
  return found;
}
"""

READ_FEED_JS = f"""
(selector) => {{
  const found = ({FIND_POST_MESSAGES_JS})(selector);
  return {{
    feedPresent: found.feedPresent,
    fallback: found.fallback,
    units: found.units,
    comments: found.comments,
    texts: found.messages.map((el) => el.innerText),
  }};
}}
"""

SEE_MORE_BUTTONS_JS = f"""
([selector, pattern]) => {{
  const found = ({FIND_POST_MESSAGES_JS})(selector);
  const label = new RegExp(pattern);
  return found.messages.flatMap((el) =>
    [...el.querySelectorAll('[role="button"]')].filter((button) => label.test(button.innerText.trim()))
  );
}}
"""

DESCRIBE_UNITS_JS = """
(selector) => {
  const feed = document.querySelector('[role="feed"]');
  if (!feed) return {sortText: '', units: []};
  const units = [...feed.children];
  const sortText = units.length && !units[0].querySelector(selector) ? units.shift().innerText : '';
  return {
    sortText,
    units: units.map((unit) => {
      const roles = new Set();
      const dataAd = new Set();
      for (const el of [unit, ...unit.querySelectorAll('*')]) {
        if (el.getAttribute('role')) roles.add(el.getAttribute('role'));
        for (const attr of el.getAttributeNames()) {
          if (attr.startsWith('data-ad')) dataAd.add(`${attr}=${el.getAttribute(attr)}`);
        }
      }
      return {
        chars: unit.innerText.trim().length,
        hasMessage: Boolean(unit.querySelector(selector)),
        roles: [...roles].sort(),
        dataAd: [...dataAd].sort(),
      };
    }),
  };
}
"""

PAGE_TEXT_JS = """
() => {
  const body = document.body ? document.body.innerText : '';
  const feed = document.querySelector('[role="feed"]');
  if (!feed) return [body, ''];
  const feedText = feed.innerText;
  return [body.includes(feedText) ? body.replace(feedText, '') : body, feedText];
}
"""


@dataclass
class FeedMessage:
    text: str
    truncated: bool


@dataclass
class FeedRead:
    feed_present: bool
    used_fallback: bool
    units_seen: int
    comments_skipped: int
    messages: list[FeedMessage] = field(default_factory=list)

    @property
    def truncated_count(self) -> int:
        return sum(message.truncated for message in self.messages)


def read_feed(page: Page) -> FeedRead:
    found = page.evaluate(READ_FEED_JS, MESSAGE_SELECTOR)
    messages = [FeedMessage(text.strip(), is_truncated(text)) for text in found["texts"] if text.strip()]
    return FeedRead(
        feed_present=found["feedPresent"],
        used_fallback=found["fallback"],
        units_seen=found["units"],
        comments_skipped=found["comments"],
        messages=messages,
    )


def expand_see_more(page: Page, budget: int) -> int:
    """Click "See more" inside post bodies only. Returns the number of clicks spent."""
    if budget <= 0:
        return 0
    handles = page.evaluate_handle(SEE_MORE_BUTTONS_JS, [MESSAGE_SELECTOR, SEE_MORE_PATTERN])
    buttons = [prop.as_element() for prop in handles.get_properties().values()]
    clicks = 0
    for button in buttons[: min(budget, MAX_EXPANDS_PER_PASS)]:
        if button is None:
            continue
        clicks += 1
        try:
            button.click(timeout=2000)
        except Exception:
            continue
    handles.dispose()
    return clicks


@dataclass
class UnitShape:
    chars: int
    has_message: bool
    roles: list[str]
    data_ad: list[str]


def describe_units(page: Page) -> tuple[str, list[UnitShape]]:
    """Structure of each feed unit without its text, for --inspect. Returns (sort widget text, units)."""
    found = page.evaluate(DESCRIBE_UNITS_JS, MESSAGE_SELECTOR)
    units = [UnitShape(u["chars"], u["hasMessage"], u["roles"], u["dataAd"]) for u in found["units"]]
    return found["sortText"], units


def read_page_text(page: Page) -> tuple[str, str]:
    """Return (text outside the feed, text inside the feed)."""
    outside, inside = page.evaluate(PAGE_TEXT_JS)
    return outside, inside
