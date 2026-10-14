import pytest
from pydantic import ValidationError

from app.agents.analyst_tools import salary_stats, search_posts


def test_salary_stats_schema_lists_only_closed_roles():
    schema = salary_stats.args_schema.model_json_schema()
    role_schema = schema["properties"]["role"]

    assert "devops" in str(role_schema)
    assert "gardener" not in str(role_schema)


def test_salary_stats_rejects_unknown_role():
    with pytest.raises(ValidationError):
        salary_stats.invoke({"role": "gardener"})


def test_salary_stats_returns_compact_result_from_real_database():
    result = salary_stats.invoke({"role": "devops"})

    assert set(result) == {"n", "p25", "p50", "p75", "note"}
    assert result["n"] >= 0


def test_search_posts_description_tells_the_model_what_it_is_for():
    assert "relevant" in search_posts.description
    assert "not to compute statistics" in search_posts.description
