"""Synthetic salary posts calibrated on a sourced reference table.

Code picks every fact (role, years, salary, basis, equity, city) from
salary_reference.json. The model only writes Hebrew text around phrases
that code chose, and code then checks the text with the same parse_amount
and normalize_role the pipeline uses. Posts that fail are dropped and counted.

    python -m app.ingestion.calibrated_generator --count 400 --seed 7 --dry-run
    python -m app.ingestion.calibrated_generator --count 400 --seed 7 --out data/synthetic_v2
"""
import argparse
import asyncio
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Awaitable, Callable

from pydantic import BaseModel

from app.ingestion.salary_reference import (
    Cell,
    SalaryReference,
    StatedBasis,
    Style,
    Weights,
    load_reference,
)
from app.tools.normalize_role import CanonicalRole, normalize_role
from app.tools.parse_amount import parse_amount

SOURCE_LABEL = "synthetic_v2"
CONCURRENCY = 5
ROUND_TO = 500
MAX_Z = 2.0
Z_75 = 0.6745

# Every title must normalize back to its role; a test checks this.
ROLE_TITLES: dict[str, list[str]] = {
    "fullstack": ["Fullstack Developer", "מפתח פולסטאק", "Full Stack Engineer"],
    "backend": ["Backend Developer", "מפתח בקאנד", "Backend Engineer"],
    "frontend": ["Frontend Developer", "מפתחת פרונטאנד", "Frontend Engineer"],
    "mobile": ["Mobile Developer", "מפתח אנדרואיד", "Android Developer"],
    "devops": ["DevOps Engineer", "דבאופס", "SRE"],
    "data_scientist": ["Data Scientist", "מדען נתונים", "ML Engineer"],
    "data_engineer": ["Data Engineer", "מהנדס נתונים"],
    "data_analyst": ["Data Analyst", "אנליסטית נתונים"],
    "qa": ["QA Engineer", "QA Automation", "בודק תוכנה"],
    "security": ["Security Engineer", "חוקר אבטחת מידע", "Security Researcher"],
    "architect": ["Software Architect", "ארכיטקט תוכנה", "Solution Architect"],
    "team_lead": ["Team Lead", "ראש צוות", "Tech Lead"],
    "product_manager": ["Product Manager", "מנהלת מוצר"],
}

# Style only, not checked: without it almost every post opens with "היי חברים".
OPENINGS = ["", "", "", "היי,", "שאלה לקבוצה:", "מתלבט ורוצה דעות.", "אנונימי כמובן.", "קצת שקיפות:"]

EQUITY_WORDS = ("אופציות", "אופציה", "מניות", "options", "rsu", "equity", "espp")
BASIS_WORDS = ("ברוטו", "נטו")
NO_CITY = "none"


class PostFacts(BaseModel):
    style: Style
    role: CanonicalRole
    role_title: str
    bucket: str
    years_experience: int
    years_phrase: str
    salary: int | None
    salary_phrase: str | None
    second_salary: int | None
    second_salary_phrase: str | None
    pay_basis: StatedBasis
    has_equity: bool
    city: str | None
    opening: str = ""
    cell_sources: list[str]

    @property
    def is_salary_post(self) -> bool:
        return self.salary is not None


class GeneratedPost(BaseModel):
    id: str
    raw_text: str
    facts: PostFacts


class GenerationReport(BaseModel):
    posts: list[GeneratedPost]
    attempts: int
    rejected: dict[str, int]


WriteFn = Callable[[PostFacts], Awaitable[str]]


def _pick(rng: random.Random, weights: dict[str, float]) -> str:
    keys = list(weights)
    return rng.choices(keys, weights=[weights[k] for k in keys])[0]


def sample_salary(cell: Cell, rng: random.Random) -> int:
    """Draw from a split log-normal that passes through p25, median and p75.

    Below the median the spread comes from p25, above it from p75, so a
    skewed cell keeps its skew. Tails are cut at MAX_Z standard deviations.
    """
    z = max(-MAX_Z, min(MAX_Z, rng.gauss(0, 1)))
    if z < 0:
        sigma = math.log(cell.median / cell.p25) / Z_75
    else:
        sigma = math.log(cell.p75 / cell.median) / Z_75
    value = cell.median * math.exp(z * sigma)
    return int(round(value / ROUND_TO) * ROUND_TO)


def salary_phrase(amount: int, basis: StatedBasis, rng: random.Random) -> str:
    """A way of writing the amount that parse_amount reads back exactly."""
    formats = [f"{amount:,} ₪", f"{amount:,} ש״ח"]
    if amount % 1000 == 0:
        thousands = amount // 1000
        formats += [f"{thousands}K", f"{thousands} א׳", f"{thousands} אלף"]
    phrase = rng.choice(formats)
    return f"{phrase} ברוטו" if basis == "gross" else phrase


def years_phrase(years: int, rng: random.Random) -> str:
    if years == 0:
        return "בלי ניסיון"
    if years == 1:
        return "שנת ניסיון"
    if years == 2:
        return "שנתיים ניסיון"
    return rng.choice([f"{years} שנות ניסיון", f"{years} שנים ניסיון"])


