import asyncio
import json
import random
from statistics import median

import pytest

from app.ingestion.calibrated_generator import (
    ROLE_TITLES,
    SOURCE_LABEL,
    PostFacts,
    generate,
    required_phrases,
    salary_phrase,
    sample_facts,
    sample_salary,
    verify_post,
    write_outputs,
)
from app.ingestion.salary_reference import Cell, load_reference
from app.tools.normalize_role import normalize_role
from app.tools.parse_amount import parse_amount

REFERENCE = load_reference()


def cell(p25=25000, med=30000, p75=40000):
    return Cell(
        role="backend", bucket="mid", p25=p25, median=med, p75=p75,
        sources=["x"], publishers=1, confidence="low", year=2026,
    )


def facts(**overrides):
    fields = {
        "style": "update",
        "role": "backend",
        "role_title": "Backend Developer",
        "bucket": "mid",
        "years_experience": 4,
        "years_phrase": "4 שנות ניסיון",
        "salary": 31000,
        "salary_phrase": "31K ברוטו",
        "second_salary": None,
        "second_salary_phrase": None,
        "pay_basis": "gross",
        "has_equity": False,
        "city": "חיפה",
        "cell_sources": ["IL-S6"],
    }
    fields.update(overrides)
    return PostFacts(**fields)


def template_post(f: PostFacts) -> str:
    text = f"היי, אני {f.role_title} עם {f.years_phrase}"
    if f.city:
        text += f", עובד ב{f.city}"
    if f.salary_phrase:
        text += f". קיבלתי הצעה של {f.salary_phrase}"
    if f.second_salary_phrase:
        text += f" ועוד אחת של {f.second_salary_phrase}"
    if f.has_equity:
        text += " + אופציות"
    return text + ". מה אתם אומרים?"


async def template_writer(f: PostFacts) -> str:
    return template_post(f)


@pytest.mark.parametrize("role", list(ROLE_TITLES))
def test_every_title_normalizes_to_its_role(role):
    for title in ROLE_TITLES[role]:
        assert normalize_role(title) == role


def test_every_reference_role_has_titles():
    assert {c.role for c in REFERENCE.cells} <= set(ROLE_TITLES)


@pytest.mark.parametrize("amount", [18000, 23500, 31000, 44000, 52500])
@pytest.mark.parametrize("basis", ["gross", "unknown"])
def test_salary_phrase_parses_back_exactly(amount, basis):
    rng = random.Random(amount)
    for _ in range(20):
        parsed = parse_amount(salary_phrase(amount, basis, rng))
        assert parsed.salary_min == parsed.salary_max == amount
        assert parsed.pay_basis == basis


