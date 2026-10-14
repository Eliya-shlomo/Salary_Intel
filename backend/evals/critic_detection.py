import asyncio
import json
from pathlib import Path

from app.agents.critic_agent import critique_candidate
from app.agents.extractor_agent import PostExtraction
from app.ingestion.candidate import Candidate, build_candidate
from evals.ablation_cases import CASES, Case

CONCURRENCY = 5
RESULTS_PATH = Path(__file__).parent / "results" / "critic_detection.json"
SWAP_BASIS = {"gross": "net", "net": "gross", "unknown": "gross"}
TECHNICAL_ROLES = {"backend", "fullstack", "frontend", "mobile", "devops"}


def ideal_candidate(case: Case) -> Candidate:
    extraction = PostExtraction(
        is_salary_post=True,
        role_text=case.role_text,
        salary_text=case.salary_text,
        years_experience=None,
        has_equity=case.has_equity,
        evidence=case.salary_text,
    )
    return build_candidate(case.post, extraction)


def corruptions(candidate: Candidate) -> dict[str, Candidate]:
    wrong_role = "product_manager" if candidate.role in TECHNICAL_ROLES else "frontend"
    return {
        "clean": candidate,
        "wrong_basis": candidate.model_copy(
            update={"pay_basis": SWAP_BASIS[candidate.pay_basis]}
        ),
        "wrong_role": candidate.model_copy(update={"role": wrong_role}),
        "wrong_equity": candidate.model_copy(
            update={"has_equity": not candidate.has_equity}
        ),
    }


async def judge(case, kind, candidate, semaphore) -> dict:
    async with semaphore:
        verdict = await critique_candidate(case.post, candidate)
        return {"id": case.id, "kind": kind, "flagged": not verdict.agrees}


async def main() -> None:
    semaphore = asyncio.Semaphore(CONCURRENCY)
    jobs = [
        judge(case, kind, candidate, semaphore)
        for case in CASES
        if case.is_salary_post
        for kind, candidate in corruptions(ideal_candidate(case)).items()
    ]
    rows = await asyncio.gather(*jobs)

    summary = {}
    for kind in ["clean", "wrong_basis", "wrong_role", "wrong_equity"]:
        subset = [r for r in rows if r["kind"] == kind]
        flagged = sum(r["flagged"] for r in subset)
        summary[kind] = {"cases": len(subset), "flagged": flagged}
        print(kind, summary[kind])

    RESULTS_PATH.parent.mkdir(exist_ok=True)
    RESULTS_PATH.write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
