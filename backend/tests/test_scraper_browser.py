from scraper.browser import expand_see_more, read_feed, read_page_text

FEED_HTML = """
<html><body>
<div role="dialog">Group header</div>
<div role="feed">
  <div><div role="button">New posts</div></div>

  <div id="u1">
    <h3>Author Name</h3>
    <div data-ad-rendering-role="story_message">
      <div data-ad-preview="message">Post one: backend developer, 28 thousand gross</div>
    </div>
  </div>

  <div id="u2">
    <div data-ad-rendering-role="story_message">
      <span>Post two: DevOps engineer 35 thousand</span>…
      <div role="button" onclick="this.parentElement.innerHTML = 'Post two: DevOps engineer 35 thousand gross, 5 years, hybrid.'">עוד</div>
    </div>
  </div>

  <div id="u3">
    <div data-ad-rendering-role="story_message">Post three has comments below it</div>
    <div role="article" aria-label="Comment by Someone 5 minutes ago">
      <div data-ad-rendering-role="story_message">Comment text…<div role="button">See more</div></div>
      <div role="article" aria-label="Reply by Other">
        <div data-ad-preview="message">Reply text</div>
      </div>
    </div>
  </div>

  <div id="u4">
    <div role="article"><div data-ad-comet-preview="message">Comment without a label</div></div>
  </div>

  <div id="u5">
    <div data-ad-rendering-role="story_message">Post five stays cut…<div role="button">See more</div></div>
  </div>
</div>
</body></html>
"""

NO_FEED_HTML = """
<html><body>
<div role="article">
  <div data-ad-preview="message">Post without a feed</div>
  <div role="article"><div data-ad-preview="message">Nested comment</div></div>
</div>
</body></html>
"""


def test_reads_one_post_per_unit_and_skips_comments(chrome_page):
    chrome_page.set_content(FEED_HTML)

    feed = read_feed(chrome_page)

    assert feed.feed_present
    assert not feed.used_fallback
    assert feed.units_seen == 5
    assert feed.comments_skipped == 3
    texts = [m.text for m in feed.messages]
    assert texts[0] == "Post one: backend developer, 28 thousand gross"
    assert texts[2] == "Post three has comments below it"
    assert len(texts) == 4
    assert not any("Comment" in t or "Reply" in t or "Author" in t for t in texts)


def test_marks_truncated_posts(chrome_page):
    chrome_page.set_content(FEED_HTML)

    feed = read_feed(chrome_page)

    assert [m.truncated for m in feed.messages] == [False, True, False, True]
    assert feed.truncated_count == 2


def test_see_more_clicks_only_inside_posts(chrome_page):
    chrome_page.set_content(FEED_HTML)

    clicks = expand_see_more(chrome_page, budget=30)
    feed = read_feed(chrome_page)

    assert clicks == 2
    assert feed.messages[1].text == "Post two: DevOps engineer 35 thousand gross, 5 years, hybrid."
    assert not feed.messages[1].truncated
    assert feed.messages[3].truncated


def test_see_more_respects_budget(chrome_page):
    chrome_page.set_content(FEED_HTML)

    assert expand_see_more(chrome_page, budget=1) == 1
    assert expand_see_more(chrome_page, budget=0) == 0


def test_falls_back_to_message_bodies_without_a_feed(chrome_page):
    chrome_page.set_content(NO_FEED_HTML)

    feed = read_feed(chrome_page)

    assert not feed.feed_present
    assert feed.used_fallback
    assert [m.text for m in feed.messages] == ["Post without a feed"]
    assert feed.comments_skipped == 1


def test_page_text_is_split_around_the_feed(chrome_page):
    chrome_page.set_content(FEED_HTML)

    outside, inside = read_page_text(chrome_page)

    assert "Group header" in outside
    assert "Post one" not in outside
    assert "Post one" in inside
