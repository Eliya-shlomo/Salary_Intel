from functools import lru_cache

from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.agents.subagents import ask_retriever, ask_stats
from app.core.config import settings

SYSTEM_PROMPT = """You answer questions about salaries in Israeli tech.

You have two specialists:
- ask_stats: salary percentiles for a role. Use it for any question about typical or median pay.
- ask_retriever: example posts. Use it for context and examples.

Rules:
- Every number in your answer must appear in a specialist report. Never estimate or compute new numbers.
- If a report says there are too few posts, say that and repeat its note. Do not guess.
- Ask each specialist a full, self-contained question.
- Answer in the language of the user's question, in a few short sentences."""


class AnalystRun(BaseModel):
    answer: str
    reports: list[str]


@lru_cache
def get_analyst():
    model = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.openai_api_key,
        temperature=0,
    )
    return create_agent(
        model=model,
        tools=[ask_stats, ask_retriever],
        system_prompt=SYSTEM_PROMPT,
    )


async def run_analyst(question: str) -> AnalystRun:
    result = await get_analyst().ainvoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    messages = result["messages"]
    return AnalystRun(
        answer=messages[-1].text,
        reports=[m.content for m in messages if isinstance(m, ToolMessage)],
    )
