import pytest

from app.tools.normalize_role import normalize_role


@pytest.mark.parametrize(
    "raw_role, expected",
    [
        ("Backend Developer", "backend"),
        ("back-end developer", "backend"),
        ("Frontend Developer", "frontend"),
        ("Full Stack Developer", "fullstack"),
        ("Senior Fullstack Developer", "fullstack"),
        ("פולסטאק", "fullstack"),
        ("מהנדס Devops בסטארטאפ", "devops"),
        ("DevOps Engineer", "devops"),
        ("SRE", "devops"),
        ("Cloud Engineer", "devops"),
        ("Data Scientist", "data_scientist"),
        ("Machine Learning Engineer", "data_scientist"),
        ("ML Engineer", "data_scientist"),
        ("Data Engineer", "data_engineer"),
        ("אנליסט", "data_analyst"),
        ("מנהלת מוצר", "product_manager"),
        ("PM", "product_manager"),
        ("Cyber Security Analyst", "security"),
        ("Solutions Architect", "architect"),
        ("Team Lead", "team_lead"),
        ("Junior QA Engineer", "qa"),
        ("QA", "qa"),
        ("Mobile Developer", "mobile"),
        ("Full Stack Backend", "fullstack"),
        ("Squad Leader", "other"),
        ("Gardener", "other"),
        ("", "other"),
    ],
)
def test_normalize_role(raw_role, expected):
    assert normalize_role(raw_role) == expected
