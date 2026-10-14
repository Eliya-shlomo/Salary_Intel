import asyncio
import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agents import subagents
from app.agents.subagents import DATA_MARKER, ask_retriever, ask_stats, build_report

STATS_JSON = '{"n": 66, "p25": 38000, "p50": 43500, "p75": 50000, "note": null}'


def sample_messages():
    return [
        HumanMessage("salary of devops"),
        AIMessage("", tool_calls=[{"name": "salary_stats", "args": {}, "id": "c1"}]),
        ToolMessage(STATS_JSON, tool_call_id="c1"),
        AIMessage("The median is 43,500 NIS from 66 posts."),
    ]


class FakeAgent:
    def __init__(self, messages):
        self.messages = messages
        self.received = None

    async def ainvoke(self, payload):
        self.received = payload
        return {"messages": self.messages}


def test_build_report_has_final_answer_and_raw_tool_output():
    report = build_report(sample_messages())

    answer, data = report.split(f"\n\n{DATA_MARKER}\n")
    assert answer == "The median is 43,500 NIS from 66 posts."
    assert json.loads(data) == [STATS_JSON]


def test_build_report_without_tool_calls_has_empty_data():
    report = build_report([HumanMessage("hi"), AIMessage("No data.")])

    assert report.endswith(f"{DATA_MARKER}\n[]")


def test_ask_stats_passes_question_and_returns_report(monkeypatch):
    fake = FakeAgent(sample_messages())
    monkeypatch.setattr(subagents, "get_stats_agent", lambda: fake)

    report = asyncio.run(ask_stats.ainvoke({"question": "salary of devops"}))

    assert fake.received["messages"][0]["content"] == "salary of devops"
    assert json.loads(report.split(f"{DATA_MARKER}\n")[1]) == [STATS_JSON]


def test_ask_retriever_uses_retriever_agent(monkeypatch):
    fake = FakeAgent([HumanMessage("q"), AIMessage("Nothing found.")])
    monkeypatch.setattr(subagents, "get_retriever_agent", lambda: fake)

    report = asyncio.run(ask_retriever.ainvoke({"question": "qa salaries"}))

    assert report.startswith("Nothing found.")


def test_subagent_tools_describe_what_they_are_for():
    assert "percentiles" in ask_stats.description
    assert "not for statistics" in ask_retriever.description
