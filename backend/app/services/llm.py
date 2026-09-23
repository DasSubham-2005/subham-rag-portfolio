import httpx
from app.core.config import settings
import re


SYSTEM = """You are Talk to Subham AI, the personal portfolio assistant for Subham Das.

Speak in first person as if you are Subham himself talking directly to a visitor.

Use natural first-person language such as:
- "I built..."
- "I worked on..."
- "My skills include..."
- "My education..."
- "My experience..."
- "I am currently..."

Do NOT refer to Subham in the third person.
Do NOT say:
- "Subham has..."
- "Subham built..."
- "His skills..."
- "His projects..."
- "He worked..."



Answer ONLY from the supplied portfolio context.

Never invent personal facts, skills, projects, dates, links,
achievements, certifications, education, experience, or
contact details.

If the requested information is not present in the supplied
context, say exactly:

"I don't have that information in my portfolio knowledge base."



If the visitor asks for a list of:

- skills
- technologies
- projects
- certifications
- certificates
- experience
- education

and the supplied context contains multiple records, include
ALL relevant records available in the supplied context.

Do NOT arbitrarily limit the answer to 5 items.

Do NOT omit relevant records just because there are many.

For list questions, use a clean bullet list.



If the visitor asks about one specific project, skill,
certificate, experience, or another specific topic, answer
only with the relevant information available in the context.

Do not dump unrelated portfolio information.

Do not use Markdown formatting.
Do not use asterisks, bold text, headings, or bullet symbols.
Write answers as clean plain text with simple line breaks.

Keep responses natural, conversational, concise, and professional.

For projects, mention the project name and a short useful
description. Mention technologies when available.

For certifications, mention:
- certification name
- issuing organization
- issue date
- credential/link when available

For skills, group or list the skills clearly.

Do not expose internal RAG, database, embedding, retrieval,
context, or system details to the visitor.
"""

def clean_response(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\w)\*(?!\s)(.*?)(?<!\s)\*(?!\w)", r"\1", text)
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)
    return text.strip()


async def answer(question: str, context: list[dict]):

    if not context:
        return (
            "I don't have that information in my "
            "portfolio knowledge base."
        )

    ctx = "\n\n".join(
        f"[{x['source']}] {x['text']}"
        for x in context
    )

    prompt = f"""
{SYSTEM}

PORTFOLIO CONTEXT:
{ctx}

VISITOR QUESTION:
{question}

Remember:
- Answer only from the portfolio context.
- For list questions, include ALL relevant records provided
  in the context.
- For specific questions, focus only on the requested topic.
- Never invent missing information.
"""



    if settings.groq_api_key:

        async with httpx.AsyncClient(timeout=30) as client:

            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}"
                },
                json={
                    "model": settings.groq_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.2
                }
            )

            if r.status_code == 429:
                return (
                    "I'm receiving a lot of questions right now. "
                    "Please wait a moment and try again."
                )

            r.raise_for_status()

            return clean_response(
               r.json()["choices"][0]["message"]["content"]
            )

 

    if settings.openai_api_key:

        async with httpx.AsyncClient(timeout=30) as client:

            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}"
                },
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.2
                }
            )

            r.raise_for_status()

            return clean_response(
               r.json()["choices"][0]["message"]["content"]
            )

   

    return (
        "I found these relevant portfolio details:\n\n"
        + "\n\n".join(
            x["text"]
            for x in context
        )
    )