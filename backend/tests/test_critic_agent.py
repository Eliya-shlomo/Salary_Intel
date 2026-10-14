import asyncio

import pytest

from app.agents import critic_agent
from app.agents.critic_agent import (
    ISSUE_BY_CHECK,
    CriticChecks,
    critique_candidate,
    verdict_from_checks,
)
from app.ingestion.candidate import Candidate

ALL_TRUE = dict.fromkeys(ISSUE_BY_CHECK, True)

CANDIDATE = Candidate(
    is_salary_post=True,
    role="backend",
    salary_min=30_000,
    salary_max=30_000,
    pay_basis="gross",
    years_experience=4,
    has_equity=None,
    evidence="30 א׳ ברוטו",
    evidence_found=True,
)


def test_all_checks_true_means_agreement():
    verdict = verdict_from_checks(CriticChecks(**ALL_TRUE))

    assert verdict.agrees
    assert verdict.issues == []


@pytest.mark.parametrize("failed_check", list(ISSUE_BY_CHECK))
def test_one_failed_check_disagrees_with_its_own_issue(failed_check):
    verdict = verdict_from_checks(CriticChecks(**{**ALL_TRUE, failed_check: False}))

    assert not verdict.agrees
    assert verdict.issues == [ISSUE_BY_CHECK[failed_check]]


def test_critique_candidate_converts_agent_output(monkeypatch):
    class FakeCritic:
        received = None

        async def ainvoke(self, payload):
            FakeCritic.received = payload
            return {"structured_response": CriticChecks(**{**ALL_TRUE, "role_label_fits": False})}

    monkeypatch.setattr(critic_agent, "get_critic", lambda: FakeCritic())

    verdict = asyncio.run(critique_candidate("post text", CANDIDATE))

    assert not verdict.agrees
    assert verdict.issues == [ISSUE_BY_CHECK["role_label_fits"]]
    content = FakeCritic.received["messages"][0]["content"]
    assert "<post>\npost text\n</post>" in content