def sample_facts(reference: SalaryReference, rng: random.Random) -> PostFacts:
    role = _pick(rng, reference.role_weights.values)
    available = {
        name: weight
        for name, weight in reference.bucket_weights.values.items()
        if reference.cell(role, name)
    }
    bucket_name = _pick(rng, available)
    bucket = reference.bucket(bucket_name)
    cell = reference.cell(role, bucket_name)

    style = _pick(rng, reference.style_weights.values)
    basis = _pick(rng, reference.basis_weights.values)
    years = rng.randint(bucket.min_years, bucket.max_years)
    city = _pick(rng, reference.city_weights.values)

    salary = phrase = second = second_phrase = None
    if style != "question_no_salary":
        salary = sample_salary(cell, rng)
        phrase = salary_phrase(salary, basis, rng)
    if style == "compare_offers":
        second = sample_salary(cell, rng)
        while abs(second - salary) < 1000:
            second = sample_salary(cell, rng)
        second_phrase = salary_phrase(second, basis, rng)

    return PostFacts(
        style=style,
        role=role,
        role_title=rng.choice(ROLE_TITLES[role]),
        bucket=bucket_name,
        years_experience=years,
        years_phrase=years_phrase(years, rng),
        salary=salary,
        salary_phrase=phrase,
        second_salary=second,
        second_salary_phrase=second_phrase,
        pay_basis=basis if salary is not None else "unknown",
        has_equity=salary is not None and rng.random() < reference.equity_share.value,
        city=None if city == NO_CITY else city,
        opening=rng.choice(OPENINGS),
        cell_sources=cell.sources,
    )


def required_phrases(facts: PostFacts) -> list[str]:
    """Phrases the writer must copy verbatim; code chose every one of them."""
    optional = (facts.salary_phrase, facts.second_salary_phrase, facts.city)
    return [facts.role_title, facts.years_phrase] + [p for p in optional if p]


def verify_post(text: str, facts: PostFacts) -> list[str]:
    """Return the reasons a post does not carry its facts. Empty means it does."""
    problems = []
    lowered = text.lower()

    for phrase in required_phrases(facts):
        if phrase not in text:
            problems.append(f"missing phrase: {phrase}")

    if normalize_role(facts.role_title) != facts.role:
        problems.append("role title does not normalize to the role")
    if normalize_role(text) != facts.role:
        problems.append("post text normalizes to another role")

    parsed = parse_amount(text)
    if facts.salary is None:
        if parsed.salary_min is not None:
            problems.append("question post contains a salary")
    else:
        if parsed.salary_min != facts.salary or parsed.salary_max != facts.salary:
            problems.append("first parsed salary is not the chosen salary")
        if parsed.pay_basis != facts.pay_basis:
            problems.append("parsed pay basis differs")

    if facts.pay_basis == "unknown" and any(w in text for w in BASIS_WORDS):
        problems.append("basis word in a post without a stated basis")
    if facts.pay_basis == "gross" and "נטו" in text:
        problems.append("net mentioned in a gross post")

    mentions_equity = any(w in lowered for w in EQUITY_WORDS)
    if mentions_equity != facts.has_equity:
        problems.append("equity mention does not match")

    return problems


async def generate(
    reference: SalaryReference,
    count: int,
    write: WriteFn,
    seed: int = 0,
    max_attempts: int | None = None,
) -> GenerationReport:
    rng = random.Random(seed)
    max_attempts = max_attempts or count * 2
    semaphore = asyncio.Semaphore(CONCURRENCY)
    posts: list[GeneratedPost] = []
    rejected: Counter = Counter()
    attempts = 0

    async def attempt(facts: PostFacts) -> tuple[PostFacts, str | None, list[str]]:
        async with semaphore:
            try:
                text = await write(facts)
            except Exception as error:
                return facts, None, [f"writer error: {type(error).__name__}"]
        return facts, text, verify_post(text, facts)

    while len(posts) < count and attempts < max_attempts:
        batch_size = min(count - len(posts), max_attempts - attempts)
        batch = [sample_facts(reference, rng) for _ in range(batch_size)]
        attempts += batch_size
        for facts, text, problems in await asyncio.gather(*map(attempt, batch)):
            if problems:
                rejected[problems[0].split(":")[0]] += 1
                continue
            posts.append(
                GeneratedPost(id=f"syn2-{len(posts) + 1:04d}", raw_text=text, facts=facts)
            )

    return GenerationReport(posts=posts, attempts=attempts, rejected=dict(rejected))


def write_outputs(report: GenerationReport, out_dir: Path, reference: SalaryReference) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "posts.jsonl", "w", encoding="utf-8") as posts_file:
        for post in report.posts:
            row = {"id": post.id, "raw_text": post.raw_text, "source": SOURCE_LABEL}
            posts_file.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(out_dir / "ground_truth.jsonl", "w", encoding="utf-8") as truth_file:
        for post in report.posts:
            row = {"id": post.id, "raw_text": post.raw_text, **post.facts.model_dump()}
            row["is_salary_post"] = post.facts.is_salary_post
            truth_file.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = {
        "reference_version": reference.version,
        "accepted": len(report.posts),
        "attempts": report.attempts,
        "rejected": report.rejected,
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))


def describe_sample(reference: SalaryReference, count: int, seed: int) -> dict:
    rng = random.Random(seed)
    facts = [sample_facts(reference, rng) for _ in range(count)]
    return {
        "styles": Counter(f.style for f in facts),
        "roles": Counter(f.role for f in facts),
        "buckets": Counter(f.bucket for f in facts),
        "with_equity": sum(f.has_equity for f in facts),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=400)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", type=Path, default=Path("data/synthetic_v2"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    reference = load_reference()
    if args.dry_run:
        for name, value in describe_sample(reference, args.count, args.seed).items():
            print(f"{name}: {dict(value) if isinstance(value, Counter) else value}")
        print(f"writer calls: at least {args.count}, at most {args.count * 2}")
        return

    from app.agents.post_writer_agent import write_post

    report = asyncio.run(generate(reference, args.count, write_post, seed=args.seed))
    write_outputs(report, args.out, reference)
    print(f"accepted {len(report.posts)} of {report.attempts} attempts")
    print(f"rejected: {report.rejected}")


if __name__ == "__main__":
    main()
