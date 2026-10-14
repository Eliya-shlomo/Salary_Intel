import hashlib
import re
import unicodedata
from typing import Literal, NamedTuple

EMAIL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?972|0)[\s-]?\d{1,2}[\s-]?\d{3}[\s-]?\d{4}(?!\d)")
URL_RE = re.compile(r"(?:https?://|www\.)\S+")
SALARY_HINT_RE = re.compile(r"(₪|א׳|אלף|ברוטו|נטו|שכר|משכורת|\d\s*[kK]\b)")
HIDDEN_CHARS_RE = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u2069\ufeff]")
TRAILING_MARKER_RE = re.compile(r"(?:…|(?<![^\s…])(?:see more|עוד))\s*$", re.IGNORECASE)

MIN_POST_CHARS = 40

BlockKind = Literal["temporary", "checkpoint", "session_ended"]

BLOCK_URL_MARKERS: dict[str, BlockKind] = {
    "/checkpoint": "checkpoint",
    "/recover": "checkpoint",
    "captcha": "checkpoint",
    "two_step_verification": "checkpoint",
    "/authentication": "checkpoint",
    "/login": "session_ended",
}
BLOCK_TEXT_MARKERS: dict[str, BlockKind] = {
    "temporarily blocked": "temporary",
    "you can't use this feature": "temporary",
    "going too fast": "temporary",
    "misusing this feature": "temporary",
    "this content isn't available": "temporary",
    "נחסמת זמנית": "temporary",
    "תוכן זה אינו זמין": "temporary",
    "unusual activity": "checkpoint",
    "suspicious activity": "checkpoint",
    "account has been locked": "checkpoint",
    "we suspended your account": "checkpoint",
    "confirm your identity": "checkpoint",
    "confirm you're human": "checkpoint",
    "security check": "checkpoint",
    "פעילות חריגה": "checkpoint",
    "use another profile": "session_ended",
}


class BlockSignal(NamedTuple):
    kind: BlockKind
    reason: str


def redact(text: str) -> str:
    text = EMAIL_RE.sub("[email]", text)
    text = URL_RE.sub("[link]", text)
    return PHONE_RE.sub("[phone]", text)


def looks_like_salary_post(text: str) -> bool:
    return (
        len(text.strip()) >= MIN_POST_CHARS
        and any(c.isdigit() for c in text)
        and bool(SALARY_HINT_RE.search(text))
    )


def is_truncated(text: str) -> bool:
    return bool(TRAILING_MARKER_RE.search(text))


def strip_truncation(text: str) -> str:
    while match := TRAILING_MARKER_RE.search(text):
        text = text[: match.start()].rstrip()
    return text


def fingerprint(text: str) -> str:
    text = HIDDEN_CHARS_RE.sub("", unicodedata.normalize("NFC", text))
    squashed = " ".join(strip_truncation(text).split())
    return hashlib.sha1(squashed.encode("utf-8")).hexdigest()


def block_reason(url: str, page_text: str) -> BlockSignal | None:
    lowered_url = url.lower()
    for marker, kind in BLOCK_URL_MARKERS.items():
        if marker in lowered_url:
            return BlockSignal(kind, f"url contains '{marker}'")
    lowered_text = page_text.replace("’", "'").replace("‘", "'").lower()
    for marker, kind in BLOCK_TEXT_MARKERS.items():
        if marker in lowered_text:
            return BlockSignal(kind, f"page says '{marker}'")
    return None
