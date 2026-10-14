import pytest

from scraper.filters import (
    block_reason,
    fingerprint,
    is_truncated,
    looks_like_salary_post,
    redact,
)

SALARY_POST = "מפתח backend עם 3 שנות ניסיון, 28 אלף ברוטו בחברה בתל אביב"


@pytest.mark.parametrize(
    "phone",
    [
        "050-1234567",
        "0501234567",
        "050 123 4567",
        "050-123-4567",
        "+972-50-123-4567",
        "+972501234567",
        "972 50 1234567",
        "03-1234567",
        "077-1234567",
    ],
)
def test_redact_israeli_phones(phone):
    assert redact(f"תתקשרו אליי {phone} בערב") == "תתקשרו אליי [phone] בערב"


def test_redact_email_and_links():
    text = "פרטים ב-dana.cohen+jobs@gmail.com או https://example.com/job?id=1 או www.example.co.il"
    assert redact(text) == "פרטים ב-[email] או [link] או [link]"


def test_redact_keeps_salary_numbers():
    text = "שכר 25000-30000 ברוטו, 120k בשנה"
    assert redact(text) == text


def test_salary_post_is_detected():
    assert looks_like_salary_post(SALARY_POST)


@pytest.mark.parametrize(
    "text",
    [
        "28 אלף ברוטו",
        "מישהו יודע איזה חברה מגייסת עכשיו מפתחים בצפון הארץ?",
        "יש לי 3 שנות ניסיון ואני מחפש עבודה חדשה בתחום הדאטה",
    ],
)
def test_non_salary_posts_are_rejected(text):
    assert not looks_like_salary_post(text)


def test_fingerprint_ignores_whitespace():
    assert fingerprint("שכר  28 אלף\nברוטו") == fingerprint("שכר 28 אלף ברוטו")


def test_fingerprint_ignores_hidden_and_bidi_characters():
    hidden = "\u200fשכר\u200b 28\u2066 אלף\u2069 ברוטו\ufeff\u202b"
    assert fingerprint(hidden) == fingerprint("שכר 28 אלף ברוטו")


def test_fingerprint_normalizes_unicode_forms():
    composed = "café 28k"
    decomposed = "cafe\u0301 28k"
    assert fingerprint(composed) == fingerprint(decomposed)


@pytest.mark.parametrize("suffix", ["…", " … עוד", "… See more", "…See more", " עוד"])
def test_fingerprint_ignores_trailing_truncation_marker(suffix):
    assert fingerprint("שכר 28 אלף ברוטו" + suffix) == fingerprint("שכר 28 אלף ברוטו")


def test_fingerprint_differs_for_different_text():
    assert fingerprint("שכר 28 אלף ברוטו") != fingerprint("שכר 29 אלף ברוטו")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("שכר 28 אלף ברוטו…", True),
        ("שכר 28 אלף ברוטו… עוד", True),
        ("salary 28k… See more", True),
        ("שכר 28 אלף ברוטו", False),
        ("ואני רוצה לדעת מה המצב בחברות אחרות סעוד", False),
    ],
)
def test_is_truncated(text, expected):
    assert is_truncated(text) is expected


@pytest.mark.parametrize(
    "url, kind",
    [
        ("https://www.facebook.com/checkpoint/1501092823525282/", "checkpoint"),
        ("https://www.facebook.com/two_step_verification/authentication/", "checkpoint"),
        ("https://www.facebook.com/login/?next=%2Fgroups%2F1", "session_ended"),
        ("https://www.facebook.com/recover/initiate/", "checkpoint"),
    ],
)
def test_block_reason_from_url(url, kind):
    signal = block_reason(url, "")
    assert signal is not None
    assert signal.kind == kind


@pytest.mark.parametrize(
    "page_text, kind",
    [
        ("You’re Temporarily Blocked", "temporary"),
        ("You can’t use this feature right now", "temporary"),
        ("You can't use this feature at the moment", "temporary"),
        ("It looks like you were misusing this feature by going too fast", "temporary"),
        ("This content isn’t available right now", "temporary"),
        ("תוכן זה אינו זמין כרגע", "temporary"),
        ("Your account has been locked", "checkpoint"),
        ("We suspended your account", "checkpoint"),
        ("Please confirm your identity", "checkpoint"),
        ("We noticed suspicious activity", "checkpoint"),
        ("Use another profile", "session_ended"),
    ],
)
def test_block_reason_from_page_text(page_text, kind):
    signal = block_reason("https://www.facebook.com/groups/123", page_text)
    assert signal is not None
    assert signal.kind == kind


def test_normal_feed_is_not_a_block():
    assert block_reason("https://www.facebook.com/groups/123?sorting_setting=CHRONOLOGICAL", SALARY_POST) is None
