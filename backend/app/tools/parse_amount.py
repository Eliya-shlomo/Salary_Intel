import re
from typing import Literal

from pydantic import BaseModel


PayBasisValue = Literal["gross", "net", "unknown"]


class ParsedAmount(BaseModel):
    salary_min: float | None
    salary_max: float | None
    pay_basis: PayBasisValue


NUMBER = r"\d+(?:,\d{3})*"

AMOUNT_PATTERN = re.compile(
    rf"(?P<prefix>₪\s*)?(?P<low>{NUMBER})"
    rf"(?:\s*(?:-|–|ל-|ל|עד)\s*(?P<high>{NUMBER}))?"
    r"(?:\s*(?P<unit>א[׳']|אלף|₪|ש[\"״]ח|שח|[kK]\b))?"
    r"(?:\s*(?P<basis>ברוטו|נטו))?"
)

BASIS_BY_WORD = {"ברוטו": "gross", "נטו": "net"}


def _to_monthly_shekels(raw: str) -> float:
    value = float(raw.replace(",", ""))
    return value * 1000 if value < 1000 else value


def parse_amount(text: str) -> ParsedAmount:
    for match in AMOUNT_PATTERN.finditer(text):
        if not (match["unit"] or match["basis"] or match["prefix"]):
            continue

        low = _to_monthly_shekels(match["low"])
        high = _to_monthly_shekels(match["high"]) if match["high"] else low
        return ParsedAmount(
            salary_min=min(low, high),
            salary_max=max(low, high),
            pay_basis=BASIS_BY_WORD.get(match["basis"], "unknown"),
        )

    return ParsedAmount(salary_min=None, salary_max=None, pay_basis="unknown")
