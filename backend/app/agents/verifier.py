import json
import re

from pydantic import BaseModel

from app.agents.subagents import DATA_MARKER

NUMBER_RE = re.compile(
    r"(?<![A-Za-z\d])(\d+(?:,\d{3})*(?:\.\d+)?)"
    r"(\s*(?:[kK](?![A-Za-z])|אלף|א׳))?"
)
LIST_MARKER_RE = re.compile(r"(?m)^\s*\d+[.)]\s+")
PERCENTILE_KEY_RE = re.compile(r"^p(\d{1,2})$")
TOLERANCE = 0.5


class Verification(BaseModel):
    ok: bool
    unsupported: list[float]


def extract_numbers(text: str) -> set[float]:
    numbers = set()
    for digits, thousands in NUMBER_RE.findall(LIST_MARKER_RE.sub("", text)):
        value = float(digits.replace(",", ""))
        numbers.add(value * 1000 if thousands else value)
    return numbers


def _numbers_in_json(value) -> set[float]:
    if isinstance(value, bool):
        return set()
    if isinstance(value, (int, float)):
        return {float(value)}
    if isinstance(value, dict):
        labels = {
            float(m.group(1)) for k in value if (m := PERCENTILE_KEY_RE.match(str(k)))
        }
        return labels.union(*(_numbers_in_json(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(_numbers_in_json(v) for v in value), set())
    return set()


def numbers_from_report(report: str) -> set[float]:
    _, marker, data = report.partition(f"{DATA_MARKER}\n")
    if not marker:
        return set()
    try:
        items = json.loads(data)
    except json.JSONDecodeError:
        return extract_numbers(data)
    numbers = set()
    for item in items:
        try:
            numbers |= _numbers_in_json(json.loads(item))
        except (json.JSONDecodeError, TypeError):
            numbers |= extract_numbers(str(item))
    return numbers


def _is_allowed(number: float, allowed: set[float]) -> bool:
    return any(abs(number - a) <= TOLERANCE for a in allowed)


def verify_answer(question: str, answer: str, reports: list[str]) -> Verification:
    allowed = extract_numbers(question)
    for report in reports:
        allowed |= numbers_from_report(report)
    unsupported = sorted(
        n for n in extract_numbers(answer) if not _is_allowed(n, allowed)
    )
    return Verification(ok=not unsupported, unsupported=unsupported)
