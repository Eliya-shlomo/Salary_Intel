import uuid

from app.db.models import SalaryPost
from app.tools.find_duplicate import find_duplicate, normalize_for_dedup

DIMENSIONS = 1536


def unit_vector(*leading: float) -> list[float]:
    return list(leading) + [0.0] * (DIMENSIONS - len(leading))


def add_post(db, raw_text, embedding=None):
    post = SalaryPost(raw_text=raw_text, embedding=embedding)
    db.add(post)
    db.flush()
    return post


def unique_text(label="post"):
    return f"{label} {uuid.uuid4()} 62 א׳ ברוטו"


def test_normalize_ignores_case_and_whitespace():
    assert normalize_for_dedup("  62 א׳   ברוטו  ") == normalize_for_dedup("62 א׳ ברוטו")
    assert normalize_for_dedup("Devops  Engineer") == "devops engineer"


def test_exact_duplicate_is_found(db):
    text = unique_text()
    post = add_post(db, text)

    match = find_duplicate(db, text)

    assert match.kind == "exact"
    assert match.post_id == post.id


def test_exact_duplicate_ignores_whitespace_and_case(db):
    text = unique_text("Devops")
    post = add_post(db, text)

    match = find_duplicate(db, f"  {text.upper()}  ".replace(" ", "   "))

    assert match.kind == "exact"
    assert match.post_id == post.id


def test_different_text_without_embedding_is_not_a_duplicate(db):
    add_post(db, unique_text())

    assert find_duplicate(db, unique_text("other")) is None


def test_near_duplicate_is_found_by_embedding(db):
    post = add_post(db, unique_text(), embedding=unit_vector(1.0))

    match = find_duplicate(db, unique_text("emoji 🙂"), embedding=unit_vector(1.0, 0.01))

    assert match.kind == "near"
    assert match.post_id == post.id
    assert match.similarity >= 0.99


def test_far_embedding_is_not_a_duplicate(db):
    add_post(db, unique_text(), embedding=unit_vector(1.0))

    match = find_duplicate(db, unique_text("other"), embedding=unit_vector(0.0, 1.0))

    assert match is None
