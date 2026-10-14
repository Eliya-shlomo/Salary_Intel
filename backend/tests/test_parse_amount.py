import pytest

from app.tools.parse_amount import parse_amount


@pytest.mark.parametrize(
    "text, expected_min, expected_max, expected_basis",
    [
        ("מהנדס Devops בסטארטאפ. 62 א׳ ברוטו + אופציות", 62_000, 62_000, "gross"),
        ("משכורת 10,500 ברוטו", 10_500, 10_500, "gross"),
        ("משכורת סביב 25 נטו", 25_000, 25_000, "net"),
        ("בין 50 ל-60 א׳ נטו", 50_000, 60_000, "net"),
        ("מה לעשות מפה?", None, None, "unknown"),
        ("19 ברוטו . החברה ממש קרובה לבית", 19_000, 19_000, "gross"),
        ("ניסיון של 10 שנים, בת 50", None, None, "unknown"),
        ("צברתי בפנסיה 210,000", None, None, "unknown"),
        ("60 א׳ + אופציות", 60_000, 60_000, "unknown"),
        ("השכר שלי ₪30,000 לחודש", 30_000, 30_000, "unknown"),
        ("₪ 28,000 ברוטו", 28_000, 28_000, "gross"),
    ],
)
def test_parse_amount(text, expected_min, expected_max, expected_basis):
    result = parse_amount(text)

    assert result.salary_min == expected_min
    assert result.salary_max == expected_max
    assert result.pay_basis == expected_basis
