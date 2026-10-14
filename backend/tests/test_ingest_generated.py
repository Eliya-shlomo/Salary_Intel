import asyncio
import json

from app.ingestion.ingest_generated import ingest_dataset
from app.ingestion.orchestrator import IngestOutcome


class FakeSession:
    def __init__(self, log):
        self.log = log

    def commit(self):
        self.log.append("commit")

    def rollback(self):
        self.log.append("rollback")

    def close(self):
        pass


def write_posts(tmp_path, ids):
    lines = [
        json.dumps({"id": i, "raw_text": f"post {i}", "source": "synthetic_v2"})
        for i in ids
    ]
    (tmp_path / "posts.jsonl").write_text("\n".join(lines))


def run(tmp_path, ingest, log):
    return asyncio.run(
        ingest_dataset(tmp_path, ingest=ingest, session_factory=lambda: FakeSession(log))
    )


def test_records_each_outcome_with_its_generated_id(tmp_path):
    write_posts(tmp_path, ["a", "b", "c"])
    outcomes = {
        "post a": IngestOutcome(status="approved", post_id=1),
        "post b": IngestOutcome(status="duplicate", duplicate_of=1),
        "post c": IngestOutcome(status="pending", post_id=2),
    }

    async def ingest(db, raw_text, source):
        assert source == "synthetic_v2"
        return outcomes[raw_text]

    log = []
    counts = run(tmp_path, ingest, log)

    assert counts == {"approved": 1, "duplicate": 1, "pending": 1}
    assert log == ["commit"] * 3
    rows = [json.loads(l) for l in (tmp_path / "ingest_results.jsonl").read_text().splitlines()]
    assert [(r["id"], r["post_id"]) for r in rows] == [("a", 1), ("b", None), ("c", 2)]


def test_errors_are_rolled_back_and_retried_on_the_next_run(tmp_path):
    write_posts(tmp_path, ["a", "b"])
    calls = []

    async def flaky(db, raw_text, source):
        calls.append(raw_text)
        if raw_text == "post b" and calls.count("post b") == 1:
            raise TimeoutError
        return IngestOutcome(status="approved", post_id=len(calls))

    log = []
    assert run(tmp_path, flaky, log) == {"approved": 1, "error": 1}
    assert "rollback" in log

    assert run(tmp_path, flaky, log) == {"approved": 1}
    assert calls == ["post a", "post b", "post b"]
