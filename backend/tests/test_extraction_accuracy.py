from evals.extraction_accuracy import score


def truth(id, salary=30000, **overrides):
    row = {
        "id": id,
        "role": "backend",
        "salary": salary,
        "pay_basis": "gross",
        "has_equity": False,
        "years_experience": 4,
        "is_salary_post": salary is not None,
    }
    row.update(overrides)
    return row


def saved(**overrides):
    row = {
        "role": "backend",
        "salary_min": 30000,
        "salary_max": 30000,
        "pay_basis": "gross",
        "has_equity": None,
        "years_experience": 4,
    }
    row.update(overrides)
    return row


def test_scores_fields_and_counts_outcomes():
    truths = [truth("a"), truth("b"), truth("c", salary=None), truth("d"), truth("e")]
    results = [
        {"id": "a", "status": "approved", "post_id": 1},
        {"id": "b", "status": "pending", "post_id": 2},
        {"id": "c", "status": "rejected", "post_id": None},
        {"id": "d", "status": "duplicate", "post_id": None},
        {"id": "e", "status": "rejected", "post_id": None},
    ]
    rows = {1: saved(), 2: saved(role="fullstack", years_experience=None)}

    report = score(truths, results, rows)

    assert report["outcomes"] == {
        "salary post approved": 1,
        "salary post pending": 1,
        "question rejected": 1,
        "duplicate": 1,
        "salary post rejected": 1,
    }
    assert report["scored"] == 2
    assert report["accuracy"]["salary"] == 1.0
    assert report["accuracy"]["role"] == 0.5
    assert report["all_fields_correct"] == 0.5
    assert report["misses"] == [{"id": "b", "wrong": ["role", "years_experience"]}]


def test_question_post_that_gets_in_is_counted():
    report = score(
        [truth("q", salary=None)],
        [{"id": "q", "status": "pending", "post_id": 9}],
        {},
    )
    assert report["outcomes"] == {"question admitted": 1}
