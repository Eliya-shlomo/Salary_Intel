import asyncio

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agents import analyst_agent
from app.agents.analyst_agent import SYSTEM_PROMPT, run_analyst

REPORT = 'The median is 43,500.\n\nTOOL_DATA:\n["{\\"n\\": 66}"]'


class FakeAnalyst:
    def __init__(self, messages):
        self.messages = messages
        self.received = None

    async def ainvoke(self, payload):
        self.received = payload
        return {"messages": self.messages}


def test_run_analyst_returns_answer_and_raw_reports(monkeypatch):
    fake = FakeAnalyst(
        [
            HumanMessage("q"),
            AIMessage("", tool_calls=[{"name": "ask_stats", "args": {}, "id": "c1"}]),
            ToolMessage(REPORT, tool_call_id="c1"),
            AIMessage("The median is 43,500 NIS."),
        ]
    )
    monkeypatch.setattr(analyst_agent, "get_analyst", lambda: fake)

    run = asyncio.run(run_analyst("salary of devops"))

    assert fake.received["messages"][0]["content"] == "salary of devops"
    assert run.answer == "The median is 43,500 NIS."
    assert run.reports == [REPORT]


def test_run_analyst_without_tool_calls_has_no_reports(monkeypatch):
    fake = FakeAnalyst([HumanMessage("q"), AIMessage("I only answer salary questions.")])
    monkeypatch.setattr(analyst_agent, "get_analyst", lambda: fake)

    run = asyncio.run(run_analyst("hello"))

    assert run.reports == []


def test_system_prompt_forbids_invented_numbers():
    assert "must appear in a specialist report" in SYSTEM_PROMPT
