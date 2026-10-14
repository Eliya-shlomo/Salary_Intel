import json
from functools import lru_cache

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI

from app.agents.analyst_tools import salary_stats, search_posts
from app.core.config import settings

DATA_MARKER = "TOOL_DATA:"

STATS_PROMPT = """You answer questions about salary statistics for Israeli tech roles.
Always call salary_stats. Never state a number that did not come from a tool result.
When the result has no percentiles, report the note as it is.
Answer in one or two short sentences."""

RETRIEVER_PROMPT = """You find example salary posts for a question.
Always call search_posts. Never state a number that did not come from a tool result.
List the examples briefly: role, years of experience, monthly salary in NIS.
If nothing relevant is found, say so."""


def _make_model() -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.openai_api_key,
        temperature=0,
    )


@lru_cache
def get_stats_agent():
    return create_agent(
        model=_make_model(),
        tools=[salary_stats],
        system_prompt=STATS_PROMPT,
    )


@lru_cache
def get_retriever_agent():
    return create_agent(
        model=_make_model(),
        tools=[search_posts],
        system_prompt=RETRIEVER_PROMPT,
    )


def build_report(messages: list) -> str:
    tool_outputs = [
        m.content if isinstance(m.content, str) else json.dumps(m.content)
        for m in messages
        if isinstance(m, ToolMessage)
    ]
    answer = messages[-1].text
    return f"{answer}\n\n{DATA_MARKER}\n{json.dumps(tool_outputs, ensure_ascii=False)}"


async def _run_subagent(agent, question: str) -> str:
    result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
    return build_report(result["messages"])


@tool
async def ask_stats(question: str) -> str:
    """Ask the statistics specialist about salary percentiles (p25, p50, p75) for a role.
    Pass a full self-contained question, for example "salary of a senior devops engineer".
    Returns its answer, then a TOOL_DATA block with the raw numbers it used."""
    return await _run_subagent(get_stats_agent(), question)


@tool
async def ask_retriever(question: str) -> str:
    """Ask the retrieval specialist to find example salary posts for a question.
    Use it for examples and context, not for statistics.
    Returns its answer, then a TOOL_DATA block with the raw posts it found."""
    return await _run_subagent(get_retriever_agent(), question)
