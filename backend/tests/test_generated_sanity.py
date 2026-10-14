from evals.generated_sanity import check
from app.ingestion.salary_reference import load_reference

REFERENCE = load_reference()


def truth_rows(role, bucket, salaries):
    return [{"role": role, "bucket": bucket, "salary": s} for s in salaries]


def test_flags_a_cell_far_from_the_reference():
    cell = REFERENCE.cell("fullstack", "mid")
    far = int(cell.median * 1.3)
    rows = check(truth_rows("fullstack", "mid", [far] * 6), REFERENCE)
    row = next(r for r in rows if r["role"] == "fullstack" and r["bucket"] == "mid")
    assert row["status"] == "FLAG"


def test_accepts_a_cell_near_the_reference_and_ignores_question_posts():
    cell = REFERENCE.cell("qa", "junior")
    truth = truth_rows("qa", "junior", [cell.median] * 5 + [None] * 3)
    row = next(r for r in check(truth, REFERENCE) if r["role"] == "qa" and r["bucket"] == "junior")
    assert (row["status"], row["n"]) == ("ok", 5)


def test_reports_cells_with_too_few_posts():
    rows = check(truth_rows("qa", "mid", [20000] * 2), REFERENCE)
    row = next(r for r in rows if r["role"] == "qa" and r["bucket"] == "mid")
    assert row["status"] == "few"
