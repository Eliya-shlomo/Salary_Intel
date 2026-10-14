import re
from typing import Literal

CanonicalRole = Literal[
    "fullstack",
    "backend",
    "frontend",
    "mobile",
    "devops",
    "data_scientist",
    "data_engineer",
    "data_analyst",
    "qa",
    "security",
    "architect",
    "team_lead",
    "product_manager",
    "other",
]

# Order matters: the first role with a matching keyword wins,
# so the more specific roles must come before the general ones.
# `parts` match anywhere in the compacted text, `words` only as a whole word.
ROLE_RULES: list[tuple[CanonicalRole, tuple[str, ...], tuple[str, ...]]] = [
    ("fullstack", ("fullstack", "פולסטאק", "פולסטק"), ()),
    ("devops", ("devops", "דבאופס", "דבופס", "cloudengineer"), ("sre",)),
    ("data_scientist", ("datascientist", "מדעןנתונים", "mlengineer", "machinelearning"), ()),
    ("data_engineer", ("dataengineer", "מהנדסנתונים"), ()),
    ("data_analyst", ("dataanalyst", "אנליסט"), ()),
    ("product_manager", ("productmanager", "מנהלמוצר", "מנהלתמוצר"), ("pm",)),
    ("security", ("security", "אבטחת"), ()),
    ("architect", ("architect", "ארכיטקט"), ()),
    ("team_lead", ("teamlead", "techlead", "מנהלצוות", "ראשצוות"), ()),
    ("qa", ("qaengineer", "qatester", "qaautomation", "בודקתוכנה"), ("qa",)),
    ("mobile", ("mobile", "android", "אנדרואיד"), ()),
    ("backend", ("backend", "בקאנד", "בקנד"), ()),
    ("frontend", ("frontend", "פרונטאנד", "פרונטנד"), ()),
]


def _compact(text: str) -> str:
    return re.sub(r"[\s\-_/.]", "", text.lower())


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+|[֐-׿]+", text.lower()))


def normalize_role(raw_role: str) -> CanonicalRole:
    compact = _compact(raw_role)
    words = _words(raw_role)
    for role, parts, whole_words in ROLE_RULES:
        if any(part in compact for part in parts) or words & set(whole_words):
            return role
    return "other"
