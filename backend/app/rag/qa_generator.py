import asyncio
import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.db.database import SessionLocal
from app.db.models import SalaryPost

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def generate_question_for_post(post: dict) -> str | None:
    """
    Given a salary post, generate a natural Hebrew question
    that this post would answer.
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are helping build a salary search evaluation dataset.
Given a salary post from an Israeli tech community, generate ONE natural Hebrew question
that someone would ask, where this post would be a relevant answer.

Rules:
- Question must be in Hebrew
- Must sound like a real person asking
- Should NOT copy exact words from the post
- Should be about salary for this role/experience level
- Return ONLY the question, nothing else"""
            },
            {
                "role": "user",
                "content": f"""Post:
Role: {post['role']}
Experience: {post['years_experience']} years
Salary: {post['salary']}
Location: {post['location']}
Text: {post['raw_text']}"""
            }
        ],
        temperature=0.7,
        max_tokens=100,
    )

    question = response.choices[0].message.content.strip()

    if not question or len(question) < 10:
        return None

    return question


async def generate_test_cases(limit: int = 50) -> list[dict]:
    """
    Generate synthetic test cases from existing posts in the DB.
    Each post becomes one test case with a generated question.
    """
    db = SessionLocal()
    try:
        posts = db.query(SalaryPost).filter(
            SalaryPost.role.isnot(None),
            SalaryPost.salary.isnot(None),
            SalaryPost.years_experience.isnot(None),
        ).limit(limit).all()

        logger.info(f"Generating questions for {len(posts)} posts...")

        test_cases = []
        for i, post in enumerate(posts, 1):
            post_dict = {
                "id": post.id,
                "role": post.role,
                "years_experience": post.years_experience,
                "salary": post.salary,
                "location": post.location,
                "raw_text": post.raw_text,
            }

            question = await generate_question_for_post(post_dict)

            if question:
                test_cases.append({
                    "query": question,
                    "relevant_ids": [post.id],
                    "source_post": post_dict,
                })
                logger.info(f"[{i}/{len(posts)}] {post.role} → {question[:50]}...")
            else:
                logger.warning(f"[{i}/{len(posts)}] Failed for post {post.id}")

        return test_cases

    finally:
        db.close()


async def main():
    test_cases = await generate_test_cases(limit=50)

    output_path = "app/generated_test_cases.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Generated {len(test_cases)} test cases")
    print(f"✓ Saved to {output_path}")
    print("\nSample:")
    for tc in test_cases[:3]:
        print(f"  Q: {tc['query']}")
        print(f"  A: post_id={tc['relevant_ids'][0]} ({tc['source_post']['role']})")
        print()


if __name__ == "__main__":
    asyncio.run(main()) 