def test_sampled_salaries_match_the_cell_quantiles():
    rng = random.Random(1)
    c = cell()
    values = sorted(sample_salary(c, rng) for _ in range(4000))
    assert abs(median(values) - c.median) <= 500
    assert abs(values[len(values) // 4] - c.p25) <= 750
    assert abs(values[3 * len(values) // 4] - c.p75) <= 750
    assert all(v % 500 == 0 for v in values)


def test_question_posts_have_no_salary_and_compare_posts_have_two():
    rng = random.Random(3)
    sampled = [sample_facts(REFERENCE, rng) for _ in range(500)]
    for f in sampled:
        if f.style == "question_no_salary":
            assert f.salary is None and not f.has_equity
        if f.style == "compare_offers":
            assert abs(f.second_salary - f.salary) >= 1000


def test_leadership_roles_are_sampled_only_where_cells_exist():
    rng = random.Random(4)
    for _ in range(500):
        f = sample_facts(REFERENCE, rng)
        assert REFERENCE.cell(f.role, f.bucket) is not None


def test_verify_accepts_a_post_that_carries_its_facts():
    f = facts()
    assert verify_post(template_post(f), f) == []


def test_verify_rejects_a_missing_phrase():
    f = facts()
    text = template_post(f).replace("31K ברוטו", "31 אלף ברוטו")
    assert "missing phrase: 31K ברוטו" in verify_post(text, f)


def test_verify_rejects_an_earlier_amount():
    f = facts()
    text = "עברתי מ-25K. " + template_post(f)
    assert "first parsed salary is not the chosen salary" in verify_post(text, f)


def test_verify_rejects_another_role_in_the_text():
    f = facts()
    text = template_post(f) + " אולי לעבור לפולסטאק?"
    assert "post text normalizes to another role" in verify_post(text, f)


def test_verify_rejects_equity_mismatch_both_ways():
    with_equity = facts(has_equity=True)
    assert "equity mention does not match" in verify_post(
        template_post(facts()), with_equity
    )
    assert "equity mention does not match" in verify_post(
        template_post(facts()) + " יש גם RSU", facts()
    )


def test_verify_rejects_a_basis_word_when_basis_is_unknown():
    f = facts(salary_phrase="31K", pay_basis="unknown")
    assert "basis word in a post without a stated basis" in verify_post(
        template_post(f) + " נטו בערך", f
    )


def test_verify_rejects_a_question_post_with_an_amount():
    f = facts(style="question_no_salary", salary=None, salary_phrase=None, pay_basis="unknown")
    assert "question post contains a salary" in verify_post(
        template_post(f) + " שמעתי שמשלמים 30K", f
    )


def test_required_phrases_skip_missing_parts():
    f = facts(city=None, salary=None, salary_phrase=None, pay_basis="unknown")
    assert required_phrases(f) == ["Backend Developer", "4 שנות ניסיון"]


def test_generate_keeps_posts_that_pass_and_records_the_truth():
    report = asyncio.run(generate(REFERENCE, 60, template_writer, seed=5))
    assert len(report.posts) == 60
    assert report.attempts == 60
    for post in report.posts:
        parsed = parse_amount(post.raw_text)
        assert parsed.salary_min == post.facts.salary
        assert normalize_role(post.raw_text) == post.facts.role


def test_generate_drops_and_counts_bad_posts():
    calls = 0

    async def sometimes_wrong(f):
        nonlocal calls
        calls += 1
        if calls % 3 == 0:
            return "עברתי מ-12K. " + template_post(f)
        if calls % 7 == 0:
            raise TimeoutError
        return template_post(f)

    report = asyncio.run(generate(REFERENCE, 30, sometimes_wrong, seed=6))
    assert len(report.posts) == 30
    assert report.attempts > 30
    assert sum(report.rejected.values()) == report.attempts - 30
    assert report.rejected.get("writer error")


def test_generate_stops_at_max_attempts():
    async def always_wrong(f):
        return "סתם פוסט"

    report = asyncio.run(generate(REFERENCE, 10, always_wrong, seed=7, max_attempts=15))
    assert report.posts == []
    assert report.attempts == 15


def test_same_seed_gives_the_same_dataset():
    first = asyncio.run(generate(REFERENCE, 20, template_writer, seed=8))
    second = asyncio.run(generate(REFERENCE, 20, template_writer, seed=8))
    assert [p.raw_text for p in first.posts] == [p.raw_text for p in second.posts]


def test_write_outputs(tmp_path):
    report = asyncio.run(generate(REFERENCE, 5, template_writer, seed=9))
    write_outputs(report, tmp_path, REFERENCE)

    posts = [json.loads(line) for line in (tmp_path / "posts.jsonl").read_text().splitlines()]
    truth = [json.loads(line) for line in (tmp_path / "ground_truth.jsonl").read_text().splitlines()]
    assert {p["source"] for p in posts} == {SOURCE_LABEL}
    assert [p["id"] for p in posts] == [t["id"] for t in truth]
    assert all("cell_sources" in t and "is_salary_post" in t for t in truth)
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert summary["accepted"] == 5
