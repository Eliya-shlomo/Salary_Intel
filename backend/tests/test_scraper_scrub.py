import asyncio
import json

import pytest

from scraper import privacy_agent, scrub_posts
from scraper.privacy_agent import PrivacyReview
from scraper.scrub_posts import apply_spans, scrub_file


class FakeAgent:
    def __init__(self, reviews):
        self.reviews = list(reviews)
        self.received = []

    async def ainvoke(self, payload):
        self.received.append(payload["messages"][0]["content"])
        return {"structured_response": self.reviews.pop(0)}


@pytest.fixture
def fake_agent(monkeypatch):
    def install(*reviews):
        agent = FakeAgent(reviews)
        monkeypatch.setattr(privacy_agent, "get_privacy_agent", lambda: agent)
        return agent

    return install


def write_raw(path, texts):
    path.write_text("".join(json.dumps({"text": t, "source": "facebook_group"}, ensure_ascii=False) + "\n" for t in texts))
    return path


def test_apply_spans_replaces_only_verified_spans():
    text, removed, problems = apply_spans("שאלתי את דנה כהן ואת @yossi על השכר", ["דנה כהן", "@yossi", "רונית"])

    assert text == "שאלתי את [name] ואת [name] על השכר"
    assert removed == ["דנה כהן", "@yossi"]
    assert problems == ["span not found in post: רונית"]


def test_apply_spans_handles_overlapping_spans():
    text, removed, problems = apply_spans("דנה כהן אמרה, ודנה צדקה", ["דנה", "דנה כהן"])

    assert text == "[name] אמרה, ו[name] צדקה"
    assert problems == []


def test_apply_spans_rejects_spans_that_are_too_long():
    long_span = "זה משפט שלם שהמודל החזיר במקום שם של בן אדם"
    text, removed, problems = apply_spans(long_span + " 30 אלף", [long_span])

    assert removed == []
    assert problems and "too long" in problems[0]


def test_scrub_file_splits_keep_unsure_and_drop(tmp_path, fake_agent):
    raw = write_raw(
        tmp_path / "posts_1.jsonl",
        ["דנה כהן: 30 אלף ברוטו", "מפתח 25 אלף, תתקשרו 050-1234567", "שכר 40 אלף", "הבוס שלי משה מרוויח 90"],
    )
    agent = fake_agent(
        PrivacyReview(spans=["דנה כהן"], decision="keep", reason="name removed"),
        PrivacyReview(spans=[], decision="keep", reason="no names"),
        PrivacyReview(spans=["רונית"], decision="keep", reason="hallucinated span"),
        PrivacyReview(spans=["משה"], decision="drop", reason="third party salary"),
    )

    counts, _ = asyncio.run(scrub_file(raw))

    assert counts == {"keep": 2, "unsure": 1, "drop": 1}
    clean = [json.loads(l)["text"] for l in (tmp_path / "posts_1.clean.jsonl").read_text().splitlines()]
    unsure = [json.loads(l)["text"] for l in (tmp_path / "posts_1.unsure.jsonl").read_text().splitlines()]
    assert clean == ["[name]: 30 אלף ברוטו", "מפתח 25 אלף, תתקשרו [phone]"]
    assert unsure == ["שכר 40 אלף"]
    assert "<post>\nדנה כהן: 30 אלף ברוטו\n</post>" in agent.received[0]
    assert "050-1234567" not in agent.received[1]


@pytest.mark.parametrize("name", ["posts_1.clean.jsonl", "posts_1.unsure.jsonl", "posts_1.results.jsonl", "posts_1.txt"])
def test_scrub_file_refuses_derived_files(tmp_path, fake_agent, name):
    path = write_raw(tmp_path / name, ["שכר 30 אלף"])
    fake_agent()

    with pytest.raises(ValueError):
        asyncio.run(scrub_file(path))


def test_no_unsure_file_when_nothing_is_unsure(tmp_path, fake_agent):
    raw = write_raw(tmp_path / "posts_1.jsonl", ["שכר 30 אלף"])
    fake_agent(PrivacyReview(spans=[], decision="keep", reason="ok"))

    asyncio.run(scrub_file(raw))

    assert not (tmp_path / "posts_1.unsure.jsonl").exists()
    assert scrub_posts.output_paths(raw)[0].exists()
